import os

import pandas as pd
import streamlit as st
import folium
from streamlit_folium import st_folium

from src.utils.i18n import get_text, translate_value, translate_column

lang = st.session_state.get("lang")

st.title(get_text('home_title', lang))


@st.cache_data
def load_data():
    if os.path.exists("./data/metadata_estacoes.parquet"):
        try:
            df = pd.read_parquet("./data/metadata_estacoes.parquet")

            for col in ['Latitude', 'Longitude']:
                if col in df.columns:
                    if df[col].dtype == 'object':
                        df[col] = df[col].astype(str).str.replace(
                            ',', '.', regex=False)
                    df[col] = pd.to_numeric(df[col], errors='coerce')

            df = df.dropna(subset=['Latitude', 'Longitude'])
            return df
        except Exception as e:
            st.error(get_text('error_reading_metadata', lang, error=str(e)))
            return None
    return None


df = load_data()

if df is not None and not df.empty:
    st.write(get_text('home_viewing', lang, count=len(df)))

    with st.expander(get_text('home_expand', lang)):
        display_df = df.copy()
        for col in ['Situacao', 'Periodicidade da Medicao']:
            if col in display_df.columns:
                display_df[col] = display_df[col].apply(
                    lambda v: translate_value(v, lang))
        st.dataframe(
            display_df,
            column_config={
                c: st.column_config.Column(translate_column(c, lang))
                for c in display_df.columns
            }
        )

    st.subheader(get_text('home_subtitle', lang))

    m = folium.Map(location=[-15, -55], zoom_start=4, tiles="CartoDB positron")

    for idx, row in df.iterrows():
        tooltip_html = f'<div style="font-size: 16px; white-space: nowrap;"><b>{row.get("Nome", get_text("unknown_station", lang))}</b><br>{get_text("code", lang)}: {row.get("Codigo Estacao", "-")}</div>'

        folium.CircleMarker(
            location=[row["Latitude"], row["Longitude"]],
            radius=4,
            color="#1f77b4",
            fill=True,
            fill_color="#1f77b4",
            fill_opacity=0.7,
            tooltip=tooltip_html
        ).add_to(m)

    map_data = st_folium(
        m,
        height=650,
        use_container_width=True,
        returned_objects=["last_object_clicked"]
    )

    if map_data and map_data.get("last_object_clicked"):
        lat = map_data["last_object_clicked"].get("lat")
        lon = map_data["last_object_clicked"].get("lng")

        if lat is not None and lon is not None:
            tol = 1e-4
            mask = (df["Latitude"].between(lat - tol, lat + tol)
                    ) & (df["Longitude"].between(lon - tol, lon + tol))
            if mask.any():
                matched = df[mask].iloc[0]
                code = matched.get("Codigo Estacao")
                if code:
                    st.session_state['selected_station_code'] = code
                    st.switch_page("pages/explorer_page.py")

else:
    st.info(get_text('home_no_data', lang))

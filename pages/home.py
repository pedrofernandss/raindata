import os

import streamlit as st
import pandas as pd
import plotly.express as px

st.title("🗺️ Mapa das Estações Pluviométricas")


@st.cache_data
def load_data():
    if os.path.exists("metadata_estacoes.parquet"):
        try:
            df = pd.read_parquet("metadata_estacoes.parquet")
            
            for col in ['Latitude', 'Longitude']:
                if col in df.columns:
                    if df[col].dtype == 'object':
                        df[col] = df[col].astype(str).str.replace(
                            ',', '.', regex=False)
                    df[col] = pd.to_numeric(df[col], errors='coerce')

            df = df.dropna(subset=['Latitude', 'Longitude'])
            return df
        except Exception as e:
            st.error(f"Erro ao ler metadados: {e}")
            return None
    return None


df = load_data()

if df is not None and not df.empty:
    st.write(f"Visualizando **{len(df)}** estações com coordenadas válidas.")

    with st.expander("Ver dados brutos das estações"):
        st.dataframe(df)

    st.subheader("Clique em um ponto para ver detalhes")

    fig = px.scatter_mapbox(
        df,
        lat="Latitude",
        lon="Longitude",
        hover_name="Nome",
        hover_data=["Codigo Estacao", "Situacao"],
        height=600,
        color_discrete_sequence=["#1f77b4"] 
    )
    fig.update_layout(
        mapbox_style="open-street-map",
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
        clickmode='event+select',
        mapbox=dict(
            center=dict(lat=-15, lon=-55), 
            zoom=3
        )
    )

    event = st.plotly_chart(
        fig,
        on_select="rerun",
        selection_mode="points",
        use_container_width=True,
        config={'scrollZoom': True, 'displayModeBar': True}
    )

    if event and event['selection']['points']:
        point_index = event['selection']['points'][0]['point_index']
        selected_row = df.iloc[point_index]
        code = selected_row.get('Codigo Estacao')

        if code:
            st.session_state['selected_station_code'] = code
            st.switch_page("pages/raindata.py")

else:
    st.info("Nenhuma estação com coordenadas encontrada. Verifique se o arquivo `metadata_estacoes.parquet` existe e foi processado corretamente.")

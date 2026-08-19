import glob
import io

import pandas as pd
import streamlit as st

from src.utils.i18n import get_text, translate_value, translate_column
from src.functions.data import download_zip_dataset, load_metadata, load_station_data
from src.functions.charts import plot_time_series


lang = st.session_state.get("lang")


st.title(get_text('dataset_explorer', lang))

df_meta = load_metadata()

if df_meta is None:
    st.warning(get_text('rain_no_metadata', lang))
else:
    st.sidebar.header(get_text('filters', lang))

    if 'Situacao' in df_meta.columns:
        st.sidebar.markdown(f"**{get_text('operational_status', lang)}**")
        situacoes = sorted(df_meta['Situacao'].dropna().unique())
        selected_situacao = []
        for situacao in situacoes:
            if st.sidebar.checkbox(
                translate_value(situacao, lang),
                value=True,
                key=f"situacao_filter_{situacao}"
            ):
                selected_situacao.append(situacao)

        if selected_situacao:
            df_filtered = df_meta[df_meta['Situacao'].isin(selected_situacao)]
        else:
            df_filtered = df_meta[df_meta['Situacao'].isin([])]
    else:
        df_filtered = df_meta

    if 'Codigo Estacao' in df_filtered.columns:
        df_filtered = df_filtered.sort_values(by='Codigo Estacao')

    st.sidebar.markdown(get_text('stations_available',
                        lang, count=len(df_filtered)))

    if not df_filtered.empty:
        col_codigo = 'Codigo Estacao' if 'Codigo Estacao' in df_filtered.columns else 'id_arquivo'
        col_nome = 'Nome' if 'Nome' in df_filtered.columns else 'id_arquivo'

        df_filtered['display_label'] = df_filtered[col_codigo].astype(
            str) + " - " + df_filtered[col_nome].astype(str)

        default_index = 0
        options = df_filtered['display_label'].unique()

        if 'selected_station_code' in st.session_state:
            pre_selected_code = st.session_state['selected_station_code']
            match = df_filtered[df_filtered[col_codigo] == pre_selected_code]

            if not match.empty:
                label_to_select = match.iloc[0]['display_label']
                if label_to_select in options:
                    default_index = list(options).index(label_to_select)
            del st.session_state['selected_station_code']

        station_option = st.selectbox(
            get_text('select_station', lang),
            options=options,
            index=default_index
        )

        if st.button(get_text('go_to_hydrologic_page', lang)):
            selected_meta = df_filtered[df_filtered['display_label']
                                        == station_option].iloc[0]
            code_to_pass = selected_meta[col_codigo]
            st.session_state['selected_station_code'] = code_to_pass

            st.switch_page("pages/data_analysis_page.py")

        station_meta = df_filtered[df_filtered['display_label']
                                   == station_option].iloc[0]
        station_id = station_meta['id_arquivo']

        st.divider()
        st.subheader(get_text('station_details', lang,
                     name=station_meta.get('Nome', station_id)))

        c1, c2, c3, c4 = st.columns(4)
        c1.metric(get_text('code', lang), station_meta.get(
            'Codigo Estacao', station_id))
        c2.metric(get_text('latitude', lang),
                  station_meta.get('Latitude', '-'))
        c3.metric(get_text('longitude', lang),
                  station_meta.get('Longitude', '-'))
        c4.metric(get_text('status', lang), translate_value(
            station_meta.get('Situacao', '-'), lang))

        patterns = [
            f"rain_datasets/dados_{station_id}_*.parquet",
            f"data/dados_{station_id}_*.parquet"
        ]

        parquet_file = None
        for p in patterns:
            files = glob.glob(p)
            if files:
                parquet_file = files[0]
                break

        if parquet_file:
            try:
                df_data = load_station_data(parquet_file)
                st.caption(
                    get_text('data_loaded', lang, count=len(df_data))
                )

                date_cols = [
                    c for c in df_data.columns if 'Data' in c or 'DATA' in c]
                date_col = date_cols[0] if date_cols else None

                if date_col:
                    df_data[date_col] = pd.to_datetime(
                        df_data[date_col], errors='coerce')
                    df_data = df_data.sort_values(by=date_col)

                    st.sidebar.divider()
                    st.sidebar.markdown(
                        f"### {get_text('period_filter', lang)}")

                    min_date = df_data[date_col].min().date()
                    max_date = df_data[date_col].max().date()

                    date_format = (
                        "DD/MM/YYYY"
                        if lang == "pt"
                        else "YYYY-MM-DD"
                    )
                    
                    periodo = st.sidebar.date_input(
                        get_text('select_interval', lang),
                        value=(min_date, max_date),
                        min_value=min_date,
                        max_value=max_date,
                        format=date_format
                    )

                    if isinstance(periodo, tuple) and len(periodo) == 2:
                        start_date, end_date = periodo
                        mask = (df_data[date_col].dt.date >= start_date) & (
                            df_data[date_col].dt.date <= end_date)
                        df_data = df_data.loc[mask]

                with st.expander(get_text('view_data_table', lang)):
                    st.dataframe(
                        df_data,
                        width='stretch',
                        column_config={
                            c: st.column_config.Column(translate_column(c, lang))
                            for c in df_data.columns
                        }
                    )

                if date_col:
                    numeric_cols = df_data.select_dtypes(
                        include=['number']).columns.tolist()
                    if numeric_cols:
                        col_plot = st.selectbox(
                            get_text('select_column_chart', lang),
                            numeric_cols,
                            format_func=lambda c: translate_column(c, lang)
                        )

                        st.markdown(get_text('time_series', lang,
                                    col=translate_column(col_plot, lang)))
                        fig = plot_time_series(
                            output_folder=None,
                            name=station_id,
                            df=df_data,
                            date_col=date_col,
                            value_col=col_plot,
                            value_label=translate_column(col_plot, lang),
                            lang=lang
                        )
                        st.pyplot(fig)

                        buf = io.BytesIO()
                        fig.savefig(buf, format="png", dpi=300,
                                    bbox_inches='tight')
                        buf.seek(0)
                        st.download_button(
                            label=get_text('download_chart', lang),
                            data=buf,
                            file_name=f"timeseries_{station_id}.png",
                            mime="image/png",
                            width='stretch'
                        )

                button_col1, button_col2 = st.columns(2)

                with button_col1:
                    csv_data = df_data.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        get_text('download_csv', lang),
                        data=csv_data,
                        file_name=f"{station_id}_dados.csv",
                        mime="text/csv",
                        width='stretch'
                    )

                with button_col2:
                    st.download_button(
                        get_text('download_all_csv', lang),
                        data=download_zip_dataset(),
                        file_name="brazilian_raindata.zip",
                        mime="application/zip",
                        width='stretch'
                    )

            except Exception as e:
                st.error(get_text('error_loading', lang, error=str(e)))
        else:
            st.error(
                get_text('data_file_not_found', lang, id=station_id))

    else:
        st.info(get_text('no_stations', lang))

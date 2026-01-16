import streamlit as st
import pandas as pd
import os
import glob
import plotly.express as px

@st.cache_data
def load_metadata():
    if os.path.exists("metadata_estacoes.parquet"):
        try:
            return pd.read_parquet("metadata_estacoes.parquet")
        except Exception:
            return None
    return None

@st.cache_data
def load_station_data(file_path):
    return pd.read_parquet(file_path)


st.title("🌧️ Explorador de Dados Pluviométricos")

df_meta = load_metadata()

if df_meta is None:
    st.warning("Arquivo de metadados não encontrado.")
else:
    st.sidebar.header("Filtros")

    if 'Situacao' in df_meta.columns:
        st.sidebar.markdown("**Situação Operacional**")
        situacoes = sorted(df_meta['Situacao'].dropna().unique())
        selected_situacao = []
        for situacao in situacoes:
            if st.sidebar.checkbox(situacao, value=True):
                selected_situacao.append(situacao)

        if selected_situacao:
            df_filtered = df_meta[df_meta['Situacao'].isin(selected_situacao)]
        else:
            df_filtered = df_meta[df_meta['Situacao'].isin([])]
    else:
        df_filtered = df_meta

    if 'Codigo Estacao' in df_filtered.columns:
        df_filtered = df_filtered.sort_values(by='Codigo Estacao')

    st.sidebar.markdown(f"**Estações disponíveis:** {len(df_filtered)}")

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
            "Selecione uma Estação:",
            options=options,
            index=default_index
        )

        station_meta = df_filtered[df_filtered['display_label']
                                   == station_option].iloc[0]
        station_id = station_meta['id_arquivo']

        st.divider()
        st.subheader(f"📍 {station_meta.get('Nome', station_id)}")

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Código", station_meta.get('Codigo Estacao', station_id))
        c2.metric("Latitude", station_meta.get('Latitude', '-'))
        c3.metric("Longitude", station_meta.get('Longitude', '-'))
        c4.metric("Situação", station_meta.get('Situacao', '-'))

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
                st.success(
                    f"Dados carregados com sucesso: {len(df_data)} registros.")

                date_cols = [
                    c for c in df_data.columns if 'Data' in c or 'DATA' in c]
                date_col = date_cols[0] if date_cols else None

                if date_col:
                    df_data[date_col] = pd.to_datetime(
                        df_data[date_col], errors='coerce')
                    df_data = df_data.sort_values(by=date_col)

                    st.sidebar.divider()
                    st.sidebar.markdown("### 📅 Filtro de Período")

                    min_date = df_data[date_col].min().date()
                    max_date = df_data[date_col].max().date()

                    periodo = st.sidebar.date_input(
                        "Selecione o Intervalo",
                        value=(min_date, max_date),
                        min_value=min_date,
                        max_value=max_date,
                        format="DD/MM/YYYY"
                    )

                    if isinstance(periodo, tuple) and len(periodo) == 2:
                        start_date, end_date = periodo
                        mask = (df_data[date_col].dt.date >= start_date) & (
                            df_data[date_col].dt.date <= end_date)
                        df_data = df_data.loc[mask]

                with st.expander("Ver Tabela de Dados"):
                    st.dataframe(df_data, use_container_width=True)

                if date_col:
                    numeric_cols = df_data.select_dtypes(
                        include=['number']).columns.tolist()
                    if numeric_cols:
                        col_plot = st.selectbox(
                            "Selecione a coluna para o gráfico:", numeric_cols)

                        fig = px.line(df_data, x=date_col, y=col_plot,
                                      title=f"Série Temporal - {col_plot}",
                                      color_discrete_sequence=["#1f77b4"])

                        st.plotly_chart(fig, use_container_width=True)

                csv_data = df_data.to_csv(index=False).encode('utf-8')
                st.download_button(
                    "📥 Baixar dados (CSV)",
                    data=csv_data,
                    file_name=f"{station_id}_dados.csv",
                    mime="text/csv"
                )

            except Exception as e:
                st.error(f"Erro ao abrir arquivo de dados: {e}")
        else:
            st.error(
                f"Arquivo de dados para a estação {station_id} não encontrado.")

    else:
        st.info("Nenhuma estação encontrada com os filtros atuais.")

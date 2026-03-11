import glob
import io
import numpy as np
import scipy as sc
import streamlit as st

from src.utils.i18n import get_text
from src.functions.data import clean_dataset, get_dry_season, get_hydrological_year_init, get_monthly_mean_precipitation, load_metadata, load_station_data
from src.functions.hydrology import compute_max_daily_preciptation, compute_gev, compute_hmax_gev, desag_max_daily_preciptation_intesity, compute_spi
from src.functions.statistic import compute_cdf, verify_probability_distribuition
from src.functions.charts import plot_monthly_average_precipitation, plot_pdf_daily_max_precipitation, plot_cdf_daily_max_precipitation, plot_idf_curves, plot_spi

lang = st.session_state.get("lang")


st.title(get_text('data_analysis', lang))

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

        station_meta = df_filtered[df_filtered['display_label']
                                   == station_option].iloc[0]
        station_id = station_meta['id_arquivo']

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
                raw_data = load_station_data(parquet_file)
                metadata, dataset, spi_dataset = clean_dataset(raw_data)

                if not dataset.empty:
                    st.subheader(get_text('station_details', lang,
                                          name=station_meta.get('Nome', station_id)))

                    # --- Monthly data (used in tab 1) ---
                    monthly_dataset = get_monthly_mean_precipitation(dataset)
                    dry_season_df = get_dry_season(monthly_dataset)
                    _, mes_inicio_ano_hidro = get_hydrological_year_init(
                        dry_season_df)

                    # --- Hydrological year marking (needed for max daily precip) ---
                    method, hydro_init = get_hydrological_year_init(
                        dry_season_df)
                    if method != "Ano hidrológico":
                        anos = dataset['ano civil'].unique().tolist()
                        for i, ano in enumerate(anos):
                            mask = dataset['ano civil'] == ano
                            dataset.loc[mask, 'ano hidrologico'] = int(i + 1)
                    else:
                        dataset['ano hidrologico'] = np.where(
                            dataset['mes'] >= hydro_init,
                            dataset['ano civil'] + 1,
                            dataset['ano civil']
                        )

                    # --- Max daily precipitation pipeline ---
                    hmax1d = compute_max_daily_preciptation(dataset)
                    c, loc, scale, gev_samples = compute_gev(hmax1d)
                    df_hmax = compute_hmax_gev(c, loc, scale)
                    rainfall_matrix = desag_max_daily_preciptation_intesity(
                        df_hmax)

                    # --- KS test for best distribution ---
                    dist_df, params, nome_dist = verify_probability_distribuition(
                        hmax1d)

                    # --- CDF data ---
                    x_dados, y_dados = compute_cdf(
                        hmax1d['precipitacao máxima anual (mm)'].values)
                    dist_obj = getattr(sc.stats, nome_dist)
                    x_numerico = np.linspace(
                        hmax1d['precipitacao máxima anual (mm)'].min(),
                        hmax1d['precipitacao máxima anual (mm)'].max(),
                        1000
                    )
                    y_numerico = dist_obj.cdf(x_numerico, *params)

                    # --- PDF data ---
                    dados_simulados = dist_obj.rvs(
                        *params, size=1000, random_state=42)
                    import pandas as pd
                    pdf_data = pd.DataFrame({
                        'real': hmax1d['precipitacao máxima anual (mm)'].values.tolist() + [None] * (1000 - len(hmax1d)),
                        'numerica': dados_simulados
                    })
                    # KDE plots need equal-length series; use separate series approach via dict
                    pdf_data_real = hmax1d['precipitacao máxima anual (mm)'].values
                    pdf_data_numerica = dados_simulados
                    pdf_df = pd.DataFrame({
                        'real': np.concatenate([pdf_data_real, np.full(1000 - len(pdf_data_real), np.nan)]),
                        'numerica': pdf_data_numerica
                    })

                    cdf_data = {
                        'real': {'x': x_dados, 'y': y_dados},
                        'numerica': {'x': list(x_numerico), 'y': list(y_numerico)}
                    }

                    # --- SPI data ---
                    spi_dataset = compute_spi(spi_dataset)

                    # --- Tabs ---
                    tab_monthly, tab_pdf, tab_cdf, tab_idf, tab_spi = st.tabs([
                        get_text('monthly_average_precipitation', lang),
                        get_text('tab_pdf', lang),
                        get_text('tab_cdf', lang),
                        get_text('tab_idf', lang),
                        get_text('tab_spi', lang),
                    ])

                    with tab_monthly:
                        chart_column, data_column = st.columns([1, 1])

                        with chart_column:
                            st.markdown(
                                get_text('monthly_average_precipitation', lang))
                            fig = plot_monthly_average_precipitation(
                                output_folder=None,
                                name=station_id,
                                monthly=monthly_dataset,
                                rainy_season_start=mes_inicio_ano_hidro,
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
                                file_name=f"media_mensal_{station_id}.png",
                                mime="image/png",
                                use_container_width=True
                            )

                        with data_column:
                            st.markdown(get_text('dry_season_table', lang))
                            display_dry = dry_season_df.copy()
                            display_dry['precipitacao media mensal (mm)'] = display_dry['precipitacao media mensal (mm)'].apply(
                                lambda x: f"{x:.1f}")
                            st.dataframe(
                                display_dry[[
                                    'mes', 'precipitacao media mensal (mm)']],
                                hide_index=True, use_container_width=True, height=220
                            )
                            st.divider()
                            st.markdown(get_text('monthly_mean_table', lang))
                            display_monthly = monthly_dataset[[
                                'mes', 'precipitacao media mensal (mm)']].copy()
                            display_monthly['precipitacao media mensal (mm)'] = display_monthly['precipitacao media mensal (mm)'].apply(
                                lambda x: f"{x:.1f}")
                            st.dataframe(
                                display_monthly,
                                hide_index=True, use_container_width=True, height=220
                            )

                    with tab_pdf:
                        chart_col, data_col = st.columns([1, 1])
                        with chart_col:
                            fig_pdf = plot_pdf_daily_max_precipitation(
                                output_folder=None, name=station_id,
                                data=pdf_df, lang=lang
                            )
                            st.pyplot(fig_pdf)
                            buf_pdf = io.BytesIO()
                            fig_pdf.savefig(buf_pdf, format="png",
                                            dpi=300, bbox_inches='tight')
                            buf_pdf.seek(0)
                            st.download_button(
                                label=get_text('download_chart', lang),
                                data=buf_pdf,
                                file_name=f"pdf_{station_id}.png",
                                mime="image/png",
                                use_container_width=True
                            )
                        with data_col:
                            st.markdown(get_text('ks_test_table', lang))
                            st.dataframe(
                                dist_df[['Tipo de Distribuição',
                                         'p-valor', 'Teste KS']],
                                hide_index=True, use_container_width=True
                            )
                            st.markdown(
                                f"**{get_text('best_distribution', lang)}:** {dist_df.iloc[0]['Tipo de Distribuição']}")

                    with tab_cdf:
                        chart_col, data_col = st.columns([1, 1])
                        with chart_col:
                            fig_cdf = plot_cdf_daily_max_precipitation(
                                output_folder=None, name=station_id,
                                data=cdf_data, lang=lang
                            )
                            st.pyplot(fig_cdf)
                            buf_cdf = io.BytesIO()
                            fig_cdf.savefig(buf_cdf, format="png",
                                            dpi=300, bbox_inches='tight')
                            buf_cdf.seek(0)
                            st.download_button(
                                label=get_text('download_chart', lang),
                                data=buf_cdf,
                                file_name=f"cdf_{station_id}.png",
                                mime="image/png",
                                use_container_width=True
                            )
                        with data_col:
                            st.markdown(get_text('hmax_table', lang))
                            display_hmax = df_hmax.copy()
                            display_hmax['h_max,1 (mm)'] = display_hmax['h_max,1 (mm)'].apply(
                                lambda x: f"{x:.1f}")
                            st.dataframe(
                                display_hmax[['t_r (anos)', 'h_max,1 (mm)']],
                                hide_index=True, use_container_width=True
                            )

                    with tab_idf:
                        fig_idf = plot_idf_curves(
                            output_folder=None, name=station_id,
                            lang=lang, rainfall_matrix=rainfall_matrix
                        )
                        st.pyplot(fig_idf)
                        buf_idf = io.BytesIO()
                        fig_idf.savefig(buf_idf, format="png",
                                        dpi=300, bbox_inches='tight')
                        buf_idf.seek(0)
                        st.download_button(
                            label=get_text('download_chart', lang),
                            data=buf_idf,
                            file_name=f"idf_{station_id}.png",
                            mime="image/png",
                            use_container_width=True
                        )

                    with tab_spi:
                        st.markdown(get_text('spi_chart_title', lang))
                        fig_spi = plot_spi(
                            output_folder=None,
                            name=station_id,
                            dataset=spi_dataset,
                            lang=lang
                        )
                        st.pyplot(fig_spi, use_container_width=True)
                        buf_spi = io.BytesIO()
                        fig_spi.savefig(buf_spi, format="png",
                                        dpi=300, bbox_inches='tight')
                        buf_spi.seek(0)
                        st.download_button(
                            label=get_text('download_chart', lang),
                            data=buf_spi,
                            file_name=f"spi_{station_id}.png",
                            mime="image/png",
                            use_container_width=True
                        )

                else:
                    st.warning(
                        "O arquivo foi encontrado, mas não contém dados válidos após a limpeza.")

            except Exception as e:
                st.error(f"Erro ao processar o arquivo da estação: {e}")
        else:
            st.error(
                f"Arquivo de dados não encontrado para a estação ID: {station_id}")

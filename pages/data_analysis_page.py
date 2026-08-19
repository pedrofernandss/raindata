import glob
import io
import numpy as np
import pandas as pd
import scipy as sc
import streamlit as st

from src.utils.i18n import get_text, translate_value, translate_column
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

                               
                # --- Daily dataset for extreme-value analysis ---
                # Unlike the monthly/SPI dataset, incomplete months are not removed here.
                extreme_dataset = raw_data.copy()
                
                # Normalize column names
                extreme_dataset.columns = extreme_dataset.columns.str.strip()
                
                extreme_dataset.rename(columns={
                    'Data Medicao': 'data medicao',
                    'PRECIPITACAO TOTAL, DIARIO (AUT)(mm)': 'precipitacao total diaria (mm)',
                    'data medicao': 'data medicao',
                    'precipitacao total, diario(mm)': 'precipitacao total diaria (mm)',
                    'precipitacao total, diario (aut)(mm)': 'precipitacao total diaria (mm)'
                }, inplace=True)
                
                # Convert date and precipitation fields
                extreme_dataset['data medicao'] = pd.to_datetime(
                    extreme_dataset['data medicao'],
                    errors='coerce'
                )
                
                extreme_dataset['precipitacao total diaria (mm)'] = pd.to_numeric(
                    extreme_dataset['precipitacao total diaria (mm)'],
                    errors='coerce'
                )
                
                # Remove only invalid dates.
                # Missing precipitation values remain identifiable through the annual
                # coverage calculation performed later.
                extreme_dataset = extreme_dataset.dropna(
                    subset=['data medicao']
                ).copy()
                
                # Calendar variables
                extreme_dataset['ano civil'] = extreme_dataset['data medicao'].dt.year
                extreme_dataset['mes'] = extreme_dataset['data medicao'].dt.month

                                
                if not dataset.empty:
                    st.subheader(get_text('station_details', lang,
                                          name=station_meta.get('Nome', station_id)))

                    # --- Monthly data (used in tab 1) ---
                    monthly_dataset = get_monthly_mean_precipitation(dataset)
                    dry_season_df = get_dry_season(monthly_dataset)
                    
                                      
                    # --- Hydrological-year definition ---
                    method, hydro_init = get_hydrological_year_init(
                        dry_season_df
                    )
                    
                    mes_inicio_ano_hidro = hydro_init
                    
                    if method != "Ano hidrológico":
                    
                        # Civil year
                        dataset['ano hidrologico'] = dataset['ano civil']
                    
                        extreme_dataset['ano hidrologico'] = (
                            extreme_dataset['ano civil']
                        )
                    
                                           
                    else:
                    
                        dataset['ano hidrologico'] = np.where(
                            dataset['mes'] >= hydro_init,
                            dataset['ano civil'] + 1,
                            dataset['ano civil']
                        )
                    
                        extreme_dataset['ano hidrologico'] = np.where(
                            extreme_dataset['mes'] >= hydro_init,
                            extreme_dataset['ano civil'] + 1,
                            extreme_dataset['ano civil']
                        )
                    
                                                               
                    # --- Max daily precipitation pipeline ---
                    # Annual maxima are calculated from the original daily observations,
                    # independently of the strict complete-month filter used for monthly
                    # statistics and SPI.
                    hmax1d = compute_max_daily_preciptation(
                        extreme_dataset,
                        hydro_init=hydro_init,
                        max_missing_days=15
                    )
                    
                    n_years = len(hmax1d)
                    
                    # --- KS test for best distribution ---
                    dist_df, params, nome_dist = verify_probability_distribuition(
                        hmax1d
                    )

                    distribution_names = {
                        'genextreme': get_text('dist_gev', lang),
                        'gumbel_r': get_text('dist_gumbel', lang),
                        'lognorm': get_text('dist_lognorm', lang),
                        'pearson3': get_text('dist_pearson3', lang),
                    }
                    
                   param_names = {
                        'genextreme': [
                            get_text('param_shape_c', lang),
                            get_text('param_location', lang),
                            get_text('param_scale', lang)
                        ],
                        'gumbel_r': [
                            get_text('param_location', lang),
                            get_text('param_scale', lang)
                        ],
                        'lognorm': [
                            get_text('param_shape_s', lang),
                            get_text('param_location', lang),
                            get_text('param_scale', lang)
                        ],
                        'pearson3': [
                            get_text('param_skewness', lang),
                            get_text('param_location', lang),
                            get_text('param_scale', lang)
                        ],
                    }
                    
                    display_dist_name = distribution_names.get(
                        nome_dist,
                        nome_dist
                    )

                    display_dist_df = dist_df.copy()
    
                    display_dist_df['Tipo de Distribuição'] = (
                        display_dist_df['Nome Scipy']
                        .map(distribution_names)
                        .fillna(display_dist_df['Tipo de Distribuição'])
                    )
                        
                    st.write(
                        f"**{get_text('best_distribution', lang)}:** {display_dist_name}"
                    )
                    
                    names = param_names.get(
                        nome_dist,
                        [
                            get_text('param_generic', lang, n=i + 1)
                            for i in range(len(params))
                        ]
                    )
                    
                    formatted_params = []
                    
                    for name, value in zip(names, params):
                    
                        value = float(value)
                    
                        if value != 0 and (abs(value) >= 1e5 or abs(value) < 1e-4):
                            formatted_value = f"{value:.4e}"
                        else:
                            formatted_value = f"{value:.5f}"
                    
                        formatted_params.append(
                            f"**{name}:** {formatted_value}"
                        )
                    
                    st.markdown(" | ".join(formatted_params))
                    
                    if n_years < 5:
                        st.warning(
                            f"⚠️ Critical data limitation: only {n_years} annual maximum "
                            "precipitation values satisfy the annual data-coverage criterion. "
                            "This record length is insufficient for a reliable characterization "
                            "of extreme rainfall frequency. Probability distribution fitting, "
                            "return-period estimates, and IDF curves may be highly unstable and "
                            "strongly influenced by individual observations. Results should be "
                            "considered exploratory only and should not be used for engineering "
                            "design or decision-making without additional data and independent validation."
                        )
                    
                    elif n_years < 10:
                        st.warning(
                            f"⚠️ Limited data availability: only {n_years} annual maximum "
                            "precipitation values satisfy the annual data-coverage criterion. "
                            "The short record introduces substantial uncertainty into probability "
                            "distribution fitting, return-period estimates, and IDF curves, "
                            "particularly for return periods considerably longer than the available "
                            "record. Results should be interpreted with caution and regarded primarily "
                            "as exploratory estimates."
                        )
                    
                    elif n_years < 20:
                        st.info(
                            f"ℹ️ Limited historical record: {n_years} annual maximum precipitation "
                            "values satisfy the annual data-coverage criterion. The available series "
                            "supports exploratory frequency analysis; however, uncertainty increases "
                            "for estimates associated with return periods substantially longer than "
                            "the observed record. Probability distributions, return-period quantiles, "
                            "and IDF curves should therefore be interpreted with caution and, whenever "
                            "possible, compared with longer or independently derived regional records."
                        )

                    else:
                        st.info(
                            f"ℹ️ Historical record: {n_years} annual maximum precipitation values "
                            "satisfy the annual data-coverage criterion. The available record provides "
                            "a comparatively stronger basis for frequency analysis; nevertheless, "
                            "uncertainty remains substantial for return periods much longer than the "
                            "observed series. Long-return-period estimates and derived IDF curves "
                            "should be interpreted as extrapolations and independently validated "
                            "before use in engineering design."
                        )
                    
                    # Best fitted distribution
                    dist_obj = getattr(sc.stats, nome_dist)
                    
                    # Return periods
                    Tr_list = [2, 5, 10, 15, 20, 25, 50, 100]
                    
                    p = 1 - 1 / np.array(Tr_list, dtype=float)
                    
                    # Quantiles calculated with the best fitted distribution
                    x_Tr = dist_obj.ppf(p, *params)

                    if np.any(~np.isfinite(x_Tr)):
                        raise ValueError(
                            "The selected probability distribution produced "
                            "invalid precipitation quantiles."
                        )
    
                    df_hmax = pd.DataFrame({
                        "t_r (anos)": Tr_list,
                        "1/Tr": 1 / np.array(Tr_list, dtype=float),
                        "h_max,1 (mm)": x_Tr
                    })
                    
                    rainfall_matrix = desag_max_daily_preciptation_intesity(
                        df_hmax)

                    # --- CDF data ---
                    x_dados, y_dados = compute_cdf(
                        hmax1d['precipitacao máxima anual (mm)'].values)
                    
                    x_numerico = np.linspace(
                        hmax1d['precipitacao máxima anual (mm)'].min(),
                        hmax1d['precipitacao máxima anual (mm)'].max(),
                        1000
                    )
                    y_numerico = dist_obj.cdf(x_numerico, *params)

                    # --- PDF data ---
                    pdf_observed = (
                        hmax1d['precipitacao máxima anual (mm)']
                        .dropna()
                        .to_numpy(dtype=float)
                    )
                    
                    # Domain used to evaluate the theoretical fitted PDF
                    x_min = pdf_observed.min()
                    x_max = pdf_observed.max()
                    
                    span = x_max - x_min
                    margin = 0.05 * span if span > 0 else 1.0
                    
                    x_pdf = np.linspace(
                        x_min - margin,
                        x_max + margin,
                        1000
                    )
                    
                    # Theoretical PDF of the selected fitted distribution
                    y_pdf = dist_obj.pdf(x_pdf, *params)
                    
                    pdf_data = {
                        'observed': pdf_observed,
                        'fitted': {
                            'x': x_pdf,
                            'y': y_pdf
                        }
                    }

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
                                width='stretch'
                            )

                        with data_column:
                            monthly_col_cfg = {
                                c: st.column_config.Column(translate_column(c, lang))
                                for c in ['mes', 'precipitacao media mensal (mm)']
                            }

                            st.markdown(get_text('dry_season_table', lang))
                            display_dry = dry_season_df.copy()
                            display_dry['precipitacao media mensal (mm)'] = display_dry['precipitacao media mensal (mm)'].apply(
                                lambda x: f"{x:.1f}")
                            st.dataframe(
                                display_dry[[
                                    'mes', 'precipitacao media mensal (mm)']],
                                hide_index=True, width='stretch', height=220,
                                column_config=monthly_col_cfg
                            )
                            st.divider()
                            st.markdown(get_text('monthly_mean_table', lang))
                            display_monthly = monthly_dataset[[
                                'mes', 'precipitacao media mensal (mm)']].copy()
                            display_monthly['precipitacao media mensal (mm)'] = display_monthly['precipitacao media mensal (mm)'].apply(
                                lambda x: f"{x:.1f}")
                            st.dataframe(
                                display_monthly,
                                hide_index=True, width='stretch', height=220,
                                column_config=monthly_col_cfg
                            )

                    with tab_pdf:
                        chart_col, data_col = st.columns([1, 1])
                        with chart_col:
                            fig_pdf = plot_pdf_daily_max_precipitation(
                                output_folder=None, name=station_id,
                                data=pdf_data, lang=lang
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
                                width='stretch'
                            )
                        with data_col:
                            st.markdown(get_text('ks_test_table', lang))
                            ks_cols = [
                                'Tipo de Distribuição',
                                'Estatística KS'
                            ]
                            st.dataframe(
                                display_dist_df[ks_cols],
                                hide_index=True, width='stretch',
                                column_config={
                                    c: st.column_config.Column(translate_column(c, lang))
                                    for c in ks_cols
                                }
                            )
                            st.markdown(
                                f"**{get_text('best_distribution', lang)}:** {display_dist_name}")

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
                                width='stretch'
                            )
                        with data_col:
                            st.markdown(get_text('hmax_table', lang))
                            display_hmax = df_hmax.copy()
                            display_hmax['h_max,1 (mm)'] = display_hmax['h_max,1 (mm)'].apply(
                                lambda x: f"{x:.1f}")
                            hmax_cols = ['t_r (anos)', 'h_max,1 (mm)']
                            st.dataframe(
                                display_hmax[hmax_cols],
                                hide_index=True, width='stretch',
                                column_config={
                                    c: st.column_config.Column(translate_column(c, lang))
                                    for c in hmax_cols
                                }
                            )

                    with tab_idf:
                        st.warning(
                            get_text('idf_scope_warning', lang)
                        )
                        chart_col, data_col = st.columns([1, 1])
                        with chart_col:
                            fig_idf = plot_idf_curves(
                                output_folder=None, name=station_id,
                                lang=lang, rainfall_matrix=rainfall_matrix
                            )
                            st.pyplot(fig_idf)
                            buf_idf = io.BytesIO()
                            fig_idf.savefig(buf_idf, format="png",
                                            dpi=300, bbox_inches='tight')
                            buf_idf.seek(0)

                            idf_csv = rainfall_matrix.to_csv(
                                index=False).encode('utf-8')

                            btn_col1, btn_col2 = st.columns(2)
                            with btn_col1:
                                st.download_button(
                                    label=get_text('download_chart', lang),
                                    data=buf_idf,
                                    file_name=f"idf_{station_id}.png",
                                    mime="image/png",
                                    width='stretch'
                                )
                            with btn_col2:
                                st.download_button(
                                    label=get_text(
                                        'idf_download_dataset', lang),
                                    data=idf_csv,
                                    file_name=f"idf_curves_dataset_{station_id}.csv",
                                    mime="text/csv",
                                    width='stretch'
                                )

                        with data_col:
                            st.markdown(get_text('hmax_table', lang))
                            display_hmax = df_hmax.copy()
                            display_hmax['h_max,1 (mm)'] = display_hmax['h_max,1 (mm)'].apply(
                                lambda x: f"{x:.1f}")
                            hmax_cols = ['t_r (anos)', 'h_max,1 (mm)']
                            st.dataframe(
                                display_hmax[hmax_cols],
                                hide_index=True, width='stretch',
                                column_config={
                                    c: st.column_config.Column(translate_column(c, lang))
                                    for c in hmax_cols
                                }
                            )

                    with tab_spi:

                        spi_counts = (
                            spi_dataset
                            .groupby('mes')['precipitacao mensal (mm)']
                            .count()
                            .reindex(range(1, 13), fill_value=0)
                        )
                    
                        min_n = int(spi_counts.min())
                        max_n = int(spi_counts.max())
                        median_n = int(round(spi_counts.median()))
                    
                        if min_n < 20:
                            st.warning(
                                get_text(
                                    'spi_record_warning_short',
                                    lang,
                                    min_n=min_n,
                                    max_n=max_n,
                                    median_n=median_n
                                )
                            )
                    
                        elif min_n < 30:
                            st.info(
                                get_text(
                                    'spi_record_warning_moderate',
                                    lang,
                                    min_n=min_n,
                                    max_n=max_n,
                                    median_n=median_n
                                )
                            )
                    
                        st.markdown(get_text('spi_chart_title', lang))
                        fig_spi = plot_spi(
                            output_folder=None,
                            name=station_id,
                            dataset=spi_dataset,
                            lang=lang
                        )
                        st.pyplot(fig_spi, width='stretch')
                        buf_spi = io.BytesIO()
                        fig_spi.savefig(buf_spi, format="png",
                                        dpi=300, bbox_inches='tight')
                        buf_spi.seek(0)

                        spi_export = spi_dataset.copy()
                        preferred_cols = ['ano civil', 'mes',
                                          'precipitacao mensal (mm)', 'SPI_1']
                        available_cols = [
                            c for c in preferred_cols if c in spi_export.columns]
                        if available_cols:
                            spi_export = spi_export[available_cols]
                        spi_csv = spi_export.to_csv(
                            index=False).encode('utf-8')

                        btn_col1, btn_col2 = st.columns(2)
                        with btn_col1:
                            st.download_button(
                                label=get_text('download_chart', lang),
                                data=buf_spi,
                                file_name=f"spi_{station_id}.png",
                                mime="image/png",
                                width='stretch'
                            )
                        with btn_col2:
                            st.download_button(
                                label=get_text('spi_download_dataset', lang),
                                data=spi_csv,
                                file_name=f"spi_1_dataset_{station_id}.csv",
                                mime="text/csv",
                                width='stretch'
                            )

                else:
                    st.warning(get_text('clean_no_valid_data', lang))

            except Exception as e:
                st.error(get_text('error_processing_station',
                          lang, error=str(e)))
        else:
            st.error(get_text('data_file_not_found', lang, id=station_id))

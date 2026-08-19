translations = {
    'pt': {
        'app_title': '🌧️ Explorador de Dados Pluviométricos',
        'language': 'Idioma',

        'home_title': '🗺️ Mapa das Estações Pluviométricas',
        'home_subtitle': 'Clique em um ponto para ver detalhes',
        'home_viewing': 'Visualizando **{count}** estações com coordenadas válidas.',
        'home_expand': 'Ver dados brutos das estações',
        'home_no_data': 'Nenhuma estação com coordenadas encontrada. Verifique se o arquivo `metadata_estacoes.parquet` existe e foi processado corretamente.',

        'dataset_explorer': '🌧️ Explorador de Dados Pluviométricos',
        'rain_no_metadata': '⚠️ Arquivo de metadados (`metadata_estacoes.parquet`) não encontrado. Por favor, certifique-se de ter executado o notebook `convert.ipynb`.',
        'filters': 'Filtros',
        'operational_status': 'Situação Operacional',
        'stations_available': '**Estações disponíveis:** {count}',
        'select_station': 'Selecione uma Estação:',
        'station_details': '📍 {name}',
        'code': 'Código',
        'latitude': 'Latitude',
        'longitude': 'Longitude',
        'status': 'Situação',
        'data_loaded': 'Dados carregados com sucesso: {count} registros.',
        'period_filter': '📅 Filtro de Período',
        'select_interval': 'Selecione o Intervalo',
        'view_data_table': 'Ver Tabela de Dados',
        'select_column_chart': 'Selecione a coluna para o gráfico:',
        'time_series': 'Série Temporal - {col}',
        'download_csv': '📥 Baixar dataset atual (.csv)',
        'download_all_csv': '📥 Baixar todos os datasets (.zip)',
        'data_file_not_found': 'Arquivo de dados para a estação {id} não encontrado.',
        'error_loading': 'Erro ao abrir arquivo de dados: {error}',
        'no_stations': 'Nenhuma estação encontrada com os filtros atuais.',
        'go_to_hydrologic_page': 'Ir para análise hidrológica',
        'data_analysis': 'Análise de Dados Hidrológicos',
        'monthly_average_precipitation': 'Precipitação Média Mensal',
        "download_chart": "📥 Baixar Gráfico (.png)",
        "dry_season_table": "Período Mais Seco",
        "monthly_mean_table": "Média Mensal",
        'tab_pdf': 'PDF - Precipitação Máxima Diária Anual',
        'tab_cdf': 'CDF - Precipitação Máxima Diária Anual',
        "tab_idf": "Curvas IDF",
        "tab_spi": "SPI-1",
        "spi_chart_title": "Índice de Precipitação Padronizado (SPI-1)",
        "ks_test_table": "Comparação pelo Critério de Kolmogorov-Smirnov",
        "best_distribution": "Distribuição selecionada",
        'hmax_table': 'Precipitação Máxima Diária por Período de Retorno',
        "computing_data": "Calculando dados hidrológicos...",
        "idf_download_dataset": "📥 Baixar dados IDF (.csv)",
        "spi_download_dataset": "📥 Baixar dados SPI-1 (.csv)",
        "clean_no_valid_data": "O arquivo foi encontrado, mas não contém dados válidos após a limpeza.",
        "error_processing_station": "Erro ao processar o arquivo da estação: {error}",
        "error_reading_metadata": "Erro ao ler metadados: {error}",
        "unknown_station": "Desconhecido",
        'quality_title': 'Qualidade dos dados e limitações de uso',

        'quality_frequency_critical': (
            'Análise de frequência: apenas {n_years} máximos anuais atendem ao '
            'critério de cobertura. A série é muito curta e os ajustes de '
            'distribuição, quantis de período de retorno e curvas IDF apresentam '
            'elevada incerteza. Os resultados devem ser tratados somente como exploratórios.'
        ),
        
        'quality_frequency_short': (
            'Análise de frequência: {n_years} máximos anuais atendem ao critério '
            'de cobertura. O histórico é curto e introduz incerteza substancial, '
            'principalmente para períodos de retorno superiores ao comprimento da série.'
        ),
        
        'quality_frequency_limited': (
            'Análise de frequência: {n_years} máximos anuais atendem ao critério '
            'de cobertura. A série permite análise exploratória, mas a incerteza '
            'aumenta para períodos de retorno muito superiores ao histórico observado.'
        ),
        
        'quality_frequency_ok': (
            'Análise de frequência: {n_years} máximos anuais atendem ao critério '
            'de cobertura. Períodos de retorno muito superiores ao histórico '
            'observado continuam representando extrapolações.'
        ),
        
        'quality_spi': (
            'SPI-1: estão disponíveis entre {min_n} e {max_n} observações mensais '
            'completas por mês do calendário, com mediana de {median_n}.'
        ),
        
        'quality_spi_critical': (
            'Há pelo menos um mês com menos de 20 observações completas; '
            'o SPI-1 deve ser considerado exploratório.'
        ),
        
        'quality_spi_limited': (
            'Há pelo menos um mês com menos de 30 observações completas; '
            'o SPI-1 deve ser interpretado com cautela.'
        ),
        
        'quality_spi_ok': (
            'O histórico mensal apresenta pelo menos 30 observações completas '
            'para cada mês do calendário.'
        ),
        
        'quality_idf': (
            'IDF: as curvas são estimativas exploratórias e de pré-projeto, '
            'obtidas com coeficientes de desagregação DAEE/CETESB. Para projeto '
            'definitivo, recomenda-se validação com relações ou dados locais ou regionais.'
        ),
        "idf_scope_warning": (
            "⚠️ As curvas IDF apresentadas são estimativas de caráter exploratório e "
            "pré-projeto. Os coeficientes de desagregação adotados são derivados do "
            "método DAEE/CETESB e podem não representar adequadamente as relações de "
            "duração da chuva em todas as regiões do Brasil. Para dimensionamento "
            "hidráulico definitivo, recomenda-se utilizar relações IDF ou coeficientes "
            "de desagregação calibrados com dados pluviográficos locais ou regionais."
        ),
        "spi_record_warning_short": (
            "⚠️ Limitação do histórico: o SPI-1 é ajustado separadamente para cada "
            "mês do calendário. Nesta estação, o número de observações mensais completas "
            "disponíveis por mês do calendário varia de {min_n} a {max_n}, com mediana "
            "de {median_n}. Pelo menos um mês possui menos de 20 observações completas. "
            "Os valores de SPI-1 devem ser interpretados com cautela devido à maior "
            "incerteza associada ao curto período de registro."
        ),
        
        "spi_record_warning_moderate": (
            "ℹ️ Histórico limitado para SPI-1: todos os meses do calendário possuem "
            "pelo menos 20 observações completas, mas pelo menos um possui menos de 30. "
            "O número de observações por mês varia de {min_n} a {max_n}, com mediana "
            "de {median_n}. Os resultados devem ser interpretados considerando a "
            "incerteza associada ao comprimento da série."
        ),
    },
    'en': {
        'app_title': '🌧️ Precipitation Data Explorer',
        'language': 'Language',

        'home_title': '🗺️ Rain Gauge Stations Map',
        'home_subtitle': 'Click on a point to view details',
        'home_viewing': 'Viewing **{count}** stations with valid coordinates.',
        'home_expand': 'View raw station data',
        'home_no_data': 'No stations with coordinates found. Please check if the `metadata_estacoes.parquet` file exists and was processed correctly.',
        'dataset_explorer': '🌧️ Precipitation Data Explorer',
        'rain_no_metadata': '⚠️ Metadata file (`metadata_estacoes.parquet`) not found. Please make sure you have run the `convert.ipynb` notebook.',
        'filters': 'Filters',
        'operational_status': 'Operational Status',
        'stations_available': '**Available stations:** {count}',
        'select_station': 'Select a Station:',
        'station_details': '📍 {name}',
        'code': 'Code',
        'latitude': 'Latitude',
        'longitude': 'Longitude',
        'status': 'Status',
        'data_loaded': 'Data loaded successfully: {count} records.',
        'period_filter': '📅 Period Filter',
        'select_interval': 'Select Interval',
        'view_data_table': 'View Data Table',
        'select_column_chart': 'Select column for chart:',
        'time_series': 'Time Series - {col}',
        'download_csv': '📥 Download current dataset (.csv)',
        'download_all_csv': '📥 Download all datasets (.zip)',
        'data_file_not_found': 'Data file for station {id} not found.',
        'error_loading': 'Error opening data file: {error}',
        'no_stations': 'No stations found with current filters.',
        'go_to_hydrologic_page': 'Go to hydrological analysis',
        'data_analysis': 'Hydrological Data Analysis',
        'monthly_average_precipitation': 'Mean Monthly Precipitation',
        "download_chart": "📥 Download Chart (.png)",
        "dry_season_table": "Dry Season",
        "monthly_mean_table": "Monthly Mean",
        'tab_pdf': 'PDF - Annual Maximum Daily Precipitation',
        'tab_cdf': 'CDF - Annual Maximum Daily Precipitation',
        "tab_idf": "IDF Curves",
        "tab_spi": "SPI-1",
        "spi_chart_title": "Standardized Precipitation Index (SPI-1)",
        "ks_test_table": "Kolmogorov-Smirnov Fit Comparison",
        "best_distribution": "Selected distribution",
        'hmax_table': 'Maximum Daily Precipitation by Return Period',
        "computing_data": "Computing hydrological data...",
        "idf_download_dataset": "📥 Download IDF data (.csv)",
        "spi_download_dataset": "📥 Download SPI-1 data (.csv)",
        "clean_no_valid_data": "The file was found, but does not contain valid data after cleaning.",
        "error_processing_station": "Error processing station file: {error}",
        "error_reading_metadata": "Error reading metadata: {error}",
        "unknown_station": "Unknown",
        'nav_home': 'Início',
        'nav_explorer': 'Explorador',
        'nav_analysis': 'Análise Hidrológica',
        
        'dist_gev': 'Generalizada de Valores Extremos (GEV)',
        'dist_gumbel': 'Gumbel',
        'dist_lognorm': 'Lognormal',
        'dist_pearson3': 'Pearson tipo III',
        
        'param_shape_c': 'Forma (c)',
        'param_shape_s': 'Forma (s)',
        'param_location': 'Localização (loc)',
        'param_scale': 'Escala',
        'param_skewness': 'Assimetria',
        'param_generic': 'Parâmetro {n}',

        'nav_home': 'Home',
        'nav_explorer': 'Dataset Explorer',
        'nav_analysis': 'Hydrological Analysis',
        
        'dist_gev': 'Generalized Extreme Value (GEV)',
        'dist_gumbel': 'Gumbel',
        'dist_lognorm': 'Lognormal',
        'dist_pearson3': 'Pearson Type III',
        
        'param_shape_c': 'Shape (c)',
        'param_shape_s': 'Shape (s)',
        'param_location': 'Location (loc)',
        'param_scale': 'Scale',
        'param_skewness': 'Skewness',
        'param_generic': 'Parameter {n}',

        'quality_title': 'Data quality and usage limitations',

        'quality_frequency_critical': (
            'Frequency analysis: only {n_years} annual maxima satisfy the data-coverage '
            'criterion. The record is very short, and distribution fitting, '
            'return-period quantiles, and IDF curves carry high uncertainty. '
            'Results should be treated as exploratory only.'
        ),
        
        'quality_frequency_short': (
            'Frequency analysis: {n_years} annual maxima satisfy the data-coverage '
            'criterion. The historical record is short and introduces substantial '
            'uncertainty, especially for return periods longer than the available record.'
        ),
        
        'quality_frequency_limited': (
            'Frequency analysis: {n_years} annual maxima satisfy the data-coverage '
            'criterion. The record supports exploratory analysis, but uncertainty '
            'increases for return periods much longer than the observed record.'
        ),
        
        'quality_frequency_ok': (
            'Frequency analysis: {n_years} annual maxima satisfy the data-coverage '
            'criterion. Return periods much longer than the observed record remain extrapolations.'
        ),
        
        'quality_spi': (
            'SPI-1: between {min_n} and {max_n} complete monthly observations are '
            'available per calendar month, with a median of {median_n}.'
        ),
        
        'quality_spi_critical': (
            'At least one calendar month has fewer than 20 complete observations; '
            'SPI-1 should be treated as exploratory.'
        ),
        
        'quality_spi_limited': (
            'At least one calendar month has fewer than 30 complete observations; '
            'SPI-1 should be interpreted with caution.'
        ),
        
        'quality_spi_ok': (
            'At least 30 complete observations are available for every calendar month.'
        ),
        
        'quality_idf': (
            'IDF: the curves are exploratory and pre-design estimates based on '
            'DAEE/CETESB rainfall-disaggregation coefficients. For final design, '
            'validation against local or regional relationships or data is recommended.'
        ),
        
        'invalid_quantiles_error': (
            'The selected probability distribution produced '
            'invalid precipitation quantiles.'
        ),
        
        'invalid_quantiles_error': (
            'A distribuição de probabilidade selecionada produziu '
            'quantis de precipitação inválidos.'
        ),        
    }
}


def get_text(key, lang='pt', **kwargs):
    text = translations.get(lang, translations['pt']).get(key, key)
    if kwargs:
        return text.format(**kwargs)
    return text


# Categorical values that appear verbatim inside the data itself (e.g. Situacao).
# Keyed by the RAW string exactly as it appears in the dataframe.
categorical_value_labels = {
    'Desativada': {'pt': 'Desativada', 'en': 'Deactivated'},
    'Fechada':    {'pt': 'Fechada',    'en': 'Closed'},
    'Operante':   {'pt': 'Operante',   'en': 'Operational'},
    'Pane':       {'pt': 'Pane',       'en': 'Malfunction'},
    'Diaria':     {'pt': 'Diária',     'en': 'Daily'},
}

# Column / field names produced by the raw BDMEP parquet and by the
# clean_dataset()/hydrology/statistic pipeline. Keyed by the RAW column name.
column_labels = {
    'Data Medicao': {'pt': 'Data Medicao', 'en': 'Measurement Date'},
    'PRECIPITACAO TOTAL, DIARIO (AUT)(mm)': {'pt': 'PRECIPITACAO TOTAL, DIARIO (AUT)(mm)', 'en': 'Total Precipitation, Daily (mm)'},
    'TEMPERATURA MEDIA, DIARIA (AUT)(°C)': {'pt': 'TEMPERATURA MEDIA, DIARIA (AUT)(°C)', 'en': 'Average Temperature, Daily (°C)'},
    'UMIDADE RELATIVA DO AR, MEDIA DIARIA (AUT)(%)': {'pt': 'UMIDADE RELATIVA DO AR, MEDIA DIARIA (AUT)(%)', 'en': 'Relative Humidity, Daily Average (%)'},
    'VENTO, VELOCIDADE MEDIA DIARIA (AUT)(m/s)': {'pt': 'VENTO, VELOCIDADE MEDIA DIARIA (AUT)(m/s)', 'en': 'Wind Speed, Daily Average (m/s)'},
    'mes': {'pt': 'mes', 'en': 'Month'},
    'precipitacao media mensal (mm)': {'pt': 'precipitacao media mensal (mm)', 'en': 'Average Monthly Precipitation (mm)'},
    'Tipo de Distribuição': {'pt': 'Tipo de Distribuição', 'en': 'Distribution Type'},
    'p-valor': {'pt': 'p-valor', 'en': 'p-value'},
    'Estatística KS': {'pt': 'Estatística KS', 'en': 'KS Statistic'},
    't_r (anos)': {'pt': 't_r (anos)', 'en': 't_r (years)'},
    'id_arquivo': {'pt': 'id_arquivo', 'en': 'File ID'},
    'Nome': {'pt': 'Nome', 'en': 'Name'},
    'Codigo Estacao': {'pt': 'Codigo Estacao', 'en': 'Station Code'},
    'Situacao': {'pt': 'Situacao', 'en': 'Status'},
    'Data Inicial': {'pt': 'Data Inicial', 'en': 'Start Date'},
    'Data Final': {'pt': 'Data Final', 'en': 'End Date'},
    'Periodicidade da Medicao': {'pt': 'Periodicidade da Medicao', 'en': 'Measurement Frequency'},
}


def _lookup(table, value, lang='pt'):
    entry = table.get(value)
    if entry is None:
        return value
    return entry.get(lang, entry.get('pt', value))


def translate_value(value, lang='pt'):
    """Translate a categorical data value (e.g. Situacao) for display only."""
    return _lookup(categorical_value_labels, value, lang)


def translate_column(value, lang='pt'):
    """Translate a raw/derived column or field name for display only."""
    return _lookup(column_labels, value, lang)

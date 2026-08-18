import os
import shutil
from datetime import datetime

import pandas as pd
import streamlit as st


@st.cache_data
def load_metadata():
    if os.path.exists("./data/metadata_estacoes.parquet"):
        try:
            return pd.read_parquet("./data/metadata_estacoes.parquet")
        except Exception:
            return None
    return None


@st.cache_data
def load_station_data(file_path):
    return pd.read_parquet(file_path)


def download_zip_dataset():
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    source_dir = os.path.join(project_root, "data")

    base_name = "brazilian_raindata"
    archive_format = "zip"

    zip_path = shutil.make_archive(base_name, archive_format, source_dir)

    with open(zip_path, "rb") as f:
        zip_data = f.read()

    return zip_data


def is_continuous(months: list) -> tuple[bool, list]:
    """Verify is the the selected six monts are a continuous calendar window. 

    Verifica se os 6 meses representam um bloco contínuo no calendário. Considera circularidade: exemplo (9,10,11,12,1,2)

    :param months: Months list (1 to 12)

    :return: [0] = Boolean seting if the list is continuous, [1] = Month list (empty if they are not continuous)
    """

    months = sorted(months)

    # Testing all the possible combinations since the time is a continuous measure
    for month in months:
        window = [(month + i - 1) % 12 + 1 for i in range(6)]
        if set(window) == set(months):
            return True, window

    return False, []


def get_monthly_mean_precipitation(dataset_metadata: pd.DataFrame) -> pd.DataFrame:
    """
    Function to calculate the mensal mean precipitation

    :param dataset: Dataset from the BDMEP file data (city, lat, long, alt, etc.)
    :type dataset: pd.DataFrame
    """
    monthly_sum = dataset_metadata.groupby(['ano civil', 'mes'])[
        'precipitacao total diaria (mm)'].sum().reset_index()

    monthly = monthly_sum.groupby(
        'mes')['precipitacao total diaria (mm)'].mean().reset_index()
    monthly.rename(columns={
                   'precipitacao total diaria (mm)': 'precipitacao media mensal (mm)'}, inplace=True)

    return monthly


def get_dry_season(monthly_dataset: pd.DataFrame) -> pd.DataFrame:

    return monthly_dataset.sort_values(by='precipitacao media mensal (mm)').head(6)


def get_hydrological_year_init(dataset: pd.DataFrame) -> tuple[str, int]:

    # Verify if the dry season is continuous
    year_tupe, months_window = is_continuous(dataset['mes'].tolist())

    if year_tupe:
        method = "Ano hidrológico"
        hydrological_year_init = months_window[-1] % 12 + 1
    else:
        method = "Ano civil"
        hydrological_year_init = 1

    return method, hydrological_year_init


def clean_dataset(input_data: str | pd.DataFrame) -> tuple[dict, pd.DataFrame, pd.DataFrame]:
    """Read data file from BDMEP and extract cabecalho or process existing DataFrame

    :param input_data: Path file string or pandas DataFrame

    :return: [0] = Metadata from the file (city, lat, long, alt, ..., etc), [1] = Clean BDMEP dataset 
    """
    cabecalho = {}
    df = pd.DataFrame()

    if isinstance(input_data, str):
        path_file = input_data
        with open(path_file, 'r', encoding='utf-8') as f:
            linhas = [next(f).strip() for _ in range(9)]
            for linha in linhas:
                if ':' in linha:
                    chave, valor = linha.split(':', 1)
                    chave_formatada = chave.strip().lower().replace(' ', '_')
                    valor = valor.strip()
                    if chave_formatada in ['latitude', 'longitude', 'altitude']:
                        valor = float(valor)
                    elif chave_formatada in ['data_inicial', 'data_final']:
                        valor = datetime.strptime(valor, '%Y-%m-%d').date()
                    cabecalho[chave_formatada] = valor
        df = pd.read_csv(path_file, sep=";", encoding="utf-8", skiprows=9)

    elif isinstance(input_data, pd.DataFrame):
        df = input_data.copy()

    df.drop(columns=['Unnamed: 5'], inplace=True, errors='ignore')

    # Normalize column names: strip whitespace first
    df.columns = df.columns.str.strip()

    mapa_colunas = {
        # uppercase variants (raw CSV / some parquet exports)
        'Data Medicao': 'data medicao',
        'PRECIPITACAO TOTAL, DIARIO (AUT)(mm)': 'precipitacao total diaria (mm)',
        'TEMPERATURA MEDIA, DIARIA (AUT)(°C)': 'temperatura media diaria (°C)',
        'UMIDADE RELATIVA DO AR, MEDIA DIARIA (AUT)(%)': 'umidade relativa ar media diaria (%)',
        'VENTO, VELOCIDADE MEDIA DIARIA (AUT)(m/s)': 'velocidade vento media diaria (m/s)',
        # lowercase variants (some parquet exports)
        'data medicao': 'data medicao',
        'precipitacao total, diario(mm)': 'precipitacao total diaria (mm)',
        'precipitacao total, diario (aut)(mm)': 'precipitacao total diaria (mm)',
        'temperatura media, diaria (aut)(°c)': 'temperatura media diaria (°C)',
        'umidade relativa do ar, media diaria (aut)(%)': 'umidade relativa ar media diaria (%)',
        'vento, velocidade media diaria (aut)(m/s)': 'velocidade vento media diaria (m/s)',
    }
    df.rename(columns=mapa_colunas, inplace=True)

    df['data medicao'] = pd.to_datetime(df['data medicao'], errors='coerce')
    df['precipitacao total diaria (mm)'] = pd.to_numeric(
        df['precipitacao total diaria (mm)'],
        errors='coerce'
    )
    
    # Negative precipitation values are physically invalid
    # and are therefore treated as missing observations.
    df.loc[
        df['precipitacao total diaria (mm)'] < 0,
        'precipitacao total diaria (mm)'
    ] = float('nan')
    df.drop(columns=['temperatura media diaria (°C)', 'umidade relativa ar media diaria (%)',
            'velocidade vento media diaria (m/s)'], inplace=True, errors='ignore')
    df['ano civil'] = df['data medicao'].dt.year
    df['mes'] = df['data medicao'].dt.month

    # Create a specfic dataset to compute the SPI
    spi_df = df.copy()
    spi_df.dropna(inplace=True)
    spi_df.reset_index(drop=True, inplace=True)
    spi_df = spi_df.groupby(['ano civil', 'mes'])[
        'precipitacao total diaria (mm)'].sum().reset_index()
    spi_df.rename(columns={
                  'precipitacao total diaria (mm)': 'precipitacao mensal (mm)'}, inplace=True)

    # Filter to remove incomplete data that may impair statistical analysis
    final_df = []

    if 'data_inicial' in cabecalho and 'data_final' in cabecalho:
        initial_year = cabecalho['data_inicial'].year
        final_year = cabecalho['data_final'].year
    else:
        initial_year = df['ano civil'].min()
        final_year = df['ano civil'].max()

    # Handle case where date parsing failed or df is empty
    try:
        if pd.isna(initial_year) or pd.isna(final_year):
            return cabecalho, pd.DataFrame(columns=df.columns), spi_df, pd.DataFrame()
    except (TypeError, ValueError):
        return cabecalho, pd.DataFrame(columns=df.columns), spi_df

    years_available = list(range(int(initial_year), int(final_year) + 1))
    for year in years_available:
        df_year = df[df['ano civil'] == year]
        months = df_year['mes'].unique().tolist()
        for mes in months:
            filtered_df = df_year[df_year['mes'] == mes]
            has_nan = filtered_df['precipitacao total diaria (mm)'].isna().any()

            expected_days = pd.Period(
                year=int(year),
                month=int(mes),
                freq='M'
            ).days_in_month
            
            observed_days = filtered_df['data medicao'].dt.normalize().nunique()
            
            is_incomplete = observed_days != expected_days
            
            if has_nan or is_incomplete:
                pass
            else:
                final_df.append(filtered_df)

    if final_df:
        final_df = pd.concat(final_df)
        final_df.reset_index(drop=True, inplace=True)
    else:
        final_df = pd.DataFrame(columns=df.columns)

    # Recreate SPI dataset using only complete months
    spi_df = final_df.groupby(['ano civil', 'mes'])[
        'precipitacao total diaria (mm)'
    ].sum().reset_index()
    
    spi_df.rename(columns={
        'precipitacao total diaria (mm)': 'precipitacao mensal (mm)'
    }, inplace=True)
    
    return cabecalho, final_df, spi_df

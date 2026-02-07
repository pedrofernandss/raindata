import os
import glob
from datetime import datetime

import numpy as np
import scipy as sc
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
    monthly_sum = dataset_metadata.groupby(['ano civil', 'mes'])['precipitacao total diaria (mm)'].sum().reset_index()

    monthly = monthly_sum.groupby('mês')['precipitacao total diaria (mm)'].mean().reset_index()
    monthly.rename(columns={'precipitacao total diaria (mm)': 'precipitacao media mensal (mm)'}, inplace=True)

    return monthly

def get_dry_season(monthly_dataset: pd.DataFrame) -> pd.DataFrame:     

    return monthly_dataset.sort_values(by='precipitacao media mensal (mm)').head(6)

def get_hydrological_year_init(dataset: pd.DataFrame) -> tuple[str, int]:
        
    # Verify if the dry season is continuous
    year_tupe, months_window = is_continuous(dataset['mês'].tolist())
    
    if year_tupe:
        method = "Ano hidrológico"
        hydrological_year_init = months_window[-1] % 12 + 1
    else:
        method = "Ano civil"
        hydrological_year_init = 1

    return method, hydrological_year_init

def clean_dataset(path_file: str) -> tuple[dict, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Read data file from BDMEP and extract cabecalho

    :param dados: Path fileCaminho para o arquivo CSV da da base de dados BDMEP

    :return: [0] = Metadata from the file (city, lat, long, alt, ..., etc), [2] = Clean BDMEP dataset 
    """

    with open(path_file, 'r', encoding='utf-8') as f:
        linhas = [next(f).strip() for _ in range(9)]
        cabecalho = {}
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
    df.drop(columns=['Unnamed: 5'], inplace=True, errors='ignore')
    df.columns = ['data medicao', 'precipitacao total diaria (mm)', 'temperatura media diaria (°C)',
                  'umidade relativa ar media diaria (%)', 'velocidade vento media diaria (m/s)']
    df['data medicao'] = pd.to_datetime(df['data medicao'], errors='coerce')
    df.drop(columns=['temperatura media diaria (°C)', 'umidade relativa ar media diaria (%)',
            'velocidade vento media diaria (m/s)'], inplace=True)
    df['ano civil'] = df['data medicao'].dt.year
    df['mês'] = df['data medicao'].dt.month

    # Filter to remove incomplete data that may impair statistical analysis
    final_df = []
    initial_year = cabecalho['data_inicial'].year
    final_year = cabecalho['data_final'].year
    years_available = list(range(initial_year, final_year + 1))
    for year in years_available:
        df_year = df[df['ano civil'] == year]
        months = df_year['mês'].unique().tolist()
        for mes in months:
            filtered_df = df_year[df_year['mês'] == mes]
            has_nan = filtered_df['precipitacao total diaria (mm)'].isna(
            ).any()
            if has_nan:
                pass
            else:
                final_df.append(filtered_df)

    final_df = pd.concat(final_df)
    final_df.reset_index(drop=True, inplace=True)

    return cabecalho, final_df

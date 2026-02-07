import os
import glob
from datetime import datetime

import numpy as np
import scipy as sc
import pandas as pd
import streamlit as st

def compute_max_daily_preciptation(dataset: pd.DataFrame) -> pd.DataFrame:
    """Function to compute the max daily preciptation in civil or hydrological year máxima diária em função do ano hidrológico ou civil.

    :param dataset: Clean BDMEP dataset

    :return: pd.DataFrame with the biggest daily precipitaion by hydrological or civil year
    """

    # Format column type
    dataset['precipitacao total diaria (mm)'] = pd.to_numeric(dataset['precipitacao total diaria (mm)'], errors='coerce')

    # Extract mean and standard deviation from the top anual values
    top_precipitation_by_year = dataset.groupby('ano hidrologico')['precipitacao total diaria (mm)'].max().reset_index()
    top_precipitation_by_year.rename(columns={'precipitacao total diaria (mm)': 'precipitacao máxima anual (mm)'}, inplace=True)

    # Remove zero's (0)
    top_precipitation_by_year = top_precipitation_by_year[
        top_precipitation_by_year['precipitacao máxima anual (mm)'] > 0]
    top_precipitation_by_year.reset_index(drop=True, inplace=True)

    return top_precipitation_by_year

def compute_gev(dataset: pd.DataFrame) -> tuple[float, float, float, list]:
    """Check the GEV parameters for the top anual precipitation

    :param dataset: pd.DataFrame with the biggest daily precipitaion by hydrological or civil year

    :return: [0] = Form parameter (c), [1] = Localization parameter (loc), [2] = Scale parameter (scale), [3] = GEV data for plot
    """

    x = pd.to_numeric(dataset['precipitacao máxima anual (mm)'], errors="coerce").dropna(
    ).to_numpy(dtype=float)
    x = x[x > 0.0]
    c, loc, scale = sc.stats.genextreme.fit(x)
    dist = sc.stats.genextreme(c, loc=loc, scale=scale)
    gev = dist.rvs(size=100)
    gev = np.maximum(gev, 0.0)

    return float(c), float(loc), float(scale), gev


def compute_hmax_gev(c: float, loc: float, scale: float) -> pd.DataFrame:
    """Compute daily max preciptation using based in return window using GEV destribuition.

    :param c: Parameter of the form of GEV distribuition 
    :param loc: Localization parameter of GEV distribuition
    :param scale: Scale parameters from GEV distribuition

    :return: Max daily precipition (mm) based in return period (anos)
    """

    Tr_list = [2, 5, 10, 15, 20, 25, 50, 100, 250, 500, 1000]
    p = 1 - 1/np.array(Tr_list, dtype=float)
    x_Tr = sc.stats.genextreme.ppf(p, c, loc=loc, scale=scale)
    p_exec = 1/np.array(Tr_list, dtype=float)
    df_hmax1 = pd.DataFrame(
        {"t_r (anos)": Tr_list, "1/Tr": p_exec, "h_max,1 (mm)": x_Tr})

    return df_hmax1

def desag_max_daily_preciptation_intesity(h_max1): 
    """
    Desagregação da precipitação máxima diária (mm) em função do tempo de concentração (tc) em minutos e tempo de retorno (tr) em anos para matriz de intensidade de chuva (mm/h)

    :param h_max1: Precipitação máxima diária (mm) em função do período de retorno (anos).

    :return: Matriz de intensidade de chuva (mm/h) em função do tempo de concentração (tc) em minutos e tempo de retorno (tr) em anos.
    """

    tc_list = [1440, 720, 600, 480, 360, 180, 60, 30, 25, 20, 15, 10, 5]
    tc_convert = [1.14, 0.85, 0.78, 0.72, 0.54, 0.48,
                  0.42, 0.74, 0.91, 0.81, 0.70, 0.54, 0.34]
    i_convert = [1/24, 1/12, 1/8, 1/6, 1/3, 1/2, 1, 1 /
                 (30/60), 1/(25/60), 1/(20/60), 1/(15/60), 1/(10/60), 1/(5/60)]
    tr = []
    tc = []
    y = []
    for index, row in h_max1.iterrows():
        y_aux = []
        for i, value in enumerate(tc_convert):
            tr.append(row['t_r (anos)'])
            tc.append(tc_list[i])
            if i == 0:
                y_aux.append(row['h_max,1 (mm)'] * value)
            elif i > 0 and i <= 6:
                y_aux.append(y_aux[0] * value)
            elif i == 7:
                y_aux.append(y_aux[6] * value)
            else:
                y_aux.append(y_aux[7] * value)
        y_aux = [a * b for a, b in zip(y_aux, i_convert)]
        y += y_aux
    matrix = {'t_c (min)': tc, 't_r (anos)': tr, 'y_obs (mm/h)': y}

    return pd.DataFrame(matrix)

def compute_preciptation(dataframe: pd.DataFrame, metadata: dict) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Main function to process (clean) preciptation data and compute daily max preciptation (mm/h) through different periods and concentration periods.

    :param dataframe: BDMEP dataset ('data medicao', 'precipitacao total diaria (mm)', 'ano civil', 'mês', 'ano hidrologico') 
    :param metadata: Metadata from BDMEP data files (cidade, lat, long, alt, ..., etc)

    :return: [0] = Daily max preciptation (mm) given period (anos), [1] = Preciptation intensity matrix (mm/h) in relation to concentration time (tc) in minutes and return time (tr) in years.
    """

    # Format column type
    dataframe['precipitacao total diaria (mm)'] = pd.to_numeric(
        dataframe['precipitacao total diaria (mm)'], errors='coerce')

    # Compute mean and standard deviation from top anual preciptation
    hmax1d = compute_max_daily_preciptation(dataframe)
    c, loc, scale, _ = compute_gev(hmax1d)

    # Compute max daily height to different return times
    df_hmax1 = compute_hmax_gev(c, loc, scale)

    # Desagragate max daily preciptation in rain intensity matrix (mm/h)
    matrix = desag_max_daily_preciptation_intesity(
        df_hmax1)
    matrix['latitude'] = metadata['latitude']
    matrix['longitude'] = metadata['longitude']
    matrix['altitude'] = metadata['altitude']
    matrix['cidade'] = metadata['nome']

    return df_hmax1, matrix

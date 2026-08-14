import numpy as np
import scipy as sc
import pandas as pd


def compute_cdf(x: list) -> tuple[list, list]:
    """Compute Cumulative Distribution Function (CDF) from a list of values.

    :param x: input list

    :return: [0] = sorted values, [1] = CDF
    """

    x_sorted = np.sort(x)
    x_cdf = np.arange(1, len(x_sorted) + 1) / len(x_sorted)

    return list(x_sorted), list(x_cdf)


def verify_probability_distribuition(dataset: pd.DataFrame) -> pd.DataFrame:
    """Check probability distribuition parameters for the biggest daily preciptation by year.

    :param dataset: Biggest daily preciptation by year (hydrologic or civil)

    :return: [0] Result from Kolmogorov-Smirnov test for each distribuition, sorted by p-value, [1] Parameters from the best distribuition (biggest p-value), [2] Best distribuition name
    """

    distribuition_list = [
    'genextreme',
    'gumbel_r',
    'lognorm',
    'pearson3'
    ]
    teste_ks = {"Tipo de Distribuição": [], "Nome Scipy": [],
                "Parâmetros": [], "p-valor": [], "Teste KS": []}
    for dist in distribuition_list:
        dados = dataset['precipitacao máxima anual (mm)'].dropna().values
        x = dados[dados > 0]
        if dist == 'genextreme':
            dist_name = 'Generalized Extreme Value'
            params = sc.stats.genextreme.fit(x)
        
        elif dist == 'gumbel_r':
            dist_name = 'Gumbel'
            params = sc.stats.gumbel_r.fit(x)
        
        elif dist == 'lognorm':
            dist_name = 'Log-Normal'
            params = sc.stats.lognorm.fit(x, floc=0)
        
        elif dist == 'pearson3':
            dist_name = 'Pearson Type III'
            params = sc.stats.pearson3.fit(x)
        
        else:
            continue

        ks_stat, p_value = sc.stats.kstest(
            x,
            dist,
            args=params
        )
        
        teste_ks["Tipo de Distribuição"].append(dist_name)
        teste_ks["Nome Scipy"].append(dist)
        teste_ks["Parâmetros"].append(params)
        teste_ks["p-valor"].append(p_value)
        teste_ks["Teste KS"].append(ks_stat)
        teste_ks_df = pd.DataFrame(teste_ks)
        teste_ks_df = teste_ks_df.sort_values(
        by="p-valor", ascending=False).reset_index(drop=True)

    return teste_ks_df, teste_ks_df.loc[0, "Parâmetros"], teste_ks_df.loc[0, "Nome Scipy"]

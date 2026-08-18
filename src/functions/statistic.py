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


def verify_probability_distribuition(dataset: pd.DataFrame):
    """
    Fit candidate probability distributions to the annual maximum
    precipitation series and compare them using the Kolmogorov-Smirnov
    statistic.

    The distribution with the smallest KS statistic is selected.

    Parameters
    ----------
    dataset : pd.DataFrame
        Annual maximum daily precipitation series.

    Returns
    -------
    results_df : pd.DataFrame
        Candidate distributions and corresponding KS statistics,
        sorted from smallest to largest KS statistic.

    params : tuple
        Parameters of the selected distribution.

    selected_dist : str
        SciPy name of the selected distribution.
    """

    distribution_list = [
        'genextreme',
        'gumbel_r',
        'lognorm',
        'pearson3'
    ]

    results = {
        "Tipo de Distribuição": [],
        "Nome Scipy": [],
        "Parâmetros": [],
        "Estatística KS": []
    }

    data = dataset[
        'precipitacao máxima anual (mm)'
    ].dropna().values

    x = data[data > 0]

    if len(x) < 2:
        raise ValueError(
            "Insufficient annual maximum precipitation data "
            "for probability distribution fitting."
        )

    for dist in distribution_list:

        if dist == 'genextreme':
            dist_name = 'Generalized Extreme Value (GEV)'
            dist_obj = sc.stats.genextreme
            params = dist_obj.fit(x)

        elif dist == 'gumbel_r':
            dist_name = 'Gumbel'
            dist_obj = sc.stats.gumbel_r
            params = dist_obj.fit(x)

        elif dist == 'lognorm':
            dist_name = 'Log-Normal'
            dist_obj = sc.stats.lognorm

            params = dist_obj.fit(
                x,
                floc=0
            )

        elif dist == 'pearson3':
            dist_name = 'Pearson Type III'
            dist_obj = sc.stats.pearson3
            params = dist_obj.fit(x)

        else:
            continue

        ks_stat = sc.stats.kstest(
            x,
            dist,
            args=params
        ).statistic

        results[
            "Tipo de Distribuição"
        ].append(dist_name)

        results[
            "Nome Scipy"
        ].append(dist)

        results[
            "Parâmetros"
        ].append(params)

        results[
            "Estatística KS"
        ].append(ks_stat)

    results_df = pd.DataFrame(results)

    results_df = results_df.sort_values(
        by="Estatística KS",
        ascending=True
    ).reset_index(drop=True)

    return (
        results_df,
        results_df.loc[0, "Parâmetros"],
        results_df.loc[0, "Nome Scipy"]
    )

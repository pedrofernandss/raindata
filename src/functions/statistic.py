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
    """
    Fit candidate probability distributions to the annual maximum
    precipitation series and compare them using the Kolmogorov-Smirnov
    statistic.

    The distribution with the smallest KS statistic is selected.

    :param dataset: Annual maximum daily precipitation series
    :return:
        [0] DataFrame with fitted distributions and KS statistics,
        sorted from smallest to largest KS statistic
        [1] Parameters of the selected distribution
        [2] SciPy name of the selected distribution
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

            # Precipitation is strictly positive;
            # location is fixed at zero.
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

        # KS statistic used as a comparative measure of fit.
        # The conventional KS p-value is not used for model selection
        # because distribution parameters are estimated from the same sample.
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

    # Smaller KS statistic indicates closer agreement
    # between empirical and fitted CDFs.
    results_df = results_df.sort_values(
        by="Estatística KS",
        ascending=True
    ).reset_index(drop=True)

    return (
        results_df,
        results_df.loc[0, "Parâmetros"],
        results_df.loc[0, "Nome Scipy"]
    )

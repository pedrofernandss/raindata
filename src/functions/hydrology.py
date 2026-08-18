import numpy as np
import scipy as sc
import pandas as pd


def compute_max_daily_preciptation(
        dataset: pd.DataFrame,
        hydro_init: int = 1,
        max_missing_days: int = 15
    ) -> pd.DataFrame:

    """
    Compute annual maximum daily precipitation using valid daily
    observations.

    Incomplete months are not discarded for extreme-value analysis.
    A civil or hydrological year is retained when the number of missing
    daily precipitation observations does not exceed max_missing_days.
    """

    df = dataset.copy()

    df['data medicao'] = pd.to_datetime(
        df['data medicao'],
        errors='coerce'
    )

    df['precipitacao total diaria (mm)'] = pd.to_numeric(
        df['precipitacao total diaria (mm)'],
        errors='coerce'
    )

    results = []

    for hydro_year, group in df.groupby('ano hidrologico'):

        if pd.isna(hydro_year):
            continue

        hydro_year = int(hydro_year)

        if hydro_init == 1:

            start_date = pd.Timestamp(
                year=hydro_year,
                month=1,
                day=1
            )

            end_date = pd.Timestamp(
                year=hydro_year,
                month=12,
                day=31
            )

        else:

            start_date = pd.Timestamp(
                year=hydro_year - 1,
                month=hydro_init,
                day=1
            )

            end_date = (
                pd.Timestamp(
                    year=hydro_year,
                    month=hydro_init,
                    day=1
                )
                - pd.Timedelta(days=1)
            )

        expected_days = (
            end_date - start_date
        ).days + 1

        group = group[
            (group['data medicao'] >= start_date) &
            (group['data medicao'] <= end_date)
        ].copy()

        valid = group.dropna(
            subset=['precipitacao total diaria (mm)']
        ).copy()

        valid = valid[
            valid['precipitacao total diaria (mm)'] >= 0
        ]

        valid_days = (
            valid['data medicao']
            .dt.normalize()
            .nunique()
        )

        missing_days = expected_days - valid_days

        if missing_days > max_missing_days:
            continue

        max_precip = valid[
            'precipitacao total diaria (mm)'
        ].max()

        if pd.notna(max_precip) and max_precip > 0:

            results.append({
                'ano hidrologico': hydro_year,
                'precipitacao máxima anual (mm)': max_precip,
                'dias validos': valid_days,
                'dias ausentes': missing_days
            })

    return pd.DataFrame(
        results,
        columns=[
            'ano hidrologico',
            'precipitacao máxima anual (mm)',
            'dias validos',
            'dias ausentes'
        ]
    )


def compute_gev(dataset: pd.DataFrame) -> tuple[float, float, float, list]:
    """Check the GEV parameters for the top anual precipitation

    :param dataset: pd.DataFrame with the biggest daily precipitaion
                    by hydrological or civil year

    :return: [0] = Form parameter (c),
             [1] = Localization parameter (loc),
             [2] = Scale parameter (scale),
             [3] = GEV data for plot
    """

    x = pd.to_numeric(
        dataset['precipitacao máxima anual (mm)'],
        errors="coerce"
    ).dropna().to_numpy(dtype=float)

    x = x[x > 0.0]

    # Sort data for L-moments calculation
    x = np.sort(x)

    n = len(x)

    if n < 3:
        raise ValueError(
            "At least three annual maximum precipitation values "
            "are required to fit the GEV distribution."
        )

    # Probability weighted moments
    b0 = np.mean(x)

    b1 = np.sum(
        ((np.arange(1, n + 1) - 1) / (n - 1)) * x
    ) / n

    b2 = np.sum(
        (
            (np.arange(1, n + 1) - 1) *
            (np.arange(1, n + 1) - 2)
            /
            ((n - 1) * (n - 2))
        ) * x
    ) / n

    # Sample L-moments
    l1 = b0
    l2 = 2 * b1 - b0
    l3 = 6 * b2 - 6 * b1 + b0

    tau3 = l3 / l2

    # GEV shape parameter by L-moments
    aux = 2 / (3 + tau3) - np.log(2) / np.log(3)

    c = 7.8590 * aux + 2.9554 * aux ** 2

    # Scale parameter
    gamma_value = sc.special.gamma(1 + c)

    scale = (
        l2 * c
        /
        ((1 - 2 ** (-c)) * gamma_value)
    )

    # Location parameter
    loc = (
        l1
        -
        scale * (1 - gamma_value) / c
    )

    dist = sc.stats.genextreme(
        c,
        loc=loc,
        scale=scale
    )

    gev = dist.rvs(
        size=100,
        random_state=42
    )

    gev = np.maximum(gev, 0.0)

    return float(c), float(loc), float(scale), gev


def compute_hmax_gev(c: float, loc: float, scale: float) -> pd.DataFrame:
    """Compute daily max preciptation using based in return window using GEV destribuition.

    :param c: Parameter of the form of GEV distribuition 
    :param loc: Localization parameter of GEV distribuition
    :param scale: Scale parameters from GEV distribuition

    :return: Max daily precipition (mm) based in return period (anos)
    """

    Tr_list = [2, 5, 10, 15, 20, 25, 50, 100]
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

    tc_list = [1440, 720, 600, 480, 360, 60, 30, 25, 20, 15, 10, 5]

    tc_convert = [1.14, 0.85, 0.82, 0.78, 0.72, 0.42,
              0.74, 0.91, 0.81, 0.70, 0.54, 0.34]

    i_convert = [1/24, 1/12, 1/10, 1/8, 1/6, 1,
             1/(30/60), 1/(25/60), 1/(20/60),
             1/(15/60), 1/(10/60), 1/(5/60)]
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
            elif i > 0 and i <= 5:
                y_aux.append(y_aux[0] * value)
            elif i == 6:
                y_aux.append(y_aux[5] * value)
            else:
                y_aux.append(y_aux[6] * value)
        y_aux = [a * b for a, b in zip(y_aux, i_convert)]
        y += y_aux
    matrix = {'t_c (min)': tc, 't_r (anos)': tr, 'y_obs (mm/h)': y}

    return pd.DataFrame(matrix)


def compute_preciptation(dataframe: pd.DataFrame, metadata: dict) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Main function to process (clean) preciptation data and compute daily max preciptation (mm/h) through different periods and concentration periods.

    :param dataframe: BDMEP dataset ('data medicao', 'precipitacao total diaria (mm)', 'ano civil', 'mes', 'ano hidrologico') 
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


def compute_spi(dataset: pd.DataFrame) -> pd.DataFrame:
    """Compute monthly Standardized Precipitation Index (SPI-1).

    :param dataset: Data monthly agregated ('year', 'month', 'monthly preciptation (mm)')

    :return: The same dataset but with the SPI-1 column
    """

    col_precip = 'precipitacao mensal (mm)'

    dataset['SPI_1'] = np.nan

    for mes in range(1, 13):
        mask_mes = dataset['mes'] == mes
        dados_mes = dataset.loc[mask_mes, col_precip]

        if dados_mes.empty:
            continue

        zeros = (dados_mes == 0).sum()
        positivos = dados_mes[dados_mes > 0]
        q = zeros / len(dados_mes)

        # Ajuste Gamma e CDF ajustada
        if len(positivos) > 1:
            a, loc, scale = sc.stats.gamma.fit(positivos, floc=0)
            cdf = sc.stats.gamma.cdf(dados_mes, a, loc=loc, scale=scale)
            cdf_adj = np.clip(q + (1 - q) * cdf, 1e-6, 1 - 1e-6)
            spi = sc.stats.norm.ppf(cdf_adj)
            dataset.loc[dados_mes.index, 'SPI_1'] = spi

    return dataset

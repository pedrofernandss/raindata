import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl

mpl.rcParams.update({
    'font.family': 'serif',
    'mathtext.fontset': 'cm',
    'axes.unicode_minus': False
})

_PLOT_CONFIG = {
    'width_cm': 12,
    'height_cm': 10,
    'inches_per_cm': 1 / 2.54,
    'label_size': 14,
    'axis_size': 14,
    'legend_size': 10,
    'alpha': 0.4,
}


def _get_fig_size() -> tuple[float, float]:
    cfg = _PLOT_CONFIG
    width_in = cfg['width_cm'] * cfg['inches_per_cm']
    height_in = cfg['height_cm'] * cfg['inches_per_cm']
    return width_in, height_in


def plot_monthly_average_precipitation(output_folder: str, name: str, monthly: pd.DataFrame, rainy_season_start: int = 1, lang: str = 'pt'):
    labels = {
        'pt': {
            'xlabel': 'Mês',
            'ylabel': 'Precipitação média mensal (mm)',
            'driest': 'Mês mais seco',
            'wettest': 'Mês mais chuvoso',
            'rainy_start': 'Início do ano hidrológico',
            'filename': f'z_monthly_avg_precipitation_{name}_pt.png'
        },
        'en': {
            'xlabel': 'Month',
            'ylabel': 'Mean monthly precipitation (mm)',
            'driest': 'Driest month',
            'wettest': 'Wettest month',
            'rainy_start': 'Start of hydrological year',
            'filename': f'z_monthly_avg_precipitation_{name}_en.png'
        }
    }

    cfg = _PLOT_CONFIG
    width_in, height_in = _get_fig_size()

    fig, ax = plt.subplots(figsize=(width_in, height_in))
    ax.plot(monthly['mes'], monthly['precipitacao media mensal (mm)'],
            marker='o', color='red')

    driest_idx = monthly['precipitacao media mensal (mm)'].idxmin()
    driest_month = int(monthly.loc[driest_idx, 'mes'])
    ax.scatter(driest_month, monthly['precipitacao media mensal (mm)'][driest_idx],
               s=140, label=f"{labels[lang]['driest']} = {driest_month}", color='blue')

    wettest_idx = monthly['precipitacao media mensal (mm)'].idxmax()
    wettest_month = int(monthly.loc[wettest_idx, 'mes'])
    ax.scatter(wettest_month, monthly['precipitacao media mensal (mm)'][wettest_idx],
               s=140, label=f"{labels[lang]['wettest']} = {wettest_month}", color='green')

    ax.axvline(x=rainy_season_start, color='purple', linestyle='--', linewidth=2.0,
               alpha=0.7, label=f"{labels[lang]['rainy_start']} = {rainy_season_start}")
    ax.set_xlabel(labels[lang]['xlabel'], fontsize=cfg['label_size'])
    ax.set_ylabel(labels[lang]['ylabel'], fontsize=cfg['label_size'])

    ax.set_xticks(range(1, 13))
    ax.set_xlim(0.5, 12.5)

    ax.tick_params(axis='both', which='major', labelsize=cfg['axis_size'])
    ax.grid(True, alpha=cfg['alpha'])
    
    ax.legend(fontsize=cfg['legend_size'], loc='lower center',
              bbox_to_anchor=(0.5, 1.02), ncol=1, frameon=True)
    fig.tight_layout(rect=[0, 0, 1, 0.95])

    if output_folder is not None:
        fig.savefig(os.path.join(output_folder,
                    labels[lang]['filename']), dpi=600)

    return fig


def plot_pdf_daily_max_precipitation(
        output_folder: str,
        name: str,
        data: dict,
        lang: str = 'pt'):

    import scipy.stats as stats

    labels = {
        'pt': {
            'ylabel': 'Densidade de probabilidade',
            'xlabel': r'$h_{max,anual}$ (mm)',
            'observed': 'Densidade empírica (KDE)',
            'fitted': 'Distribuição ajustada',
            'filename': f'{name}_pt.png'
        },
        'en': {
            'ylabel': 'Probability density',
            'xlabel': r'$h_{max,annual}$ (mm)',
            'observed': 'Empirical density (KDE)',
            'fitted': 'Fitted distribution',
            'filename': f'{name}_en.png'
        }
    }

    cfg = _PLOT_CONFIG
    width_in, height_in = _get_fig_size()

    fig, ax = plt.subplots(figsize=(width_in, height_in))

    ax.tick_params(
        axis='both',
        which='major',
        labelsize=cfg['axis_size'],
        colors='black'
    )

    ax.set_xlabel(
        labels[lang]['xlabel'],
        fontsize=cfg['label_size'],
        color='black'
    )

    ax.set_ylabel(
        labels[lang]['ylabel'],
        fontsize=cfg['label_size'],
        color='black'
    )

    ax.grid(
        True,
        which='both',
        linestyle='-',
        linewidth=0.2,
        alpha=cfg['alpha']
    )

    # Observed annual maxima: empirical density estimated by KDE
    observed = np.asarray(data['observed'], dtype=float)

    if len(observed) >= 2 and np.std(observed) > 0:

        kde = stats.gaussian_kde(observed)

        x_empirical = np.linspace(
            observed.min(),
            observed.max(),
            500
        )

        y_empirical = kde(x_empirical)

        ax.plot(
            x_empirical,
            y_empirical,
            color='blue',
            label=labels[lang]['observed']
        )

        ax.fill_between(
            x_empirical,
            y_empirical,
            alpha=cfg['alpha'],
            color='blue'
        )

    # Theoretical PDF of the selected fitted distribution
    ax.plot(
        data['fitted']['x'],
        data['fitted']['y'],
        color='red',
        linewidth=2,
        label=labels[lang]['fitted']
    )

    ax.legend(
        fontsize=cfg['legend_size'],
        loc='lower center',
        bbox_to_anchor=(0.5, 1.02),
        ncol=1,
        frameon=True
    )

    fig.tight_layout(rect=[0, 0, 1, 0.95])

    if output_folder is not None:
        fig.savefig(
            os.path.join(
                output_folder,
                labels[lang]['filename']
            ),
            dpi=600,
            bbox_inches='tight'
        )

    return fig


def plot_cdf_daily_max_precipitation(output_folder: str, name: str, data: dict, lang: str = 'pt'):
    labels = {
        'pt': {
            'xlabel': r'$h_{max,anual}$ (mm)',
            'ylabel': 'Probabilidade acumulada',
            'legend': ['dados', 'melhor distribuição'],
            'filename': f'{name}_pt.png'
        },
        'en': {
            'xlabel': r'$h_{max,annual}$ (mm)',
            'ylabel': 'Cumulative probability',
            'legend': ['data', 'best distribution'],
            'filename': f'{name}_en.png'
        }
    }

    cfg = _PLOT_CONFIG
    width_in, height_in = _get_fig_size()
    colors = ['blue', 'red']

    fig, ax = plt.subplots(figsize=(width_in, height_in))
    ax.scatter(data['real']['x'], data['real']['y'],
               label=labels[lang]['legend'][0], color=colors[0], s=30)
    ax.plot(data['numerica']['x'], data['numerica']['y'],
            label=labels[lang]['legend'][1], color=colors[1], linewidth=2)
    ax.set_xlabel(labels[lang]['xlabel'],
                  fontsize=cfg['label_size'], color='black')
    ax.set_ylabel(labels[lang]['ylabel'],
                  fontsize=cfg['label_size'], color='black')
    ax.tick_params(axis='both', which='major',
                   labelsize=cfg['axis_size'], colors='black')
    plt.grid(True, linestyle='-', linewidth=0.2, alpha=cfg['alpha'])
    plt.legend(fontsize=cfg['legend_size'], loc='lower center',
               bbox_to_anchor=(0.5, 1.02), frameon=True)
    plt.tight_layout(rect=[0, 0, 1, 0.95])

    if output_folder is not None:
        fig.savefig(os.path.join(output_folder,
                    labels[lang]['filename']), dpi=600, bbox_inches='tight')

    return fig


def plot_idf_curves(output_folder: str, name: str, lang: str, rainfall_matrix: pd.DataFrame):
    labels = {
        'pt': {
            'x_label': 'Duração (min)',
            'y_label': 'Intensidade (mm/h)',
            'title': 'Período de retorno (anos)',
            'filename': f'{name}_pt.png'
        },
        'en': {
            'x_label': 'Duration (min)',
            'y_label': 'Intensity (mm/h)',
            'title': 'Return period (years)',
            'filename': f'{name}_en.png'
        }
    }

    cfg = _PLOT_CONFIG
    width_in, height_in = _get_fig_size()
    return_periods = sorted(
        rainfall_matrix['t_r (anos)']
        .dropna()
        .unique()
    )

    fig, ax = plt.subplots(figsize=(width_in, height_in))
    for period in return_periods:
        filtered = rainfall_matrix[rainfall_matrix['t_r (anos)'] == period]
        ax.plot(filtered['t_c (min)'], filtered['y_obs (mm/h)'],
                linewidth=2.8, marker='o', label=period)
    ax.set_xlabel(labels[lang]['x_label'], fontsize=cfg['label_size'])
    ax.set_ylabel(labels[lang]['y_label'], fontsize=cfg['label_size'])
    ax.grid(True, which="both", linestyle="--", alpha=cfg['alpha'])
    ax.legend(ncol=2, title=labels[lang]['title'], fontsize=cfg['legend_size'])
    plt.tight_layout()

    if output_folder is not None:
        fig.savefig(os.path.join(output_folder,
                    labels[lang]['filename']), dpi=600, bbox_inches='tight')

    return fig


def plot_time_series(output_folder: str, name: str, df: pd.DataFrame, date_col: str, value_col: str, value_label: str, lang: str = 'pt'):
    """Plot a generic time series (e.g. daily total precipitation) for a station.

    :param output_folder: Folder to save the chart (None to skip saving)
    :param name: Station name/id for file naming
    :param df: DataFrame containing the date and value columns
    :param date_col: Name of the date column
    :param value_col: Name of the numeric column to plot
    :param value_label: Label used on the y-axis
    :param lang: 'pt' or 'en'
    """

    labels = {
        'pt': {
            'xlabel': 'Data',
            'legend': 'Dados observados',
            'filename': f'{name}_timeseries_pt.png'
        },
        'en': {
            'xlabel': 'Date',
            'legend': 'Observed data',
            'filename': f'{name}_timeseries_en.png'
        }
    }

    cfg = _PLOT_CONFIG
    width_in = 32 * cfg['inches_per_cm']
    height_in = 11 * cfg['inches_per_cm']

    fig, ax = plt.subplots(figsize=(width_in, height_in))
    ax.plot(df[date_col], df[value_col], color='steelblue',
            linewidth=0.8, label=labels[lang]['legend'])
    ax.set_xlabel(labels[lang]['xlabel'], fontsize=cfg['label_size'])
    ax.set_ylabel(value_label, fontsize=cfg['label_size'])
    ax.tick_params(axis='both', which='major', labelsize=cfg['axis_size'])
    ax.grid(
        True,
        axis='y',
        linestyle='--',
        linewidth=0.5,
        alpha=0.35
    )
    ax.legend(fontsize=cfg['legend_size'], loc='lower center',
              bbox_to_anchor=(0.5, 1.02), ncol=1, frameon=True)
    fig.tight_layout(rect=[0, 0, 1, 0.92])

    if output_folder is not None:
        fig.savefig(os.path.join(output_folder,
                    labels[lang]['filename']), dpi=600, bbox_inches='tight')

    return fig

def plot_spi(
        output_folder: str,
        name: str,
        dataset: pd.DataFrame,
        lang: str = 'pt'
    ):
    """Plot SPI-1 time series with color bands by drought/wet category.

    :param output_folder: Folder to save the chart (None to skip saving)
    :param name: Station name/id for file naming
    :param dataset: DataFrame with 'ano civil', 'mes' and 'SPI_1' columns
    :param lang: 'pt' or 'en'
    """

    labels = {
        'pt': {
            'ylabel': 'SPI-1',
            'xlabel': 'Data',
            'filename': f'{name}_spi_pt.png',
            'seco_extremo': 'Extremamente seco',
            'seco_severo': 'Severamente seco',
            'seco_moderado': 'Moderadamente seco',
            'umido_moderado': 'Moderadamente úmido',
            'umido_severo': 'Severamente úmido',
            'umido_extremo': 'Extremamente úmido',
        },
        'en': {
            'ylabel': 'SPI-1',
            'xlabel': 'Date',
            'filename': f'{name}_spi_en.png',
            'seco_extremo': 'Extremely dry',
            'seco_severo': 'Severely dry',
            'seco_moderado': 'Moderately dry',
            'umido_moderado': 'Moderately wet',
            'umido_severo': 'Severely wet',
            'umido_extremo': 'Extremely wet',
        }
    }

    cfg = _PLOT_CONFIG

    width_in = 32 * cfg['inches_per_cm']
    height_in = 11 * cfg['inches_per_cm']

    df = dataset.copy()

    # Build monthly date
    df['date'] = pd.to_datetime(
        df['ano civil'].astype(str)
        + '-'
        + df['mes'].astype(str)
        + '-01'
    )

    df = df.sort_values('date')

    # Reconstruct the complete monthly timeline so that months
    # excluded by the completeness criterion appear as gaps
    # rather than being visually connected.
    if not df.empty:

        full_monthly_index = pd.date_range(
            start=df['date'].min(),
            end=df['date'].max(),
            freq='MS'
        )

        df = (
            df.set_index('date')
            .reindex(full_monthly_index)
            .rename_axis('date')
            .reset_index()
        )

    fig, ax = plt.subplots(
        figsize=(width_in, height_in)
    )

    # ---------------------------------------------------------
    # SPI classification bands
    # ---------------------------------------------------------

    band_alpha = 0.18

    ax.axhspan(
        -4.0, -2.0,
        alpha=band_alpha,
        color='#8B0000',
        label=labels[lang]['seco_extremo']
    )
    
    ax.axhspan(
        -2.0, -1.5,
        alpha=band_alpha,
        color='#D7301F',
        label=labels[lang]['seco_severo']
    )
    
    ax.axhspan(
        -1.5, -1.0,
        alpha=band_alpha,
        color='#FC8D59',
        label=labels[lang]['seco_moderado']
    )
    
    ax.axhspan(
        1.0, 1.5,
        alpha=band_alpha,
        color='#91BFDB',
        label=labels[lang]['umido_moderado']
    )
    
    ax.axhspan(
        1.5, 2.0,
        alpha=band_alpha,
        color='#4575B4',
        label=labels[lang]['umido_severo']
    )
    
    ax.axhspan(
        2.0, 4.0,
        alpha=band_alpha,
        color='#313695',
        label=labels[lang]['umido_extremo']
    )
    # Zero line
    ax.axhline(
        0,
        color='black',
        linewidth=0.9,
        linestyle='--',
        alpha=0.6,
        zorder=4
    )

    # Monthly SPI-1 bars
    bar_colors = np.where(df['SPI_1'] >= 0, '#2C7FB8', '#D95F0E')
    
    ax.bar(
        df['date'],
        df['SPI_1'],
        width=25,           # largura em dias, adequada para série mensal
        color=bar_colors,
        edgecolor='black',
        linewidth=0.25,
        alpha=0.85,
        zorder=3
    )

    # ---------------------------------------------------------
    # Figure formatting
    # ---------------------------------------------------------

    ax.set_xlabel(
        labels[lang]['xlabel'],
        fontsize=cfg['label_size']
    )

    ax.set_ylabel(
        labels[lang]['ylabel'],
        fontsize=cfg['label_size']
    )

    ax.tick_params(
        axis='both',
        which='major',
        labelsize=cfg['axis_size']
    )

    ax.grid(
        True,
        alpha=cfg['alpha']
    )

    ax.legend(
        fontsize=cfg['legend_size'],
        loc='lower center',
        bbox_to_anchor=(0.5, 1.02),
        ncol=6,
        frameon=True
    )

    fig.tight_layout(
        rect=[0, 0, 1, 0.92]
    )

    # ---------------------------------------------------------
    # Save figure
    # ---------------------------------------------------------

    if output_folder is not None:

        fig.savefig(
            os.path.join(
                output_folder,
                labels[lang]['filename']
            ),
            dpi=600,
            bbox_inches='tight'
        )

    return fig


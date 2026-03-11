import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl

mpl.rcParams.update({
    'font.family': 'serif',
    'mathtext.fontset': 'cm',
    'axes.unicode_minus': False
})

# Shared visual settings
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


def plot_monthly_average_precipitation(output_folder: str, name: str, monthly: pd.DataFrame, rainy_season_start: int = 1, lang: str = 'pt') -> None:
    """Generates a monthly average precipitation chart in Portuguese or English.

    :param output_folder: Folder where the chart will be saved
    :param name: City name and station code for chart file naming
    :param monthly: Monthly average precipitation data
    :param rainy_season_start: Month when the rainy season starts
    :param lang: Chart language ('pt' for Portuguese, 'en' for English)
    """

    labels = {
        'pt': {
            'xlabel': 'Mês',
            'ylabel': 'Precipitação média mensal (mm)',
            'driest': 'Mês mais seco',
            'wettest': 'Mês mais chuvoso',
            'rainy_start': 'Início do período chuvoso',
            'filename': f'z_monthly_avg_precipitation_{name}_pt.png'
        },
        'en': {
            'xlabel': 'Month',
            'ylabel': 'Average precipitation (mm)',
            'driest': 'Driest month',
            'wettest': 'Wettest month',
            'rainy_start': 'Start of rainy season',
            'filename': f'z_monthly_avg_precipitation_{name}_en.png'
        }
    }

    cfg = _PLOT_CONFIG
    width_in, height_in = _get_fig_size()

    fig, ax = plt.subplots(figsize=(width_in, height_in))
    ax.plot(monthly['mes'], monthly['precipitacao media mensal (mm)'],
            marker='o', color='red')

    driest_idx = monthly['precipitacao media mensal (mm)'].idxmin()
    driest_month = driest_idx + 1
    ax.scatter(driest_month, monthly['precipitacao media mensal (mm)'][driest_idx],
               s=140, label=f"{labels[lang]['driest']} = {driest_month}", color='blue')

    wettest_idx = monthly['precipitacao media mensal (mm)'].idxmax()
    wettest_month = wettest_idx + 1
    ax.scatter(wettest_month, monthly['precipitacao media mensal (mm)'][wettest_idx],
               s=140, label=f"{labels[lang]['wettest']} = {wettest_month}", color='green')

    ax.axvline(x=rainy_season_start, color='purple', linestyle='--', linewidth=2.0,
               alpha=0.7, label=f"{labels[lang]['rainy_start']} = {rainy_season_start}")
    ax.set_xlabel(labels[lang]['xlabel'], fontsize=cfg['label_size'])
    ax.set_ylabel(labels[lang]['ylabel'], fontsize=cfg['label_size'])
    ax.tick_params(axis='both', which='major', labelsize=cfg['axis_size'])
    ax.grid(True, alpha=cfg['alpha'])
    ax.legend(fontsize=cfg['legend_size'], loc='lower center',
              bbox_to_anchor=(0.5, 1.02), ncol=1, frameon=True)
    fig.tight_layout(rect=[0, 0, 1, 0.95])

    if output_folder is not None:
        fig.savefig(os.path.join(output_folder,
                    labels[lang]['filename']), dpi=600)

    return fig


def plot_pdf_daily_max_precipitation(output_folder: str, name: str, data: dict, lang: str = 'pt') -> None:
    """Generates a PDF (KDE) chart of daily maximum precipitation in Portuguese or English.

    :param output_folder: Folder where the chart will be saved
    :param name: City/station name for file naming
    :param data: DataFrame containing 'real' and 'numerica' columns
    :param lang: Chart language ('pt' or 'en')
    """

    import seaborn as sns

    labels = {
        'pt': {
            'ylabel': 'Densidade',
            'xlabel': r'$i_{max,anual}$ (mm)',
            'legend': ['dados', 'melhor distribuição'],
            'filename': f'{name}_pt.png'
        },
        'en': {
            'ylabel': 'Density',
            'xlabel': r'$i_{max,annual}$ (mm)',
            'legend': ['data', 'best distribution'],
            'filename': f'{name}_en.png'
        }
    }

    cfg = _PLOT_CONFIG
    width_in, height_in = _get_fig_size()
    colors = ['blue', 'red']

    fig, ax = plt.subplots(figsize=(width_in, height_in))
    ax.tick_params(axis='both', which='major',
                   labelsize=cfg['axis_size'], colors='black')
    ax.set_xlabel(labels[lang]['xlabel'],
                  fontsize=cfg['label_size'], color='black')
    ax.set_ylabel(labels[lang]['ylabel'],
                  fontsize=cfg['label_size'], color='black')
    plt.grid(True, which='both', linestyle='-',
             linewidth=0.2, alpha=cfg['alpha'])
    sns.kdeplot(data=data, x='real', fill=True, alpha=cfg['alpha'],
                ax=ax, color=colors[0], label=labels[lang]['legend'][0])
    sns.kdeplot(data=data, x='numerica', fill=True, alpha=cfg['alpha'],
                ax=ax, color=colors[1], label=labels[lang]['legend'][1])
    plt.legend(fontsize=cfg['legend_size'], loc='lower center',
               bbox_to_anchor=(0.5, 1.02), ncol=1, frameon=True)
    plt.tight_layout(rect=[0, 0, 1, 0.95])
    fig.savefig(os.path.join(output_folder,
                labels[lang]['filename']), dpi=600, bbox_inches='tight')
    plt.show()


def plot_cdf_daily_max_precipitation(output_folder: str, name: str, data: dict, lang: str = 'pt') -> None:
    """Generates a CDF chart of observed vs theoretical daily maximum annual precipitation.

    :param output_folder: Folder where the chart will be saved
    :param name: City/station name
    :param data: Dictionary with 'real' and 'numerica' keys containing 'x' and 'y' arrays
    :param lang: Chart language ('pt' or 'en')
    """

    labels = {
        'pt': {
            'xlabel': r'$i_{max,anual}$ (mm)',
            'ylabel': 'Probabilidade acumulada',
            'legend': ['dados', 'melhor distribuição'],
            'filename': f'{name}_pt.png'
        },
        'en': {
            'xlabel': r'$i_{max,annual}$ (mm)',
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
    fig.savefig(os.path.join(output_folder,
                labels[lang]['filename']), dpi=600, bbox_inches='tight')
    plt.show()


def plot_idf_curves(output_folder: str, name: str, lang: str, rainfall_matrix: pd.DataFrame) -> None:
    """Plots IDF (Intensity-Duration-Frequency) curves.

    :param output_folder: Folder where the chart will be saved
    :param name: Station/city name
    :param lang: Chart language ('pt' or 'en')
    :param rainfall_matrix: DataFrame with t_c (min), t_r (years) and y_obs (mm/h)
    """

    labels = {
        'pt': {
            'x_label': 'Tempo de Duração (min)',
            'y_label': 'Intensidade (mm/h)',
            'title': 'Tempo de Retorno (anos)',
            'filename': f'{name}_pt.png'
        },
        'en': {
            'x_label': 'Duration Time (min)',
            'y_label': 'Intensity (mm/h)',
            'title': 'Return Period (years)',
            'filename': f'{name}_en.png'
        }
    }

    cfg = _PLOT_CONFIG
    width_in, height_in = _get_fig_size()
    return_periods = [2, 5, 10, 15, 20, 25, 50, 100, 250, 500, 1000]

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
    fig.savefig(os.path.join(output_folder,
                labels[lang]['filename']), dpi=600, bbox_inches='tight')
    plt.show()

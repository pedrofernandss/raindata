"""Módulo para manipulação de dados da plataforma Banco de Dados Meteorológicos do INMET"""
from datetime import datetime

import os
import pandas as pd
import numpy as np
import scipy as sc
import matplotlib.pyplot as plt
import matplotlib as mpl
import seaborn as sns
mpl.rcParams.update({
                        'font.family': 'serif',
                        'mathtext.fontset': 'cm',
                        'axes.unicode_minus': False
                    })


def eh_continuo(lista_meses: list) -> tuple[bool, list]:
    """Verifica se os 6 meses representam um bloco contínuo no calendário. Considera circularidade: exemplo (9,10,11,12,1,2)

    :param lista_meses: Lista com os meses (1 a 12)

    :return: [0] = Booleano indicando se os meses são contínuos, [1] = Lista com os meses em ordem contínua (vazia se não forem contínuos)
    """

    lista_meses = sorted(lista_meses)

    # Testar todas as rotações possíveis, pois o ano é circular
    for inicio in lista_meses:
        bloco = [(inicio + i - 1) % 12 + 1 for i in range(6)]
        if set(bloco) == set(lista_meses):
            return True, bloco

    return False, []


def definicao_ano_hidrologico(df_final: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, str, int]:
    """Define se a preciptação deverá ser verificada via ano civil ou ano hidrológico

    :param: df_final: Dados meteorológicos base BDMEP limpos ('data medicao', 'precipitacao total diaria (mm)', 'ano civil', 'mês')
    """

    # Médias mensais de precipitação
    total_mensal = df_final.groupby(['ano civil', 'mês'])['precipitacao total diaria (mm)'].sum().reset_index()
    mensal = total_mensal.groupby('mês')['precipitacao total diaria (mm)'].mean().reset_index()
    mensal.rename(columns={'precipitacao total diaria (mm)': 'precipitacao media mensal (mm)'}, inplace=True)

    # Meses mais secos
    meses_secos = mensal.sort_values(by='precipitacao media mensal (mm)').head(6)

    # Verifica se os meses secos são contínuos
    ano_tipo, bloco_meses = eh_continuo(meses_secos['mês'].tolist())
    if ano_tipo:
        metodologia = "Ano hidrológico"
        inicio_hidrologico = bloco_meses[-1] % 12 + 1
    else:
        metodologia = "Ano civil"
        inicio_hidrologico = 1

    return mensal, meses_secos, metodologia, inicio_hidrologico


def ler_dados(dados: str) -> tuple[dict, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Leitura de dados do arquivo CSV do BDMEP e extração do cabeçalho.

    :param dados: Caminho para o arquivo CSV da da base de dados BDMEP

    :return: [0] = Metadados do arquivo de dados BDMEP (cidade, lat, long, alt, ..., etc), [1] = Médias mensais de precipitação, [2] = Meses mais secos com média mensal, [3] = Dados meteorológicos base BDMEP limpos ('data medicao', 'precipitacao total diaria (mm)', 'ano civil', 'mês', 'ano hidrologico')
    """

    # Organização colunas
    with open(dados, 'r', encoding='utf-8') as f:
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
    df = pd.read_csv(dados, sep=";", encoding="utf-8", skiprows=9)
    df = df.loc[:, ~df.columns.str.contains('^Unnamed', case=False)]
    df.columns = df.columns.str.strip().str.lower()
    if 'precipitacao total, diario(mm)' in df.columns.tolist():
        rename_map = {
                        'data medicao': 'data medicao',
                        'precipitacao total, diario(mm)': 'precipitacao total diaria (mm)',
                    }
        df = df.rename(columns=lambda x: rename_map.get(x, x))
    else:
        rename_map = {
                        'data medicao': 'data medicao',
                        'precipitacao total, diario (aut)(mm)': 'precipitacao total diaria (mm)',
                        'temperatura media, diaria (aut)(°c)': 'temperatura media diaria (°C)',
                        'umidade relativa do ar, media diaria (aut)(%)': 'umidade relativa ar media diaria (%)',
                        'vento, velocidade media diaria (aut)(m/s)': 'velocidade vento media diaria (m/s)'
                    }
        df = df.rename(columns=lambda x: rename_map.get(x, x))
        df.drop(columns=['temperatura media diaria (°C)', 'umidade relativa ar media diaria (%)', 'velocidade vento media diaria (m/s)'], inplace=True)
    df['data medicao'] = pd.to_datetime(df['data medicao'], errors='coerce')
    df['ano civil'] = df['data medicao'].dt.year
    df['mês'] = df['data medicao'].dt.month
    df_spi = df.copy()
    df_spi.dropna(inplace=True)
    df_spi.reset_index(drop=True, inplace=True)
    df_spi = df_spi.groupby(['ano civil', 'mês'])['precipitacao total diaria (mm)'].sum().reset_index()
    df_spi.rename(columns={'precipitacao total diaria (mm)': 'precipitacao mensal (mm)'}, inplace=True)

    # Filtragem para eliminação de dados incompletos que prejudicam a análise estatística. Retirada do mês completo caso não exista na base
    df_final = []
    ano_inicial = cabecalho['data_inicial'].year
    ano_final = cabecalho['data_final'].year
    anos_existentes = list(range(ano_inicial, ano_final + 1))
    for ano in anos_existentes:
        df_ano = df[df['ano civil'] == ano]
        mes_unicos = df_ano['mês'].unique().tolist()
        for mes in mes_unicos:
            df_filtrado = df_ano[df_ano['mês'] == mes]
            tem_nan = df_filtrado['precipitacao total diaria (mm)'].isna().any()
            if tem_nan:
                pass
            else:
                df_final.append(df_filtrado)
    df_final = pd.concat(df_final)
    df_final.reset_index(drop=True, inplace=True)

    # Definição dos anos hidrológicos ou civis
    mensal, meses_secos, metodologia, inicio_hidrologico = definicao_ano_hidrologico(df_final)
    cabecalho['metodologia_ano'] = metodologia
    cabecalho['mes_inicio_ano_hidrologico'] = inicio_hidrologico
    # df_final.to_excel('dados_limpos_antes_ano_hidrologico.xlsx', index=False)

    # Marcação do ano hidrológico no DataFrame final
    if metodologia != "Ano hidrológico":
        anos = df_final['ano civil'].unique().tolist()
        for i, ano in enumerate(anos):
            mask = df_final['ano civil'] == ano
            df_final.loc[mask, 'ano hidrologico'] = int(i+1)
    else:
        df_final['ano hidrologico'] = np.where(df_final['mês'] >= inicio_hidrologico, df_final['ano civil'] + 1, df_final['ano civil'])
    anos = df_final['ano hidrologico'].unique().tolist()
    total_anos = len(anos)
    cabecalho['total_anos_em_dados'] = total_anos

    return cabecalho, mensal, meses_secos, df_final, df_spi


def calcular_spi_1(df_final: pd.DataFrame) -> pd.DataFrame:
    """Calcula o Standardized Precipitation Index (SPI-1) para a série mensal.

    :param df_final: Dados meteorológicos acumulados por mês ('ano civil', 'mês', 'precipitacao mensal (mm)')

    :return: O mesmo DataFrame com a nova coluna 'SPI_1' adicionada
    """
    
    col_precip = 'precipitacao mensal (mm)'

    # Cria a nova coluna 'SPI_1' vazia (NaN) para ser preenchida
    df_final['SPI_1'] = np.nan

    # O SPI precisa ser calculado comparando os mesmos meses de todos os anos
    for mes in range(1, 13):
        mask_mes = df_final['mês'] == mes
        dados_mes = df_final.loc[mask_mes, col_precip]

        # Se não houver dados para este mês, pula para o próximo
        if dados_mes.empty:
            continue

        # Fração de zeros (q) do dataset
        zeros = (dados_mes == 0).sum()
        positivos = dados_mes[dados_mes > 0]
        q = zeros / len(dados_mes)

        # Ajuste Gamma e CDF ajustada
        if len(positivos) > 1:
            a, loc, scale = sc.stats.gamma.fit(positivos, floc=0)
            cdf = sc.stats.gamma.cdf(dados_mes, a, loc=loc, scale=scale)
            cdf_adj = np.clip(q + (1 - q) * cdf, 1e-6, 1 - 1e-6)
            spi = sc.stats.norm.ppf(cdf_adj)
            df_final.loc[dados_mes.index, 'SPI_1'] = spi

    return df_final


def calcular_precipitacao_maxima_diaria(df_final: pd.DataFrame) -> pd.DataFrame:
    """Determina a precipitação máxima diária em função do ano hidrológico ou civil.

    :param df_final: Dados meteorológicos base BDMEP limpos ('data medicao', 'precipitacao total diaria (mm)', 'ano civil', 'mês', 'ano hidrologico')

    :return: Maiores precipitações diárias por ano hidrológico ou civil
    """

    # Limpeza e formatação dos dados
    df_final['precipitacao total diaria (mm)'] = pd.to_numeric(df_final['precipitacao total diaria (mm)'], errors='coerce')

    # Extração da média e desvio padrão das maiores precipitações anuais
    maiores_precipitacoes_por_ano = df_final.groupby('ano hidrologico')['precipitacao total diaria (mm)'].max().reset_index()
    maiores_precipitacoes_por_ano.rename(columns={'precipitacao total diaria (mm)': 'precipitacao máxima diária do ano (mm)'}, inplace=True)

    # Retirando valores zerados
    maiores_precipitacoes_por_ano = maiores_precipitacoes_por_ano[maiores_precipitacoes_por_ano['precipitacao máxima diária do ano (mm)'] > 0]
    maiores_precipitacoes_por_ano.reset_index(drop=True, inplace=True)

    return maiores_precipitacoes_por_ano


def checar_dis_adequada(maiores_precipitacoes_por_ano: pd.DataFrame) -> pd.DataFrame:
    """Checa os parâmetros de distribuições de probabilidade para as maiores precipitações diárias por ano hidrológico ou civil.

    :param maiores_precipitacoes_por_ano: Maiores precipitações diárias por ano hidrológico ou civil

    :return: [0] Resultados do teste de Kolmogorov-Smirnov para cada distribuição testada, ordenado pelo p-valor (maior para menor), [1] Parâmetros da melhor distribuição (maior p-valor), [2] Nome da melhor distribuição
    """

    tipo_dist = ['genextreme', 'gumbel_r', 'gumbel_l', 'norm', 'lognorm', 'weibull_min']
    teste_ks  = {"Tipo de Distribuição": [], "Nome Scipy": [], "Parâmetros": [], "p-valor": [], "Teste KS": []}
    for dist in tipo_dist:
        dados = maiores_precipitacoes_por_ano['precipitacao máxima diária do ano (mm)'].dropna().values
        x = dados[dados > 0]
        if dist == 'genextreme':
            dist_name = 'Generalized Extreme Value'
            params = sc.stats.genextreme.fit(x)
        elif dist == 'gumbel_r':
            dist_name = 'Gumbel Right'
            params = sc.stats.gumbel_r.fit(x)
        elif dist == 'gumbel_l':
            dist_name = 'Gumbel Left'
            params = sc.stats.gumbel_l.fit(x)
        elif dist == 'norm':
            dist_name = 'Normal'
            params = sc.stats.norm.fit(x)
        elif dist == 'lognorm':
            dist_name = 'Log-Normal'
            params = sc.stats.lognorm.fit(x)
        elif dist == 'weibull_min':
            dist_name = 'Weibull Minimum'
            params = sc.stats.weibull_min.fit(x)    
        else:   
            continue
        ks_stat, p_value = sc.stats.kstest(x, dist, args=params)
        teste_ks["Tipo de Distribuição"].append(dist_name)
        teste_ks["Nome Scipy"].append(dist)
        teste_ks["Parâmetros"].append(params)
        teste_ks["p-valor"].append(p_value)
        teste_ks["Teste KS"].append(ks_stat)
    teste_ks_df = pd.DataFrame(teste_ks)
    teste_ks_df = teste_ks_df.sort_values(by="p-valor", ascending=False).reset_index(drop=True)

    return teste_ks_df, teste_ks_df.loc[0, "Parâmetros"], teste_ks_df.loc[0, "Nome Scipy"]


def obter_cdf(x: list) -> tuple[list, list]:
    """Obter a função de distribuição acumulada (CDF) de uma lista de valores.

    :param x: valores de entrada para os quais a CDF deve ser calculada

    :return: [0] = valores ordenados eixo x, [1] = CDF dos valores de entrada eixo y
    """

    x_sorted = np.sort(x)
    x_cdf = np.arange(1, len(x_sorted) + 1) / len(x_sorted)

    return list(x_sorted), list(x_cdf)


def calcular_hmax(params: tuple, dist_tipo: str) -> pd.DataFrame:
    """Determina a preciptação máxima diária em função do período de retorno usando a melhor distribuição ajustada.
    
    :param params: Parâmetros da melhor distribuição ajustada (maior p-valor no teste de KS)
    :param dist_tipo: Nome da melhor distribuição ajustada (maior p-valor no teste de KS)

    :return: Precipitação máxima diária (mm) em função do período de retorno (anos)
    """
    
    Tr_list = [2, 5, 10, 15, 20, 25, 50, 100, 250, 500, 1000]
    p       = 1 - 1/np.array(Tr_list, dtype=float)
    p_exec  = 1/np.array(Tr_list, dtype=float)
    dist    = getattr(sc.stats, dist_tipo)
    x_Tr    = dist.ppf(p, *params)

    return pd.DataFrame({"t_r (anos)": Tr_list, "1/Tr": p_exec, "h_max,1 (mm)": x_Tr})


def desagragacao_preciptacao_maxima_diaria_matriz_intensidade_chuva(h_max1):
    """Desagregação da precipitação máxima diária (mm) em função do tempo de concentração (tc) em minutos e tempo de retorno (tr) em anos para matriz de intensidade de chuva (mm/h)

    :param h_max1: Precipitação máxima diária (mm) em função do período de retorno (anos).

    :return: Matriz de intensidade de chuva (mm/h) em função do tempo de concentração (tc) em minutos e tempo de retorno (tr) em anos.
    """

    tc_list    = [1440, 720, 600, 480, 360, 180, 60, 30, 25, 20, 15, 10, 5]
    tc_convert = [1.14, 0.85, 0.78, 0.72, 0.54, 0.48, 0.42, 0.74, 0.91, 0.81, 0.70, 0.54, 0.34]
    i_convert  = [1/24, 1/12, 1/8, 1/6, 1/3, 1/2, 1, 1 / (30/60), 1/(25/60), 1/(20/60), 1/(15/60), 1/(10/60), 1/(5/60)]
    tr = []
    tc = []
    y  = []
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
    matriz_intensidade = {'t_c (min)': tc, 't_r (anos)': tr, 'y_obs (mm/h)': y}

    return pd.DataFrame(matriz_intensidade)


def calculo_precipitacoes(df: pd.DataFrame, metadados: dict) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Processa dados de precipitação bruta para gerar preciptação máxima diária e precipitações em mm/h em diferentes períodos de retorno e tempos de concentração.

    :param df: Dados meteorológicos base BDMEP ('data medicao', 'precipitacao total diaria (mm)', 'ano civil', 'mês', 'ano hidrologico') 
    :param metadados: Metadados do arquivo de dados BDMEP (cidade, lat, long, alt, ..., etc)

    :return: saida[0] = Precipitação máxima diária (mm) em função do período de retorno (anos), saida[1] = Matriz de intensidade de chuva (mm/h) em função do tempo de concentração (tc) em minutos e tempo de retorno (tr) em anos.
    """

    # Limpeza e formatação dos dados
    df['precipitacao total diaria (mm)'] = pd.to_numeric(
        df['precipitacao total diaria (mm)'], errors='coerce')

    # Máximas anuais
    hmax1d = calcular_precipitacao_maxima_diaria(df)

    # Melhor distribuição
    _, params, nome_dist = checar_dis_adequada(hmax1d)

    # Altura máxima em 1 dia para diferentes períodos de retorno
    df_hmax1 = calcular_hmax(params, nome_dist)

    # Desagregação da precipitação máxima diária em matriz de intensidade de chuva (mm/h)
    matriz_chuva = desagragacao_preciptacao_maxima_diaria_matriz_intensidade_chuva(
        df_hmax1)
    matriz_chuva['latitude'] = metadados['latitude']
    matriz_chuva['longitude'] = metadados['longitude']
    matriz_chuva['altitude'] = metadados['altitude']
    matriz_chuva['cidade'] = metadados['nome']

    return df_hmax1, matriz_chuva


def plot_precipitacao_media_mensal(pasta_destino: str, nome: str,  mensal: pd.DataFrame, inicio_ano_chuvoso: int = 1, lang: str = 'pt') -> None:
    """Gera gráfico de precipitação média mensal em português ou inglês.

    :param pasta_destino: Pasta onde o gráfico será salvo
    :param nome: Nome da cidade e código da estação para nomeação do arquivo do gráfico
    :param lang: Idioma do gráfico ('pt' para português, 'en' para inglês)
    :param mensal: Médias mensais de precipitação
    :param inicio_ano_chuvoso: Mês de início do ano chuvoso
    """

    texto = {
                'pt': {
                            'xlabel': 'Mês',
                            'ylabel': 'Precipitação média mensal (mm)',
                            'mais_seco': 'Mês mais seco',
                            'mais_chuvoso': 'Mês mais chuvoso',
                            'inicio_chuva': 'Início do período chuvoso',
                            'arquivo': f'{nome}_pt.png'
                        },
                'en': {
                        'xlabel': 'Month',
                        'ylabel': 'Average precipitation (mm)',
                        'mais_seco': 'Driest month',
                        'mais_chuvoso': 'Wettest month',
                        'inicio_chuva': 'Start of rainy season',
                        'arquivo': f'{nome}_en.png'
                    }
            }

    # Configurações visuais
    width_cm  = 12
    height_cm = 10
    inches_per_cm = 1 / 2.54
    width_in    = width_cm * inches_per_cm
    height_in   = height_cm * inches_per_cm
    label_size  = 14
    axis_size   = 14
    legend_size = 10
    alpha       = 0.4

    # Plotagem do gráfico de precipitação média mensal
    plt.figure(figsize=(width_in, height_in))
    plt.plot(mensal['mês'], mensal['precipitacao media mensal (mm)'], marker='o', color='red')
    index_mais_seco = mensal['precipitacao media mensal (mm)'].idxmin()
    mes_mais_seco = index_mais_seco + 1
    plt.scatter(mes_mais_seco, mensal['precipitacao media mensal (mm)'][index_mais_seco], s=140, label=f"{texto[lang]['mais_seco']} = {mes_mais_seco}", color='blue')
    index_mais_chuvoso = mensal['precipitacao media mensal (mm)'].idxmax()
    mes_mais_chuvoso = index_mais_chuvoso + 1
    plt.scatter(mes_mais_chuvoso, mensal['precipitacao media mensal (mm)'][index_mais_chuvoso], s=140, label=f"{texto[lang]['mais_chuvoso']} = {mes_mais_chuvoso}", color='green')
    
    # Adicionar anotação com seta no inicio do período chuvoso
    plt.axvline(x=inicio_ano_chuvoso, color='purple', linestyle='--', linewidth=2.0, alpha=0.7, label=f"{texto[lang]['inicio_chuva']} = {inicio_ano_chuvoso}")
    plt.xlabel(texto[lang]['xlabel'], fontsize=label_size)
    plt.ylabel(texto[lang]['ylabel'], fontsize=label_size)
    plt.xticks(fontsize=axis_size)
    plt.yticks(fontsize=axis_size)
    plt.grid(True, alpha=alpha)
    plt.legend(fontsize=legend_size, loc='lower center', bbox_to_anchor=(0.5, 1.02), ncol=1, frameon=True)
    plt.tight_layout(rect=[0, 0, 1, 0.95])
    
    # Salvar
    plt.savefig(os.path.join(pasta_destino, f"z_medias_mensais_precipitacao_{nome}_{lang}.png"), dpi=600)
    plt.show()


def plot_pdf_precipitacao_maxima_diaria(pasta_destino: str, nome: str, data: dict, lang: str = 'pt') -> None:
    """Gera gráfico da PDF (KDE) da precipitação máxima diária em português ou inglês.

    :param pasta_destino: Pasta onde o gráfico será salvo
    :param nome: Nome da cidade/estação para nomeação do arquivo
    :param data: DataFrame contendo colunas 'x' (dados) e 'y' (distribuição)
    :param lang: Idioma do gráfico ('pt' ou 'en')
    """

    texto = {
                'pt': {
                            'ylabel': 'Densidade',
                            'xlabel': r'$i_{max,anual}$ (mm)',
                            'legenda': ['dados', 'melhor distribuição'],
                            'arquivo': f'{nome}_pt.png'
                        },
                'en': {
                            'ylabel': 'Density',
                            'xlabel': r'$i_{max,annual}$ (mm)',
                            'legenda': ['data', 'best distribution'],
                            'arquivo': f'{nome}_en.png'
                        }
            }

    # Configurações visuais
    width_cm  = 12
    height_cm = 10
    inches_per_cm = 1 / 2.54
    width_in    = width_cm * inches_per_cm
    height_in   = height_cm * inches_per_cm
    label_size  = 14
    axis_size   = 14
    legend_size = 10
    color_label = 'black'
    color_axis  = 'black'
    colors      = ['blue', 'red']
    alpha       = 0.4

    # Plotagem
    fig, ax = plt.subplots(figsize=(width_in, height_in))
    ax.tick_params(axis='both', which='major', labelsize=axis_size, colors=color_axis)
    ax.set_xlabel(texto[lang]['xlabel'], fontsize=label_size, color=color_label)
    ax.set_ylabel(texto[lang]['ylabel'], fontsize=label_size, color=color_label)
    plt.grid(True, which='both', linestyle='-', linewidth=0.2, alpha=alpha)
    sns.kdeplot(
                    data=data, x='real',
                    fill=True, alpha=alpha,
                    ax=ax, color=colors[0],
                    label=texto[lang]['legenda'][0]
                )
    sns.kdeplot(
                    data=data, x='numerica',
                    fill=True, alpha=alpha,
                    ax=ax, color=colors[1],
                    label=texto[lang]['legenda'][1]
                )
    plt.legend(
                fontsize=legend_size,
                loc='lower center',
                bbox_to_anchor=(0.5, 1.02),
                ncol=1,
                frameon=True
              )
    plt.tight_layout(rect=[0, 0, 1, 0.95])

    # Salvar
    fig.savefig(os.path.join(pasta_destino, texto[lang]['arquivo']), dpi=600, bbox_inches='tight')
    plt.show()


def plot_cdf_precipitacao_maxima_diaria(pasta_destino: str, nome: str, dados: dict, lang: str = 'pt') -> None:
    """Gera gráfico da CDF dos dados vs CDF Teórica da precipitação máxima diária anual.

    :param pasta_destino: Pasta onde o gráfico será salvo
    :param nome: Nome da cidade/estação
    :param dados: Série de máximas anuais (array ou lista)
    :param nome_dist: Nome da distribuição ajustada (string)
    :param params: Parâmetros da distribuição
    :param lang: 'pt' ou 'en'
    """

    texto = {
                'pt': {
                            'xlabel': r'$i_{max,anual}$ (mm)',
                            'ylabel': 'Probabilidade acumulada',
                            'legenda': ['dados', 'melhor distribuição'],
                            'arquivo': f'{nome}_pt.png'
                        },
                'en': {
                            'xlabel': r'$i_{max,annual}$ (mm)',
                            'ylabel': 'Cumulative probability',
                            'legenda': ['data', 'best distribution'],
                            'arquivo': f'{nome}_en.png'
                        }
            }

    # Configurações visuais
    width_cm  = 12
    height_cm = 10
    inches_per_cm = 1 / 2.54
    width_in    = width_cm * inches_per_cm
    height_in   = height_cm * inches_per_cm
    label_size  = 14
    axis_size   = 14
    legend_size = 10
    color_label = 'black'
    color_axis  = 'black'
    colors      = ['blue', 'red']
    alpha       = 0.4

    # Plot
    fig, ax = plt.subplots(figsize=(width_in, height_in))
    ax.scatter(dados['real']['x'], dados['real']['y'], label=texto[lang]['legenda'][0], color=colors[0], s=30)
    ax.plot(dados['numerica']['x'], dados['numerica']['y'], label=texto[lang]['legenda'][1], color=colors[1], linewidth=2)
    ax.set_xlabel(texto[lang]['xlabel'], fontsize=label_size, color=color_label)
    ax.set_ylabel(texto[lang]['ylabel'], fontsize=label_size, color=color_label)
    ax.tick_params(axis='both', which='major', labelsize=axis_size, colors=color_axis)
    plt.grid(True, linestyle='-', linewidth=0.2, alpha=alpha)
    plt.legend(fontsize=legend_size, loc='lower center', bbox_to_anchor=(0.5, 1.02), frameon=True)
    plt.tight_layout(rect=[0, 0, 1, 0.95])
    fig.savefig(os.path.join(pasta_destino, texto[lang]['arquivo']), dpi=600, bbox_inches='tight')
    plt.show()


def plot_curvas_idf(pasta_destino: str, nome: str, lang: str, matriz_chuva: pd.DataFrame) -> None:
    """Plota as curvas IDF (Intensidade x Duração).

    :param pasta_destino: Pasta onde o gráfico será salvo
    :param nome: Nome da estação/cidade
    :param lang: 'pt' ou 'en'
    :param matriz_chuva: DataFrame com:
                       índice = duração (min)
                       colunas = Tr (ex: 'Tr=2', 'Tr=10', etc.)
                       valores = intensidade (mm/h)
    """

    texto = {
                'pt': {
                            'x_label': 'Tempo de Duração (min)',
                            'y_label': 'Intensidade (mm/h)',
                            'titulo': 'Tempo de Retorno (anos)',
                            'arquivo': f'{nome}_pt.png'
                        },
                'en': {
                            'x_label': 'Duration Time (min)',
                            'y_label': 'Intensity (mm/h)',
                            'titulo': 'Return Period (years)',
                            'arquivo': f'{nome}_en.png'
                        }
            }


    # Configurações visuais
    width_cm  = 12
    height_cm = 10
    inches_per_cm = 1 / 2.54
    width_in    = width_cm * inches_per_cm
    height_in   = height_cm * inches_per_cm
    label_size  = 14
    axis_size   = 14
    legend_size = 10
    alpha       = 0.4
    t_r = [2, 5, 10, 15, 20, 25, 50, 100, 250, 500, 1000]

    # Plotagem do gráfico de precipitação média mensal
    fig, ax = plt.subplots(figsize=(width_in, height_in))
    for coluna in t_r:
        matriz_chuva_filtrada = matriz_chuva[matriz_chuva['t_r (anos)'] == coluna]
        ax.plot(matriz_chuva_filtrada['t_c (min)'], matriz_chuva_filtrada['y_obs (mm/h)'], linewidth=2.8, marker='o', label=coluna)
    ax.set_xlabel(texto[lang]['x_label'], fontsize=label_size)
    ax.set_ylabel(texto[lang]['y_label'], fontsize=label_size)
    ax.grid(True, which="both", linestyle="--", alpha=alpha)
    ax.legend(ncol=2, title=texto[lang]['titulo'], fontsize=legend_size)
    plt.tight_layout()
    fig.savefig(os.path.join(pasta_destino, texto[lang]['arquivo']), dpi=600, bbox_inches='tight')
    plt.show()

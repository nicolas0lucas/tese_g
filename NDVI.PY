!pip install rasterio -q
!pip install geopandas -q
!pip install matplotlib -q
!pip install geemap -q


import os
from google.colab import drive

# Solução completa para o problema de montagem
if os.path.exists('/content/drive'):
    # Remove todos os arquivos e o diretório se existir
    !rm -rf /content/drive
    !mkdir /content/drive

# Monta o Google Drive
drive.mount('/content/drive')

import os
import re
import numpy as np
import rasterio
import matplotlib.pyplot as plt
from rasterio.plot import show

def gerar_mapa_ndvi(
    caminho_imagem,       # caminho completo do GeoTIFF
    titulo_mapa,          # título do mapa: NDVI + período + ano
    pasta_saida,          # pasta onde salvar a figura
    cmap='viridis'        # colormap do matplotlib ou paleta personalizada
):
    """
    Lê a imagem NDVI, calcula estatísticas, desenha e salva uma figura
    com barra de cores (legenda), título e valores aproximados.
    """

    # Abre o arquivo raster
    with rasterio.open(caminho_imagem) as src:
        ndvi_array = src.read(1).astype(float)  # Lê a primeira banda

        # Substitui valores de NoData por np.nan (opcional, dependendo da exportação)
        ndvi_array[ndvi_array == src.nodata] = np.nan

        # Calcula estatísticas
        ndvi_min = np.nanmin(ndvi_array)
        ndvi_max = np.nanmax(ndvi_array)
        ndvi_mean = np.nanmean(ndvi_array)

        # Arredondar para 2 casas decimais
        ndvi_min_2dec = round(ndvi_min, 2)
        ndvi_max_2dec = round(ndvi_max, 2)
        ndvi_mean_2dec = round(ndvi_mean, 2)

        # Cria a figura e o eixo
        fig, ax = plt.subplots(figsize=(8, 6))

        # Plota o raster
        # Nota: `show()` do rasterio pode definir autoescala. Se quiser fixar min e max,
        # basta passar parâmetros como `vmin=..., vmax=...`.
        img_plot = ax.imshow(ndvi_array, cmap=cmap)

        # Adiciona a colorbar
        cbar = fig.colorbar(img_plot, ax=ax, shrink=0.7)
        cbar.set_label('NDVI', fontsize=12)

        # Título do mapa
        ax.set_title(f'{titulo_mapa}\n'
                     f'Min: {ndvi_min_2dec} | Max: {ndvi_max_2dec} | Mean: {ndvi_mean_2dec}',
                     fontsize=14)

        # Remove eixos (opcional)
        ax.axis('off')

        # Salva a figura na pasta de saída
        nome_arquivo_fig = os.path.join(pasta_saida, f'{titulo_mapa}.png')
        plt.savefig(nome_arquivo_fig, dpi=150, bbox_inches='tight')
        plt.close(fig)  # Fecha a figura para liberar memória


import matplotlib.colors as mcolors

# Paleta NDVI do GEE (exemplo resumido)
ndvi_colors = [
    '#FFFFFF', '#CE7E45', '#DF923D', '#F1B555', '#FCD163',
    '#99B718', '#74A901', '#66A000', '#529400', '#3E8601',
    '#207401', '#056201', '#004C00', '#023B01', '#012E01',
    '#011D01', '#011301'
]

ndvi_cmap = mcolors.LinearSegmentedColormap.from_list("NDVI_GEE", ndvi_colors)

# Então na função gerar_mapa_ndvi, passe cmap=ndvi_cmap


# Caminho da pasta onde estão os GeoTIFFs exportados
pasta_imagens = '/content/drive/MyDrive/GEE_Exports'

# Pasta para salvar as figuras (pode ser a mesma, mas aqui separado):
pasta_saida_figs = '/content/drive/MyDrive/GEE_Maps'
os.makedirs(pasta_saida_figs, exist_ok=True)

# Regex simples para capturar dados do nome do arquivo (ex: NDVI_Seco_Area1_2010.tif)
padrao = re.compile(r'(NDVI)_(Seco|Umido)_(Area\d)_(\d{4})\.tif')

# Listar arquivos na pasta de imagens
arquivos = [f for f in os.listdir(pasta_imagens) if f.endswith('.tif')]

for arq in arquivos:
    # Tenta extrair informações do nome do arquivo via regex
    match = padrao.match(arq)
    if match:
        # match.groups() -> ('NDVI', 'Seco', 'Area1', '2010')
        ndvi_str, periodo, area, ano = match.groups()

        # Monta o título
        # Exemplo: NDVI Seco 2010 (Area1) - ajuste conforme desejar
        titulo_map = f"{ndvi_str} {periodo} {ano} ({area})"

        # Caminho completo do GeoTIFF
        caminho_arquivo = os.path.join(pasta_imagens, arq)

        # Gera o mapa e salva
        gerar_mapa_ndvi(caminho_arquivo, titulo_map, pasta_saida_figs, cmap='viridis')

        print(f"Gerado mapa: {titulo_map}")
    else:
        print(f"Nome de arquivo fora do padrão: {arq}")



def gerar_mapa_ndvi_com_percentil(
    caminho_imagem,
    titulo_mapa,
    pasta_saida,
    cmap=ndvi_cmap,
    pmin=2,   # percentil mínimo
    pmax=98   # percentil máximo
):
    """
    Lê a imagem NDVI (escalada em 10.000), converte para [-1, +1],
    usa percentis para definir min/max de plotagem,
    calcula estatísticas (min, max, mean) e gera mapa com barra de cores.
    """

    with rasterio.open(caminho_imagem) as src:
        ndvi_array = src.read(1).astype(float)

        # Trata valores nodata
        if src.nodata is not None:
            ndvi_array[ndvi_array == src.nodata] = np.nan

        # Converte para escala real NDVI
        ndvi_array = ndvi_array * 0.0001  # ex.: 6200 -> 0.62

        # Calcula estatísticas gerais (sem recorte)
        ndvi_min = np.nanmin(ndvi_array)
        ndvi_max = np.nanmax(ndvi_array)
        ndvi_mean = np.nanmean(ndvi_array)

        # Arredondando p/ 2 casas decimais
        ndvi_min_2dec = round(ndvi_min, 2)
        ndvi_max_2dec = round(ndvi_max, 2)
        ndvi_mean_2dec = round(ndvi_mean, 2)

        # Calcula percentis para realçar a variação de cor
        arr_sem_nan = ndvi_array[~np.isnan(ndvi_array)]
        vmin_dyn = np.percentile(arr_sem_nan, pmin)
        vmax_dyn = np.percentile(arr_sem_nan, pmax)

        # Cria a figura
        fig, ax = plt.subplots(figsize=(8, 6))

        # Plota usando [vmin_dyn, vmax_dyn] p/ ganhar contraste
        img_plot = ax.imshow(ndvi_array, cmap=cmap, vmin=vmin_dyn, vmax=vmax_dyn)

        # Colorbar
        cbar = fig.colorbar(img_plot, ax=ax, shrink=0.7)
        cbar.set_label('NDVI', fontsize=12)

        # Título com estatísticas
        ax.set_title(
            f'{titulo_mapa}\n'
            f'Min: {ndvi_min_2dec} | Max: {ndvi_max_2dec} | Mean: {ndvi_mean_2dec}',
            fontsize=14
        )

        ax.axis('off')

        # Salva figura
        nome_arquivo_fig = os.path.join(pasta_saida, f'{titulo_mapa}.png')
        plt.savefig(nome_arquivo_fig, dpi=150, bbox_inches='tight')
        plt.close(fig)


# Paleta NDVI parecida com a do GEE
ndvi_colors = [
    '#FFFFFF', '#CE7E45', '#DF923D', '#F1B555', '#FCD163',
    '#99B718', '#74A901', '#66A000', '#529400', '#3E8601',
    '#207401', '#056201', '#004C00', '#023B01', '#012E01',
    '#011D01', '#011301'
]

ndvi_cmap = mcolors.LinearSegmentedColormap.from_list("NDVI_GEE", ndvi_colors)

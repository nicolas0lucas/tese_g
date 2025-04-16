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

# 2. Função para gerar mapas
def gerar_mapa_evi(caminho_imagem, pasta_saida, cmap=evi_cmap, pmin=2, pmax=98):
    """Gera mapa EVI a partir de qualquer arquivo .tif"""
    try:
        with rasterio.open(caminho_imagem) as src:
            evi = src.read(1)
            evi = np.ma.masked_where(evi == src.nodata, evi)

            if evi.compressed().size == 0:
                print(f"⚠ Arquivo sem dados válidos: {os.path.basename(caminho_imagem)}")
                return

            # Cálculo automático da escala
            vmin = np.percentile(evi.compressed(), pmin)
            vmax = np.percentile(evi.compressed(), pmax)

            # Configuração do plot
            plt.figure(figsize=(10, 10))
            img = plt.imshow(evi, cmap=cmap, vmin=vmin, vmax=vmax)

            # Título baseado no nome do arquivo
            nome_arquivo = os.path.basename(caminho_imagem)
            plt.title(f"EVI {os.path.splitext(nome_arquivo)[0]}", fontsize=14, pad=20)
            plt.axis('off')

            # Barra de cores
            cbar = plt.colorbar(fraction=0.046, pad=0.04)
            cbar.set_label('Índice EVI', rotation=270, labelpad=20)

            # Salvar figura
            nome_saida = os.path.splitext(nome_arquivo)[0] + '.png'
            caminho_completo = os.path.join(pasta_saida, nome_saida)
            plt.savefig(caminho_completo, bbox_inches='tight', dpi=300)
            plt.close()

            print(f"✔ Mapa gerado: {nome_saida}")

    except Exception as e:
        print(f"✖ Erro ao processar {os.path.basename(caminho_imagem)}: {str(e)}")

# 3. Configuração de diretórios
pasta_imagens = '/content/drive/MyDrive/MODIS_EVI'
pasta_saida = '/content/drive/MyDrive/GEE_Maps_EVI'
os.makedirs(pasta_saida, exist_ok=True)

# 4. Processamento de todos os arquivos .tif
print("Iniciando processamento de arquivos...")
arquivos_processados = 0

for arquivo in sorted(os.listdir(pasta_imagens)):
    if arquivo.lower().endswith('.tif'):
        caminho_completo = os.path.join(pasta_imagens, arquivo)
        gerar_mapa_evi(caminho_completo, pasta_saida)
        arquivos_processados += 1

# 5. Relatório final
print("\n" + "="*50)
print(f"Processamento concluído!")
print(f"Total de arquivos processados: {arquivos_processados}")
print(f"Mapas salvos em: {pasta_saida}")
print("="*50)

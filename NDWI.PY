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

import os
import numpy as np
import matplotlib.pyplot as plt
import rasterio
from rasterio.plot import show
from matplotlib_scalebar.scalebar import ScaleBar

# 1. Configuração da paleta de cores para NDWI (corrigida)
ndwi_cmap = plt.cm.Blues_r  # Paleta azul invertida (mais escura = maior NDWI)
plt.style.use('seaborn-v0_8-whitegrid')  # Estilo moderno para os gráficos

# 2. Função para gerar mapas NDWI (versão robusta)
def gerar_mapa_ndwi(caminho_imagem, pasta_saida, cmap=ndwi_cmap, pmin=2, pmax=98):
    """Gera mapa NDWI a partir de arquivos .tif com tratamento de erros completo"""
    try:
        # Verifica se o arquivo existe
        if not os.path.exists(caminho_imagem):
            print(f"✖ Arquivo não encontrado: {os.path.basename(caminho_imagem)}")
            return

        with rasterio.open(caminho_imagem) as src:
            ndwi = src.read(1)

            # Cria máscara para valores nodata
            ndwi = np.ma.masked_where(
                (ndwi == src.nodata) | (ndwi < -1) | (ndwi > 1),  # Filtra valores inválidos
                ndwi
            )

            # Verifica se há dados válidos
            if ndwi.compressed().size == 0:
                print(f"⚠ Arquivo sem dados válidos: {os.path.basename(caminho_imagem)}")
                return

            # Cálculo automático da escala (com limites para NDWI)
            vmin = max(-1, np.percentile(ndwi.compressed(), pmin))
            vmax = min(1, np.percentile(ndwi.compressed(), pmax))

            # Configuração do plot
            fig, ax = plt.subplots(figsize=(10, 10), dpi=120)
            img = ax.imshow(ndwi, cmap=cmap, vmin=vmin, vmax=vmax)

            # Título baseado no nome do arquivo
            nome_arquivo = os.path.basename(caminho_imagem)
            titulo = nome_arquivo.replace('NDWI_', '').replace('_', ' ').replace('.tif', '')
            ax.set_title(f"NDWI {titulo}", fontsize=14, pad=20)
            ax.axis('off')

            # Barra de cores
            cbar = plt.colorbar(img, fraction=0.046, pad=0.04)
            cbar.set_label('Índice NDWI', rotation=270, labelpad=20)

            # Adiciona escala (opcional)
            try:
                dx = src.res[0]
                ax.add_artist(ScaleBar(dx, units="m", location='lower left'))
            except:
                pass

            # Salvar figura
            nome_saida = f"NDWI_{titulo.replace(' ', '_')}.png"
            caminho_completo = os.path.join(pasta_saida, nome_saida)
            plt.savefig(caminho_completo, bbox_inches='tight', dpi=300)
            plt.close()

            print(f"✔ Mapa gerado: {nome_saida}")

    except Exception as e:
        print(f"✖ Erro ao processar {os.path.basename(caminho_imagem)}: {str(e)}")

# 3. Configuração de diretórios (ajuste seus caminhos)
pasta_imagens = '/content/drive/MyDrive/MODIS_NDWI'
pasta_saida = '/content/drive/MyDrive/MAPS_NDWI'
os.makedirs(pasta_saida, exist_ok=True)

# 4. Processamento de todos os arquivos .tif
print("Iniciando processamento de arquivos NDWI...")
arquivos_processados = 0

for arquivo in sorted(os.listdir(pasta_imagens)):
    if arquivo.lower().endswith('.tif'):
        caminho_completo = os.path.join(pasta_imagens, arquivo)
        gerar_mapa_ndwi(caminho_completo, pasta_saida)
        arquivos_processados += 1

# 5. Relatório final
print("\n" + "="*50)
print(f"Processamento concluído!")
print(f"Total de arquivos processados: {arquivos_processados}")
print(f"Mapas salvos em: {pasta_saida}")
print("="*50)


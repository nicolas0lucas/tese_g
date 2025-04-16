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

# 1. Configuração da paleta de cores para LAI
lai_cmap = plt.cm.YlGn  # Paleta verde-amarela para LAI
plt.style.use('seaborn-v0_8-whitegrid')  # Estilo moderno para os gráficos

# 2. Função para gerar mapas LAI (versão robusta)
def gerar_mapa_lai(caminho_imagem, pasta_saida, cmap=lai_cmap, pmin=2, pmax=98):
    """Gera mapa LAI a partir de arquivos .tif com tratamento de erros completo"""
    try:
        # Verifica se o arquivo existe
        if not os.path.exists(caminho_imagem):
            print(f"✖ Arquivo não encontrado: {os.path.basename(caminho_imagem)}")
            return

        with rasterio.open(caminho_imagem) as src:
            lai = src.read(1)

            # Cria máscara para valores nodata
            lai = np.ma.masked_where(
                (lai == src.nodata) | (lai < 0) | (lai > 10),  # Filtra valores inválidos (LAI típico 0-10)
                lai
            )

            # Verifica se há dados válidos
            if lai.compressed().size == 0:
                print(f"⚠ Arquivo sem dados válidos: {os.path.basename(caminho_imagem)}")
                return

            # Cálculo automático da escala (com limites para LAI)
            vmin = max(0, np.percentile(lai.compressed(), pmin))
            vmax = min(10, np.percentile(lai.compressed(), pmax))

            # Configuração do plot
            fig, ax = plt.subplots(figsize=(10, 10), dpi=120)
            img = ax.imshow(lai, cmap=cmap, vmin=vmin, vmax=vmax)

            # Título baseado no nome do arquivo
            nome_arquivo = os.path.basename(caminho_imagem)
            titulo = nome_arquivo.replace('LAI_', '').replace('_', ' ').replace('.tif', '')
            ax.set_title(f"LAI {titulo}", fontsize=14, pad=20)
            ax.axis('off')

            # Barra de cores
            cbar = plt.colorbar(img, fraction=0.046, pad=0.04)
            cbar.set_label('Leaf Area Index (m²/m²)', rotation=270, labelpad=20)

            # Adiciona escala (opcional)
            try:
                dx = src.res[0]
                ax.add_artist(ScaleBar(dx, units="m", location='lower left'))
            except:
                pass

            # Salvar figura
            nome_saida = f"LAI_{titulo.replace(' ', '_')}.png"
            caminho_completo = os.path.join(pasta_saida, nome_saida)
            plt.savefig(caminho_completo, bbox_inches='tight', dpi=300)
            plt.close()

            print(f"✔ Mapa gerado: {nome_saida}")

    except Exception as e:
        print(f"✖ Erro ao processar {os.path.basename(caminho_imagem)}: {str(e)}")

# 3. Configuração de diretórios (ajuste seus caminhos)
pasta_imagens = '/content/drive/MyDrive/MODIS_LAI'  # Pasta onde estão os arquivos LAI
pasta_saida = '/content/drive/MyDrive/MAPS_LAI'    # Pasta para salvar os mapas
os.makedirs(pasta_saida, exist_ok=True)

# 4. Processamento de todos os arquivos .tif
print("Iniciando processamento de arquivos LAI...")
arquivos_processados = 0

for arquivo in sorted(os.listdir(pasta_imagens)):
    if arquivo.lower().endswith('.tif'):
        caminho_completo = os.path.join(pasta_imagens, arquivo)
        gerar_mapa_lai(caminho_completo, pasta_saida)
        arquivos_processados += 1

# 5. Relatório final
print("\n" + "="*50)
print(f"Processamento concluído!")
print(f"Total de arquivos processados: {arquivos_processados}")
print(f"Mapas salvos em: {pasta_saida}")
print("="*50)

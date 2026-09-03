import csv
import re
import matplotlib.pyplot as plt
from collections import defaultdict
import os
import numpy as np

# =========================================================
# CONFIGURAÇÕES
# =========================================================

INPUT_CSV = "summary.csv"
PLOT_DIR = "./plots"
os.makedirs(PLOT_DIR, exist_ok=True)

# Lista de tipos que você deseja QUE APAREÇAM no gráfico
# Se remover um item daqui, ele será ignorado no processamento
TYPES = ["rca", "loa", "heaa", "hoeraa", "herloa"]

# =========================================================
# Funções auxiliares
# =========================================================

def classify(exp_name):
    """
    Extrai tipo e número de bits automaticamente.
    Retorna (None, 0) se o tipo não estiver na lista TYPES.
    """
    exp_name = exp_name.lower()

    tipo = None
    for t in TYPES:
        # Busca a palavra exata do tipo para evitar conflitos (ex: csa vs cska)
        if re.search(rf"\b{t}\b", exp_name) or t in exp_name:
            tipo = t
            break

    # Se não for um dos tipos suportados, retorna None para ser filtrado
    if tipo is None:
        return None, 0

    bits_match = re.search(r"(\d+)bit", exp_name)
    bits = int(bits_match.group(1)) if bits_match else 0

    return tipo, bits


def plot_bar(data_dict, metric_key, y_label, title, filename):
    """
    Gera gráfico de barras dinâmico baseado nos dados filtrados
    """
    if not data_dict:
        print(f"Aviso: Nenhum dado para plotar {filename}")
        return

    #plt.figure(figsize=(10, 6))
    plt.rcParams["figure.figsize"] = (8, 5)

    # Set default DPI for all subsequent saved figures
    plt.rcParams["savefig.dpi"] = 300
    # Specific font sizes for elements
    plt.rc('axes', titlesize=16, labelsize=14)   # Titles and labels
    plt.rc('xtick', labelsize=10)                # x-tick labels
    plt.rc('legend', fontsize=12)                # Legend

    # Tipos presentes no dataset (apenas os que passaram no filtro)
    tipos = sorted(data_dict.keys())

    # Bits disponíveis no dataset
    bit_sizes = sorted({b for t in data_dict for b in data_dict[t]})

    x = np.arange(len(bit_sizes))
    n = len(tipos)
    width = 0.8 / n  

    for i, tipo in enumerate(tipos):
        vals = [data_dict[tipo].get(b, {}).get(metric_key, 0) for b in bit_sizes]
        offset = (i - n/2) * width + width/2
        plt.bar(x + offset, vals, width=width, label=tipo.upper())

    plt.xticks(x, [f"{b}-bit" for b in bit_sizes])
    plt.ylabel(y_label)
    plt.title(title)
    plt.legend(loc='upper right', bbox_to_anchor=(1.2, 1.0),
          ncol=1)
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()

    filepath = os.path.join(PLOT_DIR, filename)
    plt.savefig(filepath, bbox_inches='tight')
    plt.close()
    print(f"Plot gerado: {filepath}")


# =========================================================
# Leitura e organização
# =========================================================

data = defaultdict(lambda: defaultdict(dict))

if not os.path.exists(INPUT_CSV):
    print(f"Erro: Arquivo {INPUT_CSV} não encontrado.")
    exit()

with open(INPUT_CSV, "r") as f:
    reader = csv.DictReader(f)

    for row in reader:
        exp = row["experiment"]
        tipo, bits = classify(exp)

        # FILTRO CRÍTICO: Se o tipo for None, ignora a linha completamente
        if tipo is None:
            continue
            
        try:
            # Converte valores do CSV garantindo que são números
            lut   = int(row["Slice LUTs"])
            reg   = int(row["Slice Registers"])
            dyn   = float(row["Dynamic Power (W)"])
            sta   = float(row["Static Power (W)"])
            total = dyn + sta

            data[tipo][bits] = {
                "lut": lut,
                "reg": reg,
                "dynamic": dyn,
                "static": sta,
                "total": total
            }
        except (ValueError, KeyError) as e:
            print(f"Erro ao processar linha do experimento {exp}: {e}")

# =========================================================
# Eficiência energética
# =========================================================

for tipo in data:
    for b in data[tipo]:
        # Watts por bit
        data[tipo][b]["efficiency"] = data[tipo][b]["total"] / b if b != 0 else 0

# =========================================================
# GERAÇÃO DOS GRÁFICOS
# =========================================================

# Só tenta plotar se houver dados
if data:
    plot_bar(data, "total", "Power (W)", "Total Power Comparison", "power_total.pdf")
    plot_bar(data, "dynamic", "Power (W)", "Dynamic Power Comparison", "power_dynamic.pdf")
    plot_bar(data, "static", "Power (W)", "Static Power Comparison", "power_static.pdf")
    plot_bar(data, "lut", "Slice LUTs", "LUT Usage Comparison", "lut_comparison.pdf")
    plot_bar(data, "reg", "Slice Registers", "Register Usage Comparison", "register_comparison.pdf")
    plot_bar(data, "efficiency", "Power per bit (W/bit)", "Energy Efficiency", "efficiency.pdf")
    print(f"\nSucesso! Todos os gráficos foram salvos em: {os.path.abspath(PLOT_DIR)}")
else:
    print("Nenhum dado válido encontrado para gerar gráficos. Verifique a lista TYPES e o CSV.")

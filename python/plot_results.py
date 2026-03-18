import csv
import re
import matplotlib.pyplot as plt
from collections import defaultdict
import os

# =========================================================
# CONFIGURAÇÕES
# =========================================================

INPUT_CSV = "summary.csv"
PLOT_DIR = "./plots"
os.makedirs(PLOT_DIR, exist_ok=True)

# =========================================================
# Funções auxiliares
# =========================================================

def classify(exp_name):
    """
    Extrai:
    - tipo: adder / cla
    - bits: 8 / 16 / 32
    """
    tipo = "adder" if "adder" in exp_name else "cla"
    bits_match = re.search(r"(\d+)bit", exp_name)
    bits = int(bits_match.group(1)) if bits_match else 0
    return tipo, bits

def plot_bar(data_dict, metric_key, y_label, title, filename):
    """Gera gráfico de barras comparando adder e cla por largura de bit"""
    plt.figure()
    bit_sizes = sorted({b for t in data_dict for b in data_dict[t]})
    x = range(len(bit_sizes))
    width = 0.35

    adder_vals = [data_dict["adder"].get(b, {}).get(metric_key, 0) for b in bit_sizes]
    cla_vals   = [data_dict["cla"].get(b, {}).get(metric_key, 0) for b in bit_sizes]

    plt.bar([i - width/2 for i in x], adder_vals, width=width, label="Adder")
    plt.bar([i + width/2 for i in x], cla_vals, width=width, label="CLA")

    plt.xticks(x, [f"{b}-bit" for b in bit_sizes])
    plt.ylabel(y_label)
    plt.title(title)
    plt.legend()
    plt.tight_layout()
    filepath = os.path.join(PLOT_DIR, filename)
    plt.savefig(filepath)
    plt.close()
    print(f"Plot gerado: {filepath}")

# =========================================================
# Leitura e organização
# =========================================================

data = defaultdict(lambda: defaultdict(dict))
# data[tipo][bits] = {metrics}

with open(INPUT_CSV, "r") as f:
    reader = csv.DictReader(f)
    for row in reader:
        exp = row["experiment"]
        tipo, bits = classify(exp)

        lut = int(row["Slice LUTs"])
        reg = int(row["Slice Registers"])
        dyn = float(row["Dynamic Power (W)"])
        sta = float(row["Static Power (W)"])
        total = dyn + sta

        data[tipo][bits] = {
            "lut": lut,
            "reg": reg,
            "dynamic": dyn,
            "static": sta,
            "total": total
        }

# =========================================================
# GRÁFICOS DE ENERGIA
# =========================================================

plot_bar(data, "total", "Power (W)", "Total Power Comparison", "power_total.pdf")
plot_bar(data, "dynamic", "Power (W)", "Dynamic Power Comparison", "power_dynamic.pdf")
plot_bar(data, "static", "Power (W)", "Static Power Comparison", "power_static.pdf")

# =========================================================
# GRÁFICOS DE LUTs, Registers e Eficiência
# =========================================================

plot_bar(data, "lut", "Slice LUTs", "LUT Usage Comparison", "lut_comparison.pdf")
plot_bar(data, "reg", "Slice Registers", "Register Usage Comparison", "register_comparison.pdf")

# Eficiência energética (W/bit)
for tipo in data:
    for b in data[tipo]:
        data[tipo][b]["efficiency"] = data[tipo][b]["total"] / b if b != 0 else 0

plot_bar(data, "efficiency", "Power per bit (W/bit)", "Energy Efficiency", "efficiency.pdf")

print("Todos os gráficos gerados na pasta ./plots")

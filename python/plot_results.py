import os
import csv
import re
import numpy as np
import matplotlib.pyplot as plt
from collections import defaultdict

# =========================================================
# CONFIGURACOES
# =========================================================

SUMMARY_CSV = "summary.csv"
ERROR_CSV = "error_metrics_summary.csv"
PLOT_DIR = "./plots"
os.makedirs(PLOT_DIR, exist_ok=True)

# Tipos oficiais na ordem do TCC
TYPES = ["rca", "loa", "heaa", "hoeraa", "herloa"]
APPROX_TYPES = ["loa", "heaa", "hoeraa", "herloa"]

# Mapeamento FIXO e IMUTAVEL de cores por somador para todos os graficos
# (Cores oficiais da paleta tab10, sem rosa e com identidade visual unica)
ARCH_COLORS = {
    "rca":    "#1f77b4",  # Azul
    "loa":    "#ff7f0e",  # Laranja
    "heaa":   "#2ca02c",  # Verde
    "hoeraa": "#d62728",  # Vermelho
    "herloa": "#9467bd"   # Roxo
}

# =========================================================
# FUNCOES DE PLOTAGEM COM LEGENDA EXTERNA E CORES FIXAS
# =========================================================

def plot_bar(data_dict, types_list, metric_key, y_label, title, filename, yscale=None):
    """
    Gera grafico de barras com cores fixas e legenda externa a direita
    """
    if not data_dict:
        print(f"Aviso: Nenhum dado para plotar {filename}")
        return

    plt.rcParams["figure.figsize"] = (8.5, 5)
    plt.rcParams["savefig.dpi"] = 300
    plt.rc('axes', titlesize=16, labelsize=14)
    plt.rc('xtick', labelsize=11)
    plt.rc('ytick', labelsize=11)
    plt.rc('legend', fontsize=12)

    tipos = [t for t in types_list if t in data_dict]
    bit_sizes = sorted({b for t in tipos for b in data_dict[t]})

    x = np.arange(len(bit_sizes))
    n = len(tipos)
    width = 0.8 / n

    fig, ax = plt.subplots()

    for i, tipo in enumerate(tipos):
        vals = [data_dict[tipo].get(b, {}).get(metric_key, 0) for b in bit_sizes]
        offset = (i - n/2) * width + width/2
        color = ARCH_COLORS.get(tipo.lower())
        ax.bar(x + offset, vals, width=width, label=tipo.upper(), color=color)

    ax.set_xticks(x)
    ax.set_xticklabels([f"{b}-bit" for b in bit_sizes])
    ax.set_ylabel(y_label)
    ax.set_title(title)
    if yscale:
        ax.set_yscale(yscale)

    ax.legend(loc='upper left', bbox_to_anchor=(1.02, 1.0), borderaxespad=0)
    ax.grid(axis='y', linestyle='--', alpha=0.7)

    filepath = os.path.join(PLOT_DIR, filename)
    plt.savefig(filepath, bbox_inches='tight')
    plt.close(fig)
    print(f"Plot gerado: {filepath}")


def plot_bar_dists(err_dict, types_list, bits, metric_key, y_label, title, filename, yscale=None):
    """
    Gera grafico de barras por distribuicao com cores fixas e legenda externa a direita
    """
    plt.rcParams["figure.figsize"] = (8.5, 5)
    plt.rcParams["savefig.dpi"] = 300
    plt.rc('axes', titlesize=16, labelsize=14)
    plt.rc('xtick', labelsize=11)
    plt.rc('ytick', labelsize=11)
    plt.rc('legend', fontsize=12)

    dists = ["uniform", "normal", "exponential"]
    dist_labels = ["Uniform", "Normal", "Exponential"]
    tipos = [t for t in types_list if t in err_dict]

    x = np.arange(len(dists))
    n = len(tipos)
    width = 0.8 / n

    fig, ax = plt.subplots()

    for i, tipo in enumerate(tipos):
        vals = [err_dict[tipo].get(bits, {}).get(d, {}).get(metric_key, 0) for d in dists]
        offset = (i - n/2) * width + width/2
        color = ARCH_COLORS.get(tipo.lower())
        ax.bar(x + offset, vals, width=width, label=tipo.upper(), color=color)

    ax.set_xticks(x)
    ax.set_xticklabels(dist_labels)
    ax.set_ylabel(y_label)
    ax.set_title(title)
    if yscale:
        ax.set_yscale(yscale)

    ax.legend(loc='upper left', bbox_to_anchor=(1.02, 1.0), borderaxespad=0)
    ax.grid(axis='y', linestyle='--', alpha=0.7)

    filepath = os.path.join(PLOT_DIR, filename)
    plt.savefig(filepath, bbox_inches='tight')
    plt.close(fig)
    print(f"Plot gerado: {filepath}")


# =========================================================
# LEITURA E PROCESSAMENTO DOS DADOS DE HARDWARE
# =========================================================

def load_hardware_data():
    data = defaultdict(lambda: defaultdict(dict))
    power_samples = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))

    if not os.path.exists(SUMMARY_CSV):
        print(f"Erro: Arquivo {SUMMARY_CSV} nao encontrado.")
        return data

    with open(SUMMARY_CSV, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            arch = row["architecture"].lower()
            if arch not in TYPES:
                continue

            bits = int(row["bits"])
            lut = int(row["Slice LUTs"]) if row["Slice LUTs"] else 0
            reg = int(row["Slice Registers"]) if row["Slice Registers"] else 0
            dyn = float(row["Dynamic Power (W)"]) if row["Dynamic Power (W)"] else 0.0
            sta = float(row["Static Power (W)"]) if row["Static Power (W)"] else 0.0
            tot = float(row["Total Power (W)"]) if row["Total Power (W)"] else (dyn + sta)

            data[arch][bits]["lut"] = lut
            data[arch][bits]["reg"] = reg
            power_samples[arch][bits]["dynamic"].append(dyn)
            power_samples[arch][bits]["static"].append(sta)
            power_samples[arch][bits]["total"].append(tot)

    for arch in data:
        for bits in data[arch]:
            dyn_mean = np.mean(power_samples[arch][bits]["dynamic"])
            sta_mean = np.mean(power_samples[arch][bits]["static"])
            tot_mean = np.mean(power_samples[arch][bits]["total"])

            data[arch][bits]["dynamic"] = dyn_mean
            data[arch][bits]["static"] = sta_mean
            data[arch][bits]["total"] = tot_mean
            data[arch][bits]["efficiency"] = tot_mean / bits if bits != 0 else 0

    return data


# =========================================================
# LEITURA E PROCESSAMENTO DOS DADOS DE ERRO
# =========================================================

def load_error_data():
    err_by_bit = defaultdict(lambda: defaultdict(dict))
    err_by_dist = defaultdict(lambda: defaultdict(lambda: defaultdict(dict)))

    if not os.path.exists(ERROR_CSV):
        print(f"Erro: Arquivo {ERROR_CSV} nao encontrado.")
        return err_by_bit, err_by_dist

    samples_by_bit = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))

    with open(ERROR_CSV, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            arch = row["architecture"].lower()
            if arch not in TYPES:
                continue

            bits = int(row["bits"])
            dist = row["distribution"].lower()

            mae = float(row["MAE"])
            mse = float(row["MSE"])
            ep  = float(row["EP"]) * 100
            mre = float(row["MRE"]) * 100

            err_by_dist[arch][bits][dist] = {
                "mae": mae,
                "mse": mse,
                "ep": ep,
                "mre": mre
            }

            samples_by_bit[arch][bits]["mae"].append(mae)
            samples_by_bit[arch][bits]["mse"].append(mse)
            samples_by_bit[arch][bits]["ep"].append(ep)
            samples_by_bit[arch][bits]["mre"].append(mre)

    for arch in samples_by_bit:
        for bits in samples_by_bit[arch]:
            err_by_bit[arch][bits] = {
                "mae": np.mean(samples_by_bit[arch][bits]["mae"]),
                "mse": np.mean(samples_by_bit[arch][bits]["mse"]),
                "ep":  np.mean(samples_by_bit[arch][bits]["ep"]),
                "mre": np.mean(samples_by_bit[arch][bits]["mre"])
            }

    return err_by_bit, err_by_dist


# =========================================================
# EXECUCAO PRINCIPAL
# =========================================================

def main():
    print("Regenerando graficos com cores estritamente padronizadas por somador...")

    hw_data = load_hardware_data()
    err_by_bit, err_by_dist = load_error_data()

    # 1. Graficos de Hardware (RCA, LOA, HEAA, HOERAA, HERLOA)
    if hw_data:
        plot_bar(hw_data, TYPES, "total", "Power (W)", "Total Power Comparison", "power_total.pdf")
        plot_bar(hw_data, TYPES, "dynamic", "Power (W)", "Dynamic Power Comparison", "power_dynamic.pdf")
        plot_bar(hw_data, TYPES, "static", "Power (W)", "Static Power Comparison", "power_static.pdf")
        plot_bar(hw_data, TYPES, "lut", "Slice LUTs", "LUT Usage Comparison", "lut_comparison.pdf")
        plot_bar(hw_data, TYPES, "reg", "Slice Registers", "Register Usage Comparison", "register_comparison.pdf")
        plot_bar(hw_data, TYPES, "efficiency", "Power per bit (W/bit)", "Energy Efficiency", "efficiency.pdf")

    # 2. Graficos Globais de Metricas de Erro (LOA, HEAA, HOERAA, HERLOA)
    if err_by_bit:
        plot_bar(err_by_bit, APPROX_TYPES, "mae", "MAE", "Mean Absolute Error Comparison", "mae_comparison.pdf", yscale="log")
        plot_bar(err_by_bit, APPROX_TYPES, "mse", "MSE", "Mean Squared Error Comparison", "mse_comparison.pdf", yscale="log")
        plot_bar(err_by_bit, APPROX_TYPES, "ep", "Error Probability (%)", "Error Probability Comparison", "ep_comparison.pdf")
        plot_bar(err_by_bit, APPROX_TYPES, "mre", "MRE (%)", "Mean Relative Error Comparison", "mre_comparison.pdf")

    # 3. Graficos de Erro por Distribuicao (16 e 32 bits)
    if err_by_dist:
        for b in [16, 32]:
            plot_bar_dists(err_by_dist, APPROX_TYPES, b, "mae", "MAE", f"MAE Comparison by Distribution ({b}-bit)", f"mae_{b}bit_dist.pdf")
            plot_bar_dists(err_by_dist, APPROX_TYPES, b, "mse", "MSE", f"MSE Comparison by Distribution ({b}-bit)", f"mse_{b}bit_dist.pdf", yscale="log")
            plot_bar_dists(err_by_dist, APPROX_TYPES, b, "ep", "Error Probability (%)", f"Error Probability by Distribution ({b}-bit)", f"ep_{b}bit_dist.pdf")

    print(f"\n[SUCESSO] Todos os graficos com cores unificadas foram salvos em: {os.path.abspath(PLOT_DIR)}")


if __name__ == "__main__":
    main()

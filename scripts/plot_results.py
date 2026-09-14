import os
import csv
import re
import numpy as np
import matplotlib.pyplot as plt
from collections import defaultdict

# =========================================================
# CONFIGURACOES
# =========================================================

SUMMARY_CSV = "results/summary_main.csv"
ERROR_CSV = "results/error_metrics_main.csv"
PLOT_DIR = "./plots"
os.makedirs(PLOT_DIR, exist_ok=True)

# Tipos oficiais na ordem do TCC
TYPES = ["rca", "loa", "heaa", "hoeraa", "herloa"]
APPROX_TYPES = ["loa", "heaa", "hoeraa", "herloa"]

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

            canonical_k = 4 if bits == 8 else (8 if bits == 16 else 16)
            k_bits_val = int(row.get("k_bits", canonical_k)) if row.get("k_bits") else canonical_k

            if k_bits_val == canonical_k or arch == "rca":
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

            # Para comparativo global entre bits (8, 16, 32), usar K canônico (N/2)
            # 8-bit -> K=4, 16-bit -> K=8, 32-bit -> K=16
            canonical_k = 4 if bits == 8 else (8 if bits == 16 else 16)
            k_bits_val = int(row.get("k_bits", canonical_k)) if row.get("k_bits") else canonical_k

            if k_bits_val == canonical_k or arch == "rca":
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
# LEITURA E PROCESSAMENTO DOS DADOS DSE (VARIAÇÃO DE K)
# =========================================================

def load_dse_data(target_bits=8):
    """
    Carrega dados específicos de hardware e erro para um word length (8 ou 16 bits),
    agrupando por K. Para 16 bits, calcula a média entre distribuições.
    """
    dse_hw = defaultdict(lambda: defaultdict(dict))
    dse_err = defaultdict(lambda: defaultdict(dict))
    hw_power_accum = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
    err_accum = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))

    if os.path.exists(SUMMARY_CSV):
        with open(SUMMARY_CSV, "r") as f:
            for row in csv.DictReader(f):
                if row.get("bits") != str(target_bits):
                    continue
                arch = row["architecture"].lower()
                k = int(row["k_bits"]) if row.get("k_bits") else 0
                lut = int(row["Slice LUTs"]) if row.get("Slice LUTs") else 0
                dyn = float(row["Dynamic Power (W)"]) if row.get("Dynamic Power (W)") else 0.0
                tot = float(row["Total Power (W)"]) if row.get("Total Power (W)") else 0.0

                dse_hw[arch][k]["lut"] = lut
                hw_power_accum[arch][k]["dynamic"].append(dyn)
                hw_power_accum[arch][k]["total"].append(tot)

        for arch in hw_power_accum:
            for k in hw_power_accum[arch]:
                dse_hw[arch][k]["dynamic"] = np.mean(hw_power_accum[arch][k]["dynamic"])
                dse_hw[arch][k]["total"] = np.mean(hw_power_accum[arch][k]["total"])

    if os.path.exists(ERROR_CSV):
        with open(ERROR_CSV, "r") as f:
            for row in csv.DictReader(f):
                if row.get("bits") != str(target_bits):
                    continue
                arch = row["architecture"].lower()
                k = int(row["k_bits"]) if row.get("k_bits") else 0
                mae = float(row["MAE"])
                mse = float(row["MSE"])
                ep  = float(row["EP"]) * 100
                mre = float(row["MRE"]) * 100

                err_accum[arch][k]["mae"].append(mae)
                err_accum[arch][k]["mse"].append(mse)
                err_accum[arch][k]["ep"].append(ep)
                err_accum[arch][k]["mre"].append(mre)

        for arch in err_accum:
            for k in err_accum[arch]:
                dse_err[arch][k] = {
                    "mae": np.mean(err_accum[arch][k]["mae"]),
                    "mse": np.mean(err_accum[arch][k]["mse"]),
                    "ep": np.mean(err_accum[arch][k]["ep"]),
                    "mre": np.mean(err_accum[arch][k]["mre"])
                }

    return dse_hw, dse_err


def load_dse_8bit_data():
    return load_dse_data(8)


def plot_dse_bars(data_dict, types_list, metric_key, y_label, title, filename_base, yscale=None):
    """
    Gera gráfico de barras agrupadas para o DSE
    """
    plt.rcParams["figure.figsize"] = (8.5, 5)
    plt.rcParams["savefig.dpi"] = 300
    plt.rc('axes', titlesize=16, labelsize=14)
    plt.rc('xtick', labelsize=11)
    plt.rc('ytick', labelsize=11)
    plt.rc('legend', fontsize=12)

    tipos = [t for t in types_list if t in data_dict]
    k_vals = sorted({k for t in tipos for k in data_dict[t]})

    x = np.arange(len(k_vals))
    n = len(tipos)
    width = 0.8 / n

    fig, ax = plt.subplots()

    for i, tipo in enumerate(tipos):
        vals = [data_dict[tipo].get(k, {}).get(metric_key, 0) for k in k_vals]
        offset = (i - n/2) * width + width/2
        color = ARCH_COLORS.get(tipo.lower())
        ax.bar(x + offset, vals, width=width, label=tipo.upper(), color=color)

    ax.set_xticks(x)
    ax.set_xticklabels([f"K={k}" if k > 0 else "K=0 (RCA)" for k in k_vals])
    ax.set_ylabel(y_label)
    ax.set_title(title)
    if yscale:
        ax.set_yscale(yscale)

    ax.legend(loc='upper left', bbox_to_anchor=(1.02, 1.0), borderaxespad=0)
    ax.grid(axis='y', linestyle='--', alpha=0.7)

    for ext in [".pdf", ".png"]:
        filepath = os.path.join(PLOT_DIR, f"{filename_base}{ext}")
        plt.savefig(filepath, bbox_inches='tight')
    plt.close(fig)
    print(f"Plot DSE barras gerado: {filename_base} (.pdf / .png)")


def plot_dse_lines(data_dict, types_list, metric_key, y_label, title, filename_base, yscale=None):
    """
    Gera gráfico de linhas/curvas de exploração com K
    """
    plt.rcParams["figure.figsize"] = (8.5, 5)
    plt.rcParams["savefig.dpi"] = 300
    plt.rc('axes', titlesize=16, labelsize=14)
    plt.rc('xtick', labelsize=11)
    plt.rc('ytick', labelsize=11)
    plt.rc('legend', fontsize=12)

    tipos = [t for t in types_list if t in data_dict]
    k_vals = sorted({k for t in tipos for k in data_dict[t]})

    fig, ax = plt.subplots()
    markers = {"rca": "o", "loa": "s", "heaa": "^", "hoeraa": "D", "herloa": "v"}

    for tipo in tipos:
        vals = [data_dict[tipo].get(k, {}).get(metric_key, 0) for k in k_vals]
        color = ARCH_COLORS.get(tipo.lower())
        ax.plot(k_vals, vals, marker=markers.get(tipo.lower(), "o"), linewidth=2.5, markersize=8, label=tipo.upper(), color=color)

    ax.set_xticks(k_vals)
    ax.set_xticklabels([f"K={k}" if k > 0 else "K=0 (RCA)" for k in k_vals])
    ax.set_xlabel("Número de Bits Aproximados (K)")
    ax.set_ylabel(y_label)
    ax.set_title(title)
    if yscale:
        ax.set_yscale(yscale)

    ax.legend(loc='upper left', bbox_to_anchor=(1.02, 1.0), borderaxespad=0)
    ax.grid(True, linestyle='--', alpha=0.7)

    for ext in [".pdf", ".png"]:
        filepath = os.path.join(PLOT_DIR, f"{filename_base}{ext}")
        plt.savefig(filepath, bbox_inches='tight')
    plt.close(fig)
    print(f"Curva DSE gerada: {filename_base} (.pdf / .png)")


def plot_dse_tradeoff(dse_hw, dse_err, bits=8, filename_base=None):
    """
    Gera gráfico de dispersão do Trade-off Potência Dinâmica vs MAE (Fronteira de Pareto)
    """
    if filename_base is None:
        filename_base = f"dse_{bits}bit_tradeoff_power_mae"

    plt.rcParams["figure.figsize"] = (8.5, 5)
    plt.rcParams["savefig.dpi"] = 300
    plt.rc('axes', titlesize=16, labelsize=14)
    plt.rc('xtick', labelsize=11)
    plt.rc('ytick', labelsize=11)
    plt.rc('legend', fontsize=12)

    fig, ax = plt.subplots()
    markers = {"rca": "o", "loa": "s", "heaa": "^", "hoeraa": "D", "herloa": "v"}

    for tipo in APPROX_TYPES:
        color = ARCH_COLORS.get(tipo.lower())
        m = markers.get(tipo.lower(), "o")
        k_vals = sorted(dse_err[tipo].keys())
        p_vals = [dse_hw[tipo].get(k, {}).get("dynamic", 0.0) * 1000 for k in k_vals]  # mW
        mae_vals = [dse_err[tipo].get(k, {}).get("mae", 0.0) for k in k_vals]

        ax.plot(mae_vals, p_vals, marker=m, linewidth=2, markersize=8, label=tipo.upper(), color=color)

        for k, x_val, y_val in zip(k_vals, mae_vals, p_vals):
            ax.annotate(f"K={k}", (x_val, y_val), textcoords="offset points", xytext=(5, 5), fontsize=9)

    ax.set_xlabel("Mean Absolute Error (MAE)")
    ax.set_ylabel("Dynamic Power (mW)")
    ax.set_title(f"Trade-off: Dynamic Power vs. MAE ({bits}-bit)")
    ax.legend(loc='upper right')
    ax.grid(True, linestyle='--', alpha=0.7)

    for ext in [".pdf", ".png"]:
        filepath = os.path.join(PLOT_DIR, f"{filename_base}{ext}")
        plt.savefig(filepath, bbox_inches='tight')
    plt.close(fig)
    print(f"Trade-off DSE gerado: {filename_base} (.pdf / .png)")


# Aliases para retrocompatibilidade
plot_8bit_dse_bars = plot_dse_bars
plot_8bit_dse_lines = plot_dse_lines
plot_8bit_tradeoff = plot_dse_tradeoff


# =========================================================
# EXECUCAO PRINCIPAL
# =========================================================

def main():
    print("Regenerando graficos com cores estritamente padronizadas por somador...")

    hw_data = load_hardware_data()
    err_by_bit, err_by_dist = load_error_data()
    dse_hw_8, dse_err_8 = load_dse_data(8)
    dse_hw_16, dse_err_16 = load_dse_data(16)

    # 1. Graficos de Hardware Macro (8 vs 16 vs 32 bits, com K canônico N/2)
    if hw_data:
        plot_bar(hw_data, TYPES, "total", "Power (W)", "Total Power Comparison", "power_total.pdf")
        plot_bar(hw_data, TYPES, "dynamic", "Power (W)", "Dynamic Power Comparison", "power_dynamic.pdf")
        plot_bar(hw_data, TYPES, "static", "Power (W)", "Static Power Comparison", "power_static.pdf")
        plot_bar(hw_data, TYPES, "lut", "Slice LUTs", "LUT Usage Comparison", "lut_comparison.pdf")
        plot_bar(hw_data, TYPES, "reg", "Slice Registers", "Register Usage Comparison", "register_comparison.pdf")
        plot_bar(hw_data, TYPES, "efficiency", "Power per bit (W/bit)", "Energy Efficiency", "efficiency.pdf")

    # 2. Graficos Globais de Metricas de Erro (LOA, HEAA, HOERAA, HERLOA com K canônico N/2)
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

    # 4. Graficos Dedicados de DSE de 8 Bits (Variação de K: 2, 4, 6)
    if dse_err_8:
        print("\n--- Gerando suite DSE para 8-bit (K=2, 4, 6) ---")
        plot_dse_bars(dse_err_8, APPROX_TYPES, "mae", "MAE", "MAE vs. K (8-bit Adders)", "dse_8bit_mae")
        plot_dse_bars(dse_err_8, APPROX_TYPES, "mse", "MSE", "MSE vs. K (8-bit Adders)", "dse_8bit_mse", yscale="log")
        plot_dse_bars(dse_err_8, APPROX_TYPES, "ep", "Error Probability (%)", "Error Probability vs. K (8-bit)", "dse_8bit_ep")
        plot_dse_bars(dse_err_8, APPROX_TYPES, "mre", "MRE (%)", "Mean Relative Error vs. K (8-bit)", "dse_8bit_mre")

        plot_dse_lines(dse_err_8, APPROX_TYPES, "mae", "MAE", "MAE Progression with K (8-bit)", "dse_8bit_mae_curve")
        plot_dse_lines(dse_err_8, APPROX_TYPES, "mse", "MSE (log scale)", "MSE Progression with K (8-bit)", "dse_8bit_mse_curve", yscale="log")
        plot_dse_lines(dse_err_8, APPROX_TYPES, "ep", "Error Probability (%)", "EP Progression with K (8-bit)", "dse_8bit_ep_curve")

    if dse_hw_8:
        plot_dse_bars(dse_hw_8, TYPES, "lut", "Slice LUTs", "LUT Usage vs. K (8-bit Spartan-7)", "dse_8bit_lut")
        plot_dse_lines(dse_hw_8, TYPES, "lut", "Slice LUTs", "LUT Usage vs. K (8-bit Spartan-7)", "dse_8bit_lut_curve")
        plot_dse_bars(dse_hw_8, TYPES, "dynamic", "Dynamic Power (W)", "Dynamic Power vs. K (8-bit)", "dse_8bit_power_dyn")

    if dse_hw_8 and dse_err_8:
        plot_dse_tradeoff(dse_hw_8, dse_err_8, bits=8, filename_base="dse_8bit_tradeoff_power_mae")

    # 5. Graficos Dedicados de DSE de 16 Bits (Variação de K: 4, 8, 12 - ativado quando múltiplos K estiverem disponíveis)
    has_16bit_dse = any(len(dse_err_16[arch]) > 1 for arch in dse_err_16)
    if has_16bit_dse:
        print("\n--- Gerando suite DSE para 16-bit (K=4, 8, 12) ---")
        plot_dse_bars(dse_err_16, APPROX_TYPES, "mae", "MAE", "MAE vs. K (16-bit Adders)", "dse_16bit_mae")
        plot_dse_bars(dse_err_16, APPROX_TYPES, "mse", "MSE", "MSE vs. K (16-bit Adders)", "dse_16bit_mse", yscale="log")
        plot_dse_bars(dse_err_16, APPROX_TYPES, "ep", "Error Probability (%)", "Error Probability vs. K (16-bit)", "dse_16bit_ep")
        plot_dse_bars(dse_err_16, APPROX_TYPES, "mre", "MRE (%)", "Mean Relative Error vs. K (16-bit)", "dse_16bit_mre")

        plot_dse_lines(dse_err_16, APPROX_TYPES, "mae", "MAE", "MAE Progression with K (16-bit)", "dse_16bit_mae_curve")
        plot_dse_lines(dse_err_16, APPROX_TYPES, "mse", "MSE (log scale)", "MSE Progression with K (16-bit)", "dse_16bit_mse_curve", yscale="log")
        plot_dse_lines(dse_err_16, APPROX_TYPES, "ep", "Error Probability (%)", "EP Progression with K (16-bit)", "dse_16bit_ep_curve")

        if dse_hw_16:
            plot_dse_bars(dse_hw_16, TYPES, "lut", "Slice LUTs", "LUT Usage vs. K (16-bit Spartan-7)", "dse_16bit_lut")
            plot_dse_lines(dse_hw_16, TYPES, "lut", "Slice LUTs", "LUT Usage vs. K (16-bit Spartan-7)", "dse_16bit_lut_curve")
            plot_dse_bars(dse_hw_16, TYPES, "dynamic", "Dynamic Power (W)", "Dynamic Power vs. K (16-bit)", "dse_16bit_power_dyn")

        if dse_hw_16 and dse_err_16:
            plot_dse_tradeoff(dse_hw_16, dse_err_16, bits=16, filename_base="dse_16bit_tradeoff_power_mae")

    print(f"\n[SUCESSO] Todos os graficos (Macro + DSE) foram salvos em: {os.path.abspath(PLOT_DIR)}")


if __name__ == "__main__":
    main()

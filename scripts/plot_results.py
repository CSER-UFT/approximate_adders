import os
import csv
import locale
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
from collections import defaultdict

# =========================================================
# CONFIGURACOES
# =========================================================

SUMMARY_CSV = "results/summary_main.csv"
ERROR_CSV = "results/error_metrics_main.csv"
PLOT_DIR = "./plots"
DSE_DIR = "design_space_exploration"
ERROR_DIR = "error_metrics"
HARDWARE_DIR = "hardware_metrics"
for subdir in [DSE_DIR, ERROR_DIR, HARDWARE_DIR]:
    os.makedirs(os.path.join(PLOT_DIR, subdir), exist_ok=True)

# Separador decimal com virgula nos eixos
try:
    locale.setlocale(locale.LC_NUMERIC, "pt_BR.UTF-8")
    plt.rcParams["axes.formatter.use_locale"] = True
except locale.Error:
    pass
plt.rcParams["axes.formatter.use_mathtext"] = True

TYPES = ["rca", "loa", "heaa", "hoeraa", "herloa"]
APPROX_TYPES = ["loa", "heaa", "hoeraa", "herloa"]

K_VALUES = {8: [1, 2, 3, 4], 16: [2, 3, 4, 5, 6], 32: [4, 6, 8, 10]}
K_REF = {8: 2, 16: 4, 32: 8}

# conjunto de entradas de referencia de cada largura
REF_DIST = {8: "exhaustive", 16: "uniform", 32: "uniform"}
DISTS = ["uniform", "normal", "exponential"]
DIST_LABELS = ["Uniforme", "Normal", "Exponencial"]
WIDTH_LABELS = {8: "8 bits\n(todas as entradas)", 16: "16 bits\n(uniforme)", 32: "32 bits\n(uniforme)"}

ARCH_COLORS = {
    "rca":    "#1f77b4",  # Azul
    "loa":    "#ff7f0e",  # Laranja
    "heaa":   "#2ca02c",  # Verde
    "hoeraa": "#d62728",  # Vermelho
    "herloa": "#9467bd"   # Roxo
}
MARKERS = {"loa": "s", "heaa": "^", "hoeraa": "D", "herloa": "v"}
LINESTYLES = {"loa": "-", "heaa": "--", "hoeraa": "-.", "herloa": ":"}

# =========================================================
# LEITURA DOS DADOS
# =========================================================

def load_table(path, columns):
    # tabela[(arquitetura, bits, k, distribuicao)] = {metrica: valor}
    table = {}
    if not os.path.exists(path):
        print(f"Erro: Arquivo {path} nao encontrado.")
        return table

    with open(path, "r") as f:
        for row in csv.DictReader(f):
            arch = row["architecture"].lower()
            if arch not in TYPES:
                continue
            key = (arch, int(row["bits"]), int(row["k_bits"]), row["distribution"].lower())
            table[key] = {metric: float(row[column]) * scale for metric, (column, scale) in columns.items()}
    return table


def k_of(arch, k):
    return 0 if arch == "rca" else k


def by_width(table):
    # dados[arquitetura][bits], com K = N/4 e as entradas de referencia
    data = defaultdict(dict)
    for arch in TYPES:
        for bits in K_REF:
            key = (arch, bits, k_of(arch, K_REF[bits]), REF_DIST[bits])
            if key in table:
                data[arch][bits] = table[key]
    return data


def by_dist(table, bits):
    # dados[arquitetura][distribuicao], com K = N/4
    data = defaultdict(dict)
    for arch in TYPES:
        for dist in DISTS:
            key = (arch, bits, k_of(arch, K_REF[bits]), dist)
            if key in table:
                data[arch][dist] = table[key]
    return data


def by_k(table, bits):
    # dados[arquitetura][k], com as entradas de referencia; RCA em K=0
    data = defaultdict(dict)
    for arch in TYPES:
        for k in [0] + K_VALUES[bits]:
            key = (arch, bits, k, REF_DIST[bits])
            if key in table:
                data[arch][k] = table[key]
    return data

# =========================================================
# FUNCOES DE PLOTAGEM
# =========================================================

def setup_style():
    plt.rcParams["figure.figsize"] = (8.5, 5)
    plt.rcParams["savefig.dpi"] = 300
    plt.rc('axes', titlesize=20, labelsize=18)
    plt.rc('xtick', labelsize=15)
    plt.rc('ytick', labelsize=15)
    plt.rc('legend', fontsize=16)


def log_label(label, scale):
    if scale != "log":
        return label
    return f"{label[:-1]}, escala log)" if label.endswith(")") else f"{label} (escala log)"


def save(fig, filename_base, exts):
    for ext in exts:
        plt.savefig(os.path.join(PLOT_DIR, f"{filename_base}{ext}"), bbox_inches='tight')
    plt.close(fig)
    print(f"Plot gerado: {filename_base}")


def plot_bars(data, types_list, x_keys, x_labels, metric_key, y_label, title, filename_base,
              yscale=None, exts=(".pdf",)):
    setup_style()
    tipos = [t for t in types_list if t in data]

    x = np.arange(len(x_keys))
    n = len(tipos)
    width = 0.8 / n

    fig, ax = plt.subplots()
    all_vals = []

    for i, tipo in enumerate(tipos):
        vals = [data[tipo].get(key, {}).get(metric_key, 0) for key in x_keys]
        all_vals.extend(vals)
        offset = (i - n/2) * width + width/2
        ax.bar(x + offset, vals, width=width, label=tipo.upper(), color=ARCH_COLORS.get(tipo))

    ax.set_xticks(x)
    ax.set_xticklabels(x_labels)
    if metric_key == "lut":
        ax.yaxis.set_major_locator(MaxNLocator(integer=True))
    ax.set_ylabel(y_label)
    ax.set_title(title)
    if yscale == "log":
        ax.set_yscale(yscale)
        # deixa folga abaixo da menor barra
        positivos = [v for v in all_vals if v > 0]
        if positivos:
            ax.set_ylim(bottom=min(positivos) / 3)

    ax.legend(loc='upper left', bbox_to_anchor=(1.02, 1.0), borderaxespad=0)
    ax.grid(axis='y', linestyle='--', alpha=0.7)
    save(fig, filename_base, exts)


def plot_lines(data, bits, metric_key, y_label, title, filename_base, yscale=None):
    setup_style()
    k_vals = K_VALUES[bits]
    offset_map = {"loa": -0.06, "heaa": -0.02, "hoeraa": 0.02, "herloa": 0.06}

    fig, ax = plt.subplots()

    for tipo in APPROX_TYPES:
        vals = [data[tipo].get(k, {}).get(metric_key, 0) for k in k_vals]
        if yscale == "log":
            vals = [v if v > 0 else np.nan for v in vals]  # erro zero nao aparece em log
        x_vals = [k + offset_map[tipo] for k in k_vals]
        ax.plot(x_vals, vals, marker=MARKERS[tipo], linewidth=2.5, markersize=8, alpha=0.85,
                label=tipo.upper(), color=ARCH_COLORS.get(tipo), linestyle=LINESTYLES[tipo])

    ax.set_xticks(k_vals)
    ax.set_xticklabels([f"K={k}" for k in k_vals])
    ax.set_xlabel("Número de Bits Aproximados (K)")
    ax.set_ylabel(y_label)
    ax.set_title(title)
    if yscale:
        ax.set_yscale(yscale)

    ax.legend(loc='upper left', bbox_to_anchor=(1.02, 1.0), borderaxespad=0)
    ax.grid(True, linestyle='--', alpha=0.7)
    save(fig, filename_base, (".pdf", ".png"))


def plot_tradeoff(hw, err, bits, title, filename_base, xscale=None):
    setup_style()
    fig, ax = plt.subplots()

    for tipo in APPROX_TYPES:
        k_vals = K_VALUES[bits]
        p_vals = [hw[tipo].get(k, {}).get("dynamic", 0) for k in k_vals]
        mae_vals = [err[tipo].get(k, {}).get("mae", 0) for k in k_vals]
        pts = [(x, y) for x, y in zip(mae_vals, p_vals) if xscale != "log" or x > 0]
        if not pts:
            continue

        xs, ys = zip(*pts)
        ax.plot(xs, ys, marker=MARKERS[tipo], linewidth=2.5, markersize=8, alpha=0.85,
                label=tipo.upper(), color=ARCH_COLORS.get(tipo), linestyle=LINESTYLES[tipo])

    if xscale:
        ax.set_xscale(xscale)
    ax.margins(x=0.07, y=0.14)
    ax.set_xlabel(log_label("Erro Absoluto Médio (MAE, unidades)", xscale))
    ax.set_ylabel("Potência Dinâmica (mW)")
    ax.set_title(title)

    ax.legend(loc='upper left', bbox_to_anchor=(1.02, 1.0), borderaxespad=0)
    ax.grid(True, linestyle='--', alpha=0.7)
    save(fig, filename_base, (".pdf", ".png"))

def plot_overview(table, types_list, metric_key, y_label, title, filename_base, yscale=None):
    # todas as larguras e distribuicoes em um unico grafico, com K = N/4
    setup_style()
    fig, ax = plt.subplots(figsize=(13, 5))

    # posicao de cada grupo no eixo x, com espaco entre as larguras
    conds, ticks, tick_labels, centers = [], [], [], {}
    pos = 0.0
    for bits in sorted(K_REF):
        dists = [REF_DIST[bits]] if bits == 8 else DISTS
        labels = ["Todas as\nentradas"] if bits == 8 else DIST_LABELS
        start = pos
        for dist, label in zip(dists, labels):
            conds.append((bits, dist, pos))
            ticks.append(pos)
            tick_labels.append(label)
            pos += 1.0
        centers[bits] = (start + pos - 1.0) / 2
        pos += 0.6

    n = len(types_list)
    width = 0.16
    for i, tipo in enumerate(types_list):
        offset = (i - (n - 1) / 2) * width
        xs = [p + offset for _, _, p in conds]
        ys = [table.get((tipo, bits, k_of(tipo, K_REF[bits]), dist), {}).get(metric_key, 0) for bits, dist, _ in conds]
        if yscale == "log":
            ax.plot(xs, ys, linestyle="none", marker=MARKERS[tipo], markersize=8, alpha=0.85,
                    color=ARCH_COLORS.get(tipo), label=tipo.upper())
        else:
            ax.bar(xs, ys, width=width, color=ARCH_COLORS.get(tipo), label=tipo.upper())

    ax.set_xticks(ticks)
    ax.set_xticklabels(tick_labels)
    for bits, center in centers.items():
        ax.text(center, -0.17, f"{bits} bits", transform=ax.get_xaxis_transform(), ha="center", va="top", fontsize=17)
    for left, right in zip(sorted(centers)[:-1], sorted(centers)[1:]):
        last_left = max(p for b, _, p in conds if b == left)
        first_right = min(p for b, _, p in conds if b == right)
        ax.axvline((last_left + first_right) / 2, color="gray", linewidth=1, alpha=0.6)
    ax.set_xlim(ticks[0] - 0.6, ticks[-1] + 0.6)

    if yscale:
        ax.set_yscale(yscale)
    ax.set_ylabel(y_label)
    ax.set_title(title)

    ax.legend(loc='upper left', bbox_to_anchor=(1.02, 1.0), borderaxespad=0)
    ax.grid(axis='y', linestyle='--', alpha=0.7)
    save(fig, filename_base, (".pdf",))

# =========================================================
# EXECUCAO PRINCIPAL
# =========================================================

def main():
    # potencia em mW; probabilidade de erro e MRE em %
    hw = load_table(SUMMARY_CSV, {"lut": ("Slice LUTs", 1), "dynamic": ("Dynamic Power (W)", 1000)})
    err = load_table(ERROR_CSV, {"mae": ("MAE", 1), "mse": ("MSE", 1), "ep": ("EP", 100), "mre": ("MRE", 100)})
    if not hw or not err:
        return

    # Comparacao entre larguras (K = N/4)
    widths = sorted(K_REF)
    width_labels = [WIDTH_LABELS[b] for b in widths]
    hw_width, err_width = by_width(hw), by_width(err)
    plot_bars(hw_width, TYPES, widths, width_labels, "dynamic", "Potência Dinâmica (mW)",
              "Comparação de Potência Dinâmica (K = N/4)", f"{HARDWARE_DIR}/power_dynamic")
    plot_bars(hw_width, TYPES, widths, width_labels, "lut", "Uso de LUTs",
              "Comparação de Uso de LUTs (K = N/4)", f"{HARDWARE_DIR}/lut_comparison")
    plot_bars(err_width, APPROX_TYPES, widths, width_labels, "mae", "MAE (unidades, escala log)",
              "Comparação de MAE (K = N/4)", f"{ERROR_DIR}/mae_comparison", yscale="log")
    plot_bars(err_width, APPROX_TYPES, widths, width_labels, "mre", "MRE (%, escala log)",
              "Comparação de MRE (K = N/4)", f"{ERROR_DIR}/mre_comparison", yscale="log")

    # Efeito da distribuicao das entradas (16 e 32 bits, K = N/4)
    for bits in [16, 32]:
        cond = f"({bits} bits, K={K_REF[bits]})"
        plot_bars(by_dist(hw, bits), TYPES, DISTS, DIST_LABELS, "dynamic", "Potência Dinâmica (mW)",
                  f"Potência Dinâmica por Distribuição {cond}", f"{HARDWARE_DIR}/power_dynamic_{bits}bit_dist")
        plot_bars(by_dist(err, bits), APPROX_TYPES, DISTS, DIST_LABELS, "mre", "MRE (%)",
                  f"MRE por Distribuição {cond}", f"{ERROR_DIR}/mre_{bits}bit_dist")

    # Visao geral por largura e distribuicao (K = N/4)
    plot_overview(hw, TYPES, "dynamic", "Potência Dinâmica (mW)",
                  "Potência Dinâmica por Largura e Distribuição (K = N/4)", f"{HARDWARE_DIR}/power_dynamic_overview")
    plot_overview(err, APPROX_TYPES, "mre", "MRE (%, escala log)",
                  "MRE por Largura e Distribuição (K = N/4)", f"{ERROR_DIR}/mre_overview", yscale="log")

    # Variacao de K em cada largura
    mae_scale = {8: None, 16: None, 32: "log"}
    mse_scale = {8: None, 16: "log", 32: "log"}
    mre_scale = {8: None, 16: "log", 32: "log"}
    tradeoff_scale = {8: None, 16: "log", 32: "log"}

    for bits in widths:
        cond = f"({bits} bits)" if bits == 8 else f"({bits} bits, uniforme)"
        hw_k, err_k = by_k(hw, bits), by_k(err, bits)
        k_keys = [0] + K_VALUES[bits]
        k_labels = ["K=0 (RCA)"] + [f"K={k}" for k in K_VALUES[bits]]
        base = f"{DSE_DIR}/dse_{bits}bit"

        plot_lines(err_k, bits, "mae", log_label("MAE (unidades)", mae_scale[bits]),
                   f"MAE vs. K {cond}", f"{base}_mae_curve", yscale=mae_scale[bits])
        plot_lines(err_k, bits, "mse", log_label("MSE (unidades²)", mse_scale[bits]),
                   f"MSE vs. K {cond}", f"{base}_mse_curve", yscale=mse_scale[bits])
        plot_lines(err_k, bits, "ep", "Probabilidade de Erro (%)",
                   f"Probabilidade de Erro vs. K {cond}", f"{base}_ep_curve")
        plot_lines(err_k, bits, "mre", log_label("MRE (%)", mre_scale[bits]),
                   f"MRE vs. K {cond}", f"{base}_mre_curve", yscale=mre_scale[bits])

        plot_bars(hw_k, TYPES, k_keys, k_labels, "lut", "Uso de LUTs",
                  f"Uso de LUTs vs. K ({bits} bits)", f"{base}_lut", exts=(".pdf", ".png"))
        plot_bars(hw_k, TYPES, k_keys, k_labels, "dynamic", "Potência Dinâmica (mW)",
                  f"Potência Dinâmica vs. K {cond}", f"{base}_power_dyn", exts=(".pdf", ".png"))

        plot_tradeoff(hw_k, err_k, bits, f"Potência Dinâmica vs. MAE {cond}",
                      f"{base}_tradeoff_power_mae", xscale=tradeoff_scale[bits])

    print(f"Graficos salvos em: {os.path.abspath(PLOT_DIR)}")


if __name__ == "__main__":
    main()

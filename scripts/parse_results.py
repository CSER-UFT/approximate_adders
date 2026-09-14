import os
import re
import csv

VIVADO_REPORTS_DIR = "./vivado_reports"
OUTPUT_CSV = "./results/summary_main.csv"


# =========================================================
# Funções auxiliares
# =========================================================

def extract_float(line):
    nums = re.findall(r"\d+\.\d+", line.replace(",", ""))
    return float(nums[-1]) if nums else ""


def parse_experiment_metadata(exp_name, rel_dir=""):
    clean = exp_name
    if clean.startswith("sim_"):
        clean = clean[4:]

    parts = clean.split("_")
    arch = parts[0].upper()

    # Bits
    bits = 0
    bits_match = re.search(r"(\d+)bit", clean)
    if bits_match:
        bits = int(bits_match.group(1))
    elif "8bit" in rel_dir:
        bits = 8
    elif "16bit" in rel_dir:
        bits = 16
    elif "32bit" in rel_dir:
        bits = 32

    # k_bits
    k_bits = None
    k_match = re.search(r"_k(\d+)", clean)
    if k_match:
        k_bits = int(k_match.group(1))
    else:
        # Tenta extrair da pasta rel_dir (ex: 8bit/k4)
        k_dir_match = re.search(r"/k(\d+)", rel_dir.replace("\\", "/"))
        if k_dir_match:
            k_bits = int(k_dir_match.group(1))
        elif arch == "RCA":
            k_bits = 0
        elif bits == 8:
            k_bits = 4
        elif bits == 16:
            k_bits = 8
        elif bits == 32:
            k_bits = 16
        else:
            k_bits = 0

    # Distribuicao
    if "exponential" in clean:
        distribution = "exponential"
    elif "normal" in clean:
        distribution = "normal"
    elif "uniform" in clean:
        distribution = "uniform"
    elif bits == 8:
        distribution = "exhaustive"
    else:
        distribution = "unknown"

    # Nome padronizado do experimento: <arch>_<N>bit_k<K>_<distribuicao>
    canonical_exp = f"{arch.lower()}_{bits}bit_k{k_bits}_{distribution}"

    return canonical_exp, arch, bits, k_bits, distribution


# =========================================================
# Parsing dos relatórios
# =========================================================

def parse_resource(filepath):
    lut = ""
    reg = ""

    with open(filepath, "r") as f:
        for line in f:
            if "Slice LUTs" in line and "|" in line:
                cols = [c.strip() for c in line.split("|")]
                if len(cols) > 2 and cols[2].isdigit():
                    lut = int(cols[2])

            elif "Slice Registers" in line and "|" in line:
                cols = [c.strip() for c in line.split("|")]
                if len(cols) > 2 and cols[2].isdigit():
                    reg = int(cols[2])

    return lut, reg


def parse_power(filepath):
    total = ""
    dynamic = ""
    static = ""

    with open(filepath, "r") as f:
        for line in f:
            if "Total On-Chip Power" in line:
                total = extract_float(line)

            elif "Dynamic (W)" in line:
                dynamic = extract_float(line)

            elif "Device Static" in line:
                static = extract_float(line)

    return total, dynamic, static


# =========================================================
# Programa principal
# =========================================================

def main():
    experiments = {}
    os.makedirs(os.path.dirname(OUTPUT_CSV), exist_ok=True)

    for root, _, files in os.walk(VIVADO_REPORTS_DIR):
        rel_dir = os.path.relpath(root, VIVADO_REPORTS_DIR)
        for filename in files:
            if not filename.endswith(".rpt"):
                continue

            base = filename.replace("_resource.rpt", "") \
                           .replace("_timing.rpt", "") \
                           .replace("_power.rpt", "")

            filepath = os.path.join(root, filename)

            canonical_exp, arch, bits, k_bits, dist = parse_experiment_metadata(base, rel_dir)

            if canonical_exp not in experiments:
                experiments[canonical_exp] = {
                    "architecture": arch,
                    "bits": bits,
                    "k_bits": k_bits,
                    "distribution": dist,
                    "lut": "",
                    "reg": "",
                    "total": "",
                    "dynamic": "",
                    "static": ""
                }

            if "_resource.rpt" in filename:
                lut, reg = parse_resource(filepath)
                experiments[canonical_exp]["lut"] = lut
                experiments[canonical_exp]["reg"] = reg

            elif "_power.rpt" in filename:
                total, dynamic, static = parse_power(filepath)
                experiments[canonical_exp]["total"] = total
                experiments[canonical_exp]["dynamic"] = dynamic
                experiments[canonical_exp]["static"] = static

    # =========================================================
    # Ordenação estruturada (Bits -> K -> Distribuição -> Arquitetura)
    # =========================================================

    def sort_key(item):
        exp, data = item
        dist_order = {"exhaustive": 0, "uniform": 1, "normal": 2, "exponential": 3}
        arch_order = {"RCA": 0, "LOA": 1, "HEAA": 2, "HOERAA": 3, "HERLOA": 4}
        bits = data.get("bits", 0)
        k_bits = data.get("k_bits", 0)
        dist = dist_order.get(data.get("distribution"), 99)
        arch = arch_order.get(data.get("architecture"), 99)
        return (bits, k_bits, dist, arch, exp)

    sorted_experiments = sorted(experiments.items(), key=sort_key)

    # =========================================================
    # Geração do CSV
    # =========================================================

    fieldnames = [
        "experiment",
        "architecture",
        "bits",
        "k_bits",
        "distribution",
        "Slice LUTs",
        "Slice Registers",
        "Total Power (W)",
        "Dynamic Power (W)",
        "Static Power (W)"
    ]

    with open(OUTPUT_CSV, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(fieldnames)

        for exp, e in sorted_experiments:
            writer.writerow([
                exp,
                e.get("architecture", ""),
                e.get("bits", ""),
                e.get("k_bits", ""),
                e.get("distribution", ""),
                e.get("lut", ""),
                e.get("reg", ""),
                e.get("total", ""),
                e.get("dynamic", ""),
                e.get("static", "")
            ])

    print(f"CSV mestre gerado com sucesso: {OUTPUT_CSV} ({len(sorted_experiments)} experimentos)")


if __name__ == "__main__":
    main()

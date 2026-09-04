import os
import re
import csv

RESULTS_DIR = "./results"
OUTPUT_CSV = "summary.csv"


# =========================================================
# Funções auxiliares
# =========================================================

def extract_float(line):
    nums = re.findall(r"\d+\.\d+", line.replace(",", ""))
    return float(nums[-1]) if nums else ""


def parse_experiment_metadata(exp_name):
    clean = exp_name
    if clean.startswith("sim_"):
        clean = clean[4:]

    parts = clean.split("_")
    arch = parts[0].upper()

    bits = 0
    if len(parts) > 1 and "bit" in parts[1]:
        try:
            bits = int(parts[1].replace("bit", ""))
        except ValueError:
            bits = 0

    if bits == 8:
        distribution = "exhaustive"
    elif len(parts) > 2:
        distribution = parts[2].lower()
    else:
        distribution = "unknown"

    return arch, bits, distribution


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

    for filename in os.listdir(RESULTS_DIR):
        if not filename.endswith(".rpt"):
            continue

        base = filename.replace("_resource.rpt", "") \
                       .replace("_timing.rpt", "") \
                       .replace("_power.rpt", "")

        filepath = os.path.join(RESULTS_DIR, filename)

        if base not in experiments:
            arch, bits, dist = parse_experiment_metadata(base)
            experiments[base] = {
                "architecture": arch,
                "bits": bits,
                "distribution": dist
            }

        if "_resource.rpt" in filename:
            lut, reg = parse_resource(filepath)
            experiments[base]["lut"] = lut
            experiments[base]["reg"] = reg

        elif "_power.rpt" in filename:
            total, dynamic, static = parse_power(filepath)
            experiments[base]["total"] = total
            experiments[base]["dynamic"] = dynamic
            experiments[base]["static"] = static

    # =========================================================
    # Ordenação estruturada (Bits -> Distribuição -> Arquitetura)
    # =========================================================

    def sort_key(item):
        exp, data = item
        dist_order = {"exhaustive": 0, "uniform": 1, "normal": 2, "exponential": 3}
        arch_order = {"RCA": 0, "LOA": 1, "HEAA": 2, "HOERAA": 3, "HERLOA": 4}
        bits = data.get("bits", 0)
        dist = dist_order.get(data.get("distribution"), 99)
        arch = arch_order.get(data.get("architecture"), 99)
        return (bits, dist, arch, exp)

    sorted_experiments = sorted(experiments.items(), key=sort_key)

    # =========================================================
    # Geração do CSV
    # =========================================================

    with open(OUTPUT_CSV, "w", newline="") as f:
        writer = csv.writer(f)

        writer.writerow([
            "experiment",
            "architecture",
            "bits",
            "distribution",
            "Slice LUTs",
            "Slice Registers",
            "Total Power (W)",
            "Dynamic Power (W)",
            "Static Power (W)"
        ])

        for exp, e in sorted_experiments:
            writer.writerow([
                exp,
                e.get("architecture", ""),
                e.get("bits", ""),
                e.get("distribution", ""),
                e.get("lut", ""),
                e.get("reg", ""),
                e.get("total", ""),
                e.get("dynamic", ""),
                e.get("static", "")
            ])

    print(f"CSV gerado com sucesso: {OUTPUT_CSV}")


if __name__ == "__main__":
    main()

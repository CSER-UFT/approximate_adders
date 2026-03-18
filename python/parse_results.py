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


# =========================================================
# Parsing dos relatórios
# =========================================================

def parse_resource(filepath):
    lut = ""
    reg = ""

    with open(filepath, "r") as f:
        for line in f:
            # Slice LUTs
            if "Slice LUTs" in line and "|" in line:
                cols = [c.strip() for c in line.split("|")]
                if len(cols) > 2 and cols[2].isdigit():
                    lut = int(cols[2])

            # Slice Registers
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
            experiments[base] = {}

        # Resource report
        if "_resource.rpt" in filename:
            lut, reg = parse_resource(filepath)
            experiments[base]["lut"] = lut
            experiments[base]["reg"] = reg

        # Power report
        elif "_power.rpt" in filename:
            total, dynamic, static = parse_power(filepath)
            experiments[base]["total"] = total
            experiments[base]["dynamic"] = dynamic
            experiments[base]["static"] = static

    # =========================================================
    # Geração do CSV
    # =========================================================

    with open(OUTPUT_CSV, "w", newline="") as f:
        writer = csv.writer(f)

        writer.writerow([
            "experiment",
            "Slice LUTs",
            "Slice Registers",
            "Total Power (W)",
            "Dynamic Power (W)",
            "Static Power (W)"
        ])

        for exp in sorted(experiments.keys()):
            e = experiments[exp]

            writer.writerow([
                exp,
                e.get("lut", ""),
                e.get("reg", ""),
                e.get("total", ""),
                e.get("dynamic", ""),
                e.get("static", "")
            ])

    print(f"CSV gerado com sucesso: {OUTPUT_CSV}")


if __name__ == "__main__":
    main()

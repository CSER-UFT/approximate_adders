import os
import csv
from typing import List, Dict, Tuple


def compute_error_metrics(exact: List[int], approx: List[int]) -> Dict[str, float]:
    total_samples = len(exact)
    if total_samples == 0 or len(approx) != total_samples:
        raise ValueError("Conjuntos de dados invalidos ou de tamanhos diferentes.")

    ed_list = [abs(e - a) for e, a in zip(exact, approx)]
    mae = sum(ed_list) / total_samples
    mse = sum(ed ** 2 for ed in ed_list) / total_samples
    error_count = sum(1 for ed in ed_list if ed != 0)
    ep = error_count / total_samples

    relative_errors = [ed / e for ed, e in zip(ed_list, exact) if e != 0]
    mre = (sum(relative_errors) / len(relative_errors)) if relative_errors else 0.0

    return {
        "MAE": mae,
        "MSE": mse,
        "EP": ep,
        "MRE": mre,
        "Total Samples": total_samples,
        "Error Count": error_count
    }


def parse_result_file(filepath: str, bits: int) -> Tuple[List[Tuple[int, int, int]], List[int], List[int]]:
    inputs = []
    exact_sums = []
    circuit_sums = []

    with open(filepath, "r") as f:
        for line_num, line in enumerate(f, start=1):
            stripped = line.strip()
            if not stripped:
                continue

            parts = stripped.split()
            if len(parts) != 5:
                raise ValueError(
                    f"Erro de formato no arquivo '{filepath}', linha {line_num}: "
                    f"esperados 5 campos (A B Cin Sum Cout), mas encontrados {len(parts)} campos: '{stripped}'"
                )

            try:
                a = int(parts[0], 16)
                b = int(parts[1], 16)
                cin = int(parts[2], 2)
                sum_val = int(parts[3], 16)
                cout = int(parts[4], 2)
            except ValueError as e:
                raise ValueError(
                    f"Erro ao converter valores no arquivo '{filepath}', linha {line_num}: '{stripped}' -> {e}"
                )

            inputs.append((a, b, cin))
            exact_sums.append(a + b + cin)
            circuit_sums.append((cout << bits) | sum_val)

    return inputs, exact_sums, circuit_sums


def validate_rca(filepath: str, bits: int, inputs: List[Tuple[int, int, int]], exact_sums: List[int], circuit_sums: List[int]):
    for idx, (inp, exact, circ) in enumerate(zip(inputs, exact_sums, circuit_sums), start=1):
        if exact != circ:
            a, b, cin = inp
            raise ValueError(
                f"FALHA DE VALIDACAO NO RCA!\n"
                f"  Arquivo:  {filepath}\n"
                f"  Linha:    {idx}\n"
                f"  A:        0x{a:X} ({a})\n"
                f"  B:        0x{b:X} ({b})\n"
                f"  Cin:      {cin}\n"
                f"  Esperado (a + b + cin): {exact}\n"
                f"  Obtido no Circuito:     {circ}"
            )


def validate_input_alignment(rca_file: str, approx_file: str, rca_inputs: List[Tuple[int, int, int]], approx_inputs: List[Tuple[int, int, int]]):
    if len(rca_inputs) != len(approx_inputs):
        raise ValueError(
            f"DESALINHAMENTO DE QUANTIDADE DE AMOSTRAS!\n"
            f"  RCA ({rca_file}): {len(rca_inputs)} amostras\n"
            f"  Aproximado ({approx_file}): {len(approx_inputs)} amostras"
        )

    for idx, (inp_rca, inp_app) in enumerate(zip(rca_inputs, approx_inputs), start=1):
        if inp_rca != inp_app:
            a_r, b_r, c_r = inp_rca
            a_a, b_a, c_a = inp_app
            raise ValueError(
                f"DESALINHAMENTO DE ENTRADAS LINHA A LINHA!\n"
                f"  Linha:               {idx}\n"
                f"  Arquivo RCA:         {rca_file} -> A=0x{a_r:X}, B=0x{b_r:X}, Cin={c_r}\n"
                f"  Arquivo Aproximado:  {approx_file} -> A=0x{a_a:X}, B=0x{b_a:X}, Cin={c_a}"
            )


def evaluate_all_results(results_dir: str = "./results", output_csv: str = "error_metrics_summary.csv"):
    architectures = ["loa", "heaa", "hoeraa", "herloa"]
    distributions = ["uniform", "normal", "exponential"]

    processed_files = []
    validated_rcas = set()
    aligned_pairs = []
    warnings_list = []
    records = []

    # 1. Somadores de 8 bits
    rca_8bit_file = os.path.join(results_dir, "rca_8bit.txt")
    rca_8bit_data = None

    if os.path.exists(rca_8bit_file):
        rca_in, rca_exact, rca_circ = parse_result_file(rca_8bit_file, 8)
        if len(rca_in) != 65536:
            warnings_list.append(f"ALERTA: rca_8bit.txt contem {len(rca_in)} amostras (esperado: 65536).")
        validate_rca(rca_8bit_file, 8, rca_in, rca_exact, rca_circ)
        rca_8bit_data = (rca_in, rca_circ)
        validated_rcas.add("rca_8bit.txt")
        processed_files.append("rca_8bit.txt")

    for arch in architectures:
        approx_8bit_file = os.path.join(results_dir, f"{arch}_8bit.txt")
        if not os.path.exists(approx_8bit_file):
            continue

        app_in, app_exact, app_circ = parse_result_file(approx_8bit_file, 8)
        processed_files.append(f"{arch}_8bit.txt")

        if len(app_in) != 65536:
            warnings_list.append(f"ALERTA: {arch}_8bit.txt contem {len(app_in)} amostras (esperado: 65536).")

        if rca_8bit_data is not None:
            rca_in, rca_circ = rca_8bit_data
            validate_input_alignment(rca_8bit_file, approx_8bit_file, rca_in, app_in)
            aligned_pairs.append(("rca_8bit.txt", f"{arch}_8bit.txt"))
            exact_vals = rca_circ
        else:
            warnings_list.append(f"AVISO: arquivo RCA não encontrado ({rca_8bit_file}); usando soma exata calculada como referência.")
            exact_vals = app_exact

        metrics = compute_error_metrics(exact_vals, app_circ)
        records.append({
            "experiment": f"{arch}_8bit",
            "architecture": arch.upper(),
            "bits": 8,
            "distribution": "exhaustive",
            **metrics
        })

    # 2. Somadores de 16 e 32 bits (Distribuicoes estatisticas)
    for bits in [16, 32]:
        for dist in distributions:
            rca_file = os.path.join(results_dir, f"rca_{bits}bit_{dist}.txt")
            rca_data = None

            if os.path.exists(rca_file):
                rca_in, rca_exact, rca_circ = parse_result_file(rca_file, bits)
                validate_rca(rca_file, bits, rca_in, rca_exact, rca_circ)
                rca_data = (rca_in, rca_circ)
                validated_rcas.add(f"rca_{bits}bit_{dist}.txt")
                processed_files.append(f"rca_{bits}bit_{dist}.txt")

            for arch in architectures:
                exp_name = f"{arch}_{bits}bit_{dist}"
                approx_file = os.path.join(results_dir, f"{exp_name}.txt")

                if not os.path.exists(approx_file):
                    continue

                app_in, app_exact, app_circ = parse_result_file(approx_file, bits)
                processed_files.append(f"{exp_name}.txt")

                if rca_data is not None:
                    rca_in, rca_circ = rca_data
                    validate_input_alignment(rca_file, approx_file, rca_in, app_in)
                    aligned_pairs.append((f"rca_{bits}bit_{dist}.txt", f"{exp_name}.txt"))
                    exact_vals = rca_circ
                else:
                    warnings_list.append(f"AVISO: arquivo RCA não encontrado ({rca_file}); usando soma exata calculada como referência.")
                    exact_vals = app_exact

                metrics = compute_error_metrics(exact_vals, app_circ)
                records.append({
                    "experiment": exp_name,
                    "architecture": arch.upper(),
                    "bits": bits,
                    "distribution": dist,
                    **metrics
                })

    if records:
        fieldnames = [
            "experiment", "architecture", "bits", "distribution",
            "MAE", "MSE", "EP", "MRE", "Total Samples", "Error Count"
        ]
        with open(output_csv, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(records)

    print("1. ARQUIVOS PROCESSADOS:")
    for pf in sorted(processed_files):
        print(f"   - {pf}")
    print()

    print("2. VALIDACAO DOS ARQUIVOS RCA (100% Exatos contra a + b + cin):")
    if validated_rcas:
        for vr in sorted(validated_rcas):
            print(f"   - [OK] {vr}: validado com 0 divergencias.")
    else:
        print("   - Nenhum arquivo RCA processado.")
    print()

    print("3. ALINHAMENTO DE ENTRADAS (RCA x APROXIMADO):")
    if aligned_pairs:
        for rca_p, app_p in aligned_pairs:
            print(f"   - [OK] {rca_p} <-> {app_p}: entradas 100% alinhadas linha a linha.")
    else:
        print("   - Nenhum par comparado.")
    print()

    print("4. ALERTAS E AVISOS ENCONTRADOS:")
    if warnings_list:
        for w in warnings_list:
            print(f"   - {w}")
    else:
        print("   - Nenhum alerta. Todos os dados estao em perfeita conformidade.")
    print()

    print("5. METRICAS FINAIS POR EXPERIMENTO:")
    print(f"| {'Experimento':<16} | {'Bits':^4} | {'Distribuicao':^12} | {'MAE':^8} | {'MSE':^8} | {'EP (%)':^8} | {'MRE (%)':^8} | {'Erros':^7} | {'Total':^7} |")
    print(f"|{'-'*18}|{'-'*6}|{'-'*14}|{'-'*10}|{'-'*10}|{'-'*10}|{'-'*10}|{'-'*9}|{'-'*9}|")
    for r in records:
        print(f"| {r['experiment']:<16} | {r['bits']:^4} | {r['distribution']:^12} | {r['MAE']:8.4f} | {r['MSE']:8.4f} | {r['EP']*100:6.2f}%  | {r['MRE']*100:6.2f}%  | {r['Error Count']:^7} | {r['Total Samples']:^7} |")
    print()
    print(f"Metricas de erro salvas com sucesso em: {output_csv}\n")


if __name__ == "__main__":
    evaluate_all_results()

import os
import csv
import re
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


def find_file(base_name: str, search_dirs: List[str]) -> str:
    for sdir in search_dirs:
        for root, _, files in os.walk(sdir):
            if base_name in files:
                return os.path.join(root, base_name)
    return None


def evaluate_all_results(
    sim_dirs: List[str] = None,
    output_csv: str = "./results/error_metrics_main.csv"
):
    if sim_dirs is None:
        sim_dirs = ["./sim_output", "./results"]

    architectures = ["loa", "heaa", "hoeraa", "herloa"]
    distributions = ["uniform", "normal", "exponential"]

    processed_files = []
    validated_rcas = set()
    aligned_pairs = []
    warnings_list = []
    records = []

    # 1. Somadores de 8 bits
    rca_8bit_file = find_file("rca_8bit.txt", sim_dirs)
    rca_8bit_data = None

    if rca_8bit_file and os.path.exists(rca_8bit_file):
        rca_in, rca_exact, rca_circ = parse_result_file(rca_8bit_file, 8)
        if len(rca_in) != 65536:
            warnings_list.append(f"ALERTA: rca_8bit.txt contem {len(rca_in)} amostras (esperado: 65536).")
        validate_rca(rca_8bit_file, 8, rca_in, rca_exact, rca_circ)
        rca_8bit_data = (rca_in, rca_circ)
        validated_rcas.add(os.path.basename(rca_8bit_file))
        processed_files.append(rca_8bit_file)

    # 1. Somadores de 8 bits (Varredura de K em [2, 4, 6])
    for k in [1, 2, 3]:
        for arch in architectures:
            approx_8bit_file = None
            for sdir in sim_dirs:
                cands = [
                    os.path.join(sdir, "8bit", f"k{k}", f"{arch}_8bit.txt"),
                    os.path.join(sdir, f"{arch}_8bit_k{k}.txt"),
                    os.path.join(sdir, f"{arch}_8bit.txt") if k == 4 else None
                ]
                for c in cands:
                    if c and os.path.exists(c):
                        approx_8bit_file = c
                        break
                if approx_8bit_file:
                    break

            if not approx_8bit_file:
                continue

            app_in, app_exact, app_circ = parse_result_file(approx_8bit_file, 8)
            processed_files.append(approx_8bit_file)

            if len(app_in) != 65536:
                warnings_list.append(f"ALERTA: {approx_8bit_file} contem {len(app_in)} amostras (esperado: 65536).")

            if rca_8bit_data is not None:
                rca_in, rca_circ = rca_8bit_data
                validate_input_alignment(rca_8bit_file, approx_8bit_file, rca_in, app_in)
                aligned_pairs.append((os.path.basename(rca_8bit_file), f"{os.path.basename(os.path.dirname(approx_8bit_file))}/{os.path.basename(approx_8bit_file)}"))
                exact_vals = rca_circ
            else:
                warnings_list.append(f"AVISO: arquivo RCA não encontrado; usando soma exata calculada como referência.")
                exact_vals = app_exact

            metrics = compute_error_metrics(exact_vals, app_circ)
            records.append({
                "experiment": f"{arch}_8bit_k{k}_exhaustive",
                "architecture": arch.upper(),
                "bits": 8,
                "k_bits": k,
                "distribution": "exhaustive",
                **metrics
            })

    # 2. Somadores de 16 bits (Varredura de K em [4, 8, 12] x 3 Distribuicoes)
    k_16_list = [2, 3, 4, 5, 6]
    for dist in distributions:
        rca_16_file = None
        for sdir in sim_dirs:
            cands = [
                os.path.join(sdir, "16bit", "k0", f"rca_16bit_{dist}.txt"),
                os.path.join(sdir, f"rca_16bit_{dist}.txt"),
            ]
            for c in cands:
                if c and os.path.exists(c):
                    rca_16_file = c
                    break
            if rca_16_file:
                break

        rca_data = None
        if rca_16_file and os.path.exists(rca_16_file):
            rca_in, rca_exact, rca_circ = parse_result_file(rca_16_file, 16)
            validate_rca(rca_16_file, 16, rca_in, rca_exact, rca_circ)
            rca_data = (rca_in, rca_circ)
            validated_rcas.add(f"16bit/{os.path.basename(rca_16_file)}")
            processed_files.append(rca_16_file)

        for k in k_16_list:
            for arch in architectures:
                approx_16_file = None
                for sdir in sim_dirs:
                    cands = [
                        os.path.join(sdir, "16bit", f"k{k}", f"{arch}_16bit_{dist}.txt"),
                        os.path.join(sdir, f"{arch}_16bit_k{k}_{dist}.txt"),
                        os.path.join(sdir, f"{arch}_16bit_{dist}.txt") if k == 8 else None
                    ]
                    for c in cands:
                        if c and os.path.exists(c):
                            approx_16_file = c
                            break
                    if approx_16_file:
                        break

                if not approx_16_file:
                    continue

                app_in, app_exact, app_circ = parse_result_file(approx_16_file, 16)
                processed_files.append(approx_16_file)

                if rca_data is not None:
                    rca_in, rca_circ = rca_data
                    validate_input_alignment(rca_16_file, approx_16_file, rca_in, app_in)
                    aligned_pairs.append((f"16bit/{os.path.basename(rca_16_file)}", f"16bit/k{k}/{os.path.basename(approx_16_file)}"))
                    exact_vals = rca_circ
                else:
                    warnings_list.append(f"AVISO: arquivo RCA não encontrado ({rca_16_file}); usando soma exata calculada como referência.")
                    exact_vals = app_exact

                canonical_exp = f"{arch}_16bit_k{k}_{dist}"
                metrics = compute_error_metrics(exact_vals, app_circ)
                records.append({
                    "experiment": canonical_exp,
                    "architecture": arch.upper(),
                    "bits": 16,
                    "k_bits": k,
                    "distribution": dist,
                    **metrics
                })

    k_32_list = [4, 6, 8, 10]
    for dist in distributions:
        rca_32_file = None
        for sdir in sim_dirs:
            cands = [
                os.path.join(sdir, "32bit", "k0", f"rca_32bit_{dist}.txt"),
                os.path.join(sdir, f"rca_32bit_{dist}.txt"),
            ]
            for c in cands:
                if c and os.path.exists(c):
                    rca_32_file = c
                    break
            if rca_32_file:
                break

        rca_data = None
        if rca_32_file and os.path.exists(rca_32_file):
            rca_in, rca_exact, rca_circ = parse_result_file(rca_32_file, 32)
            validate_rca(rca_32_file, 32, rca_in, rca_exact, rca_circ)
            rca_data = (rca_in, rca_circ)
            validated_rcas.add(f"32bit/{os.path.basename(rca_32_file)}")
            processed_files.append(rca_32_file)

        for k in k_32_list:
            for arch in architectures:
                approx_32_file = None
                for sdir in sim_dirs:
                    cands = [
                        os.path.join(sdir, "32bit", f"k{k}", f"{arch}_32bit_{dist}.txt"),
                        os.path.join(sdir, f"{arch}_32bit_k{k}_{dist}.txt"),
                        os.path.join(sdir, f"{arch}_32bit_{dist}.txt") if k == 16 else None
                    ]
                    for c in cands:
                        if c and os.path.exists(c):
                            approx_32_file = c
                            break
                    if approx_32_file:
                        break

                if not approx_32_file:
                    continue

                app_in, app_exact, app_circ = parse_result_file(approx_32_file, 32)
                processed_files.append(approx_32_file)

                if rca_data is not None:
                    rca_in, rca_circ = rca_data
                    validate_input_alignment(rca_32_file, approx_32_file, rca_in, app_in)
                    aligned_pairs.append((f"32bit/{os.path.basename(rca_32_file)}", f"32bit/k{k}/{os.path.basename(approx_32_file)}"))
                    exact_vals = rca_circ
                else:
                    warnings_list.append(f"AVISO: arquivo RCA não encontrado ({rca_32_file}); usando soma exata calculada como referência.")
                    exact_vals = app_exact

                canonical_exp = f"{arch}_32bit_k{k}_{dist}"
                metrics = compute_error_metrics(exact_vals, app_circ)
                records.append({
                    "experiment": canonical_exp,
                    "architecture": arch.upper(),
                    "bits": 32,
                    "k_bits": k,
                    "distribution": dist,
                    **metrics
                })

    if records:
        os.makedirs(os.path.dirname(output_csv), exist_ok=True)
        fieldnames = [
            "experiment", "architecture", "bits", "k_bits", "distribution",
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
    print(f"| {'Experimento':<24} | {'Bits':^4} | {'K':^3} | {'Distribuicao':^12} | {'MAE':^8} | {'MSE':^10} | {'EP (%)':^8} | {'MRE (%)':^10} | {'Erros':^7} | {'Total':^7} |")
    print(f"|{'-'*26}|{'-'*6}|{'-'*5}|{'-'*14}|{'-'*10}|{'-'*12}|{'-'*10}|{'-'*12}|{'-'*9}|{'-'*9}|")
    for r in records:
        print(f"| {r['experiment']:<24} | {r['bits']:^4} | {r['k_bits']:^3} | {r['distribution']:^12} | {r['MAE']:8.4f} | {r['MSE']:10.2f} | {r['EP']*100:6.2f}%  | {r['MRE']*100:8.4f}% | {r['Error Count']:^7} | {r['Total Samples']:^7} |")
    print()
    print(f"Metricas de erro salvas com sucesso em: {output_csv}\n")


if __name__ == "__main__":
    evaluate_all_results()

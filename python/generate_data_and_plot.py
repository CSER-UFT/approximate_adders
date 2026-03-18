import numpy as np
import matplotlib.pyplot as plt
import os

# =========================================================
# CONFIGURAÇÕES
# =========================================================

np.random.seed(42)

N_16 = 50_000   # tamanho da entrada 16 bits
N_32 = 100_000  # tamanho da entrada 32 bits

# probabilidade de mudança de valor entre vetores consecutivos
CHANGE_PROB_16 = 0.5   
CHANGE_PROB_32 = 0.5

OUTPUT_DIR = "./data"
PLOT_DIR = "./plots"

os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(PLOT_DIR, exist_ok=True)

# =========================================================
# FUNÇÃO DE CORRELAÇÃO TEMPORAL
# =========================================================

def smooth_sequence(seq, change_prob=0.3):
    """Garante que nem todos os valores mudam simultaneamente"""
    smoothed = np.copy(seq)
    for i in range(1, len(seq)):
        if np.random.rand() > change_prob:
            smoothed[i] = smoothed[i-1]
    return smoothed

# =========================================================
# GERAÇÃO DE DISTRIBUIÇÕES
# =========================================================

def generate_uniform(bits, N):
    max_val = 2**bits
    a = np.random.randint(0, max_val, N)
    b = np.random.randint(0, max_val, N)
    return a, b

def generate_normal(bits, N):
    max_val = 2**bits - 1
    mean = max_val // 2
    std = max_val // 8
    a = np.clip(np.random.normal(mean, std, N), 0, max_val)
    b = np.clip(np.random.normal(mean, std, N), 0, max_val)
    return a.astype(np.uint64), b.astype(np.uint64)

def generate_exponential(bits, N):
    max_val = 2**bits - 1
    scale = max_val // 8
    a = np.random.exponential(scale, N)
    b = np.random.exponential(scale, N)
    a = np.clip(a, 0, max_val)
    b = np.clip(b, 0, max_val)
    return a.astype(np.uint64), b.astype(np.uint64)

# =========================================================
# SALVAR ARQUIVO
# =========================================================

def save_file(a, b, bits, dist_name):
    filename = f"{bits}_{dist_name}.txt"
    filepath = os.path.join(OUTPUT_DIR, filename)
    width = bits // 4
    with open(filepath, "w") as f:
        for x, y in zip(a, b):
            f.write(f"{int(x):0{width}X} {int(y):0{width}X}\n")
    print(f"Arquivo gerado: {filepath}")

# =========================================================
# PLOT HISTOGRAMA
# =========================================================

def plot_histogram(a, bits, dist_name):
    plt.figure()
    plt.hist(a, bins=100, color='skyblue', edgecolor='black')
    plt.title(f"{dist_name.capitalize()} Distribution ({bits}-bit)")
    plt.xlabel("Value")
    plt.ylabel("Frequency")
    plt.tight_layout()
    filename = f"{bits}bits_{dist_name}_hist.pdf"
    filepath = os.path.join(PLOT_DIR, filename)
    plt.savefig(filepath)
    plt.close()
    print(f"Histograma gerado: {filepath}")

# =========================================================
# PIPELINE PRINCIPAL
# =========================================================

def process_distribution(bits, dist_name, generator, N):
    a, b = generator(bits, N)

    # aplica suavização temporal mais agressiva para 16 bits
    change_prob = CHANGE_PROB_16 if bits == 16 else CHANGE_PROB_32
    a = smooth_sequence(a, change_prob)
    b = smooth_sequence(b, change_prob)

    save_file(a, b, bits, dist_name)
    plot_histogram(a, bits, dist_name)

def main():
    distributions = {
        "uniform": generate_uniform,
        "normal": generate_normal,
        "exponential": generate_exponential
    }

    for bits, N in [(16, N_16), (32, N_32)]:
        for name, func in distributions.items():
            process_distribution(bits, name, func, N)

if __name__ == "__main__":
    main()

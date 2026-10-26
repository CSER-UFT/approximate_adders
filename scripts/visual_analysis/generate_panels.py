import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import os
import csv
import locale
from skimage import data, io
from skimage.metrics import peak_signal_noise_ratio as psnr
from skimage.metrics import structural_similarity as ssim

plt.rcParams["axes.formatter.use_mathtext"] = True
try:
    locale.setlocale(locale.LC_NUMERIC, "pt_BR.UTF-8")
    plt.rcParams["axes.formatter.use_locale"] = True
except locale.Error:
    pass

from adders import add_exact, add_loa, add_heaa, add_hoeraa, add_herloa

N_BITS = 8
K_VALUES = [1, 2, 3, 4, 6]
K_PANEL = [2, 4, 6]
K_MAP = 4

ADDERS = [('LOA', add_loa), ('HEAA', add_heaa), ('HOERAA', add_hoeraa), ('HERLOA', add_herloa)]

def neighbor_sum(channel, add):
    # soma de cada pixel com o vizinho da direita, cada operando dividido por 2
    p = np.pad(channel.astype(np.uint32), ((0, 0), (0, 1)), mode='edge')
    return add(p[:, :-1] >> 1, p[:, 1:] >> 1)

def mean_filter(channel, add):
    # média 2x2: cada operando é dividido por 2 antes da soma, 3 somas por pixel
    p = np.pad(channel.astype(np.uint32), ((0, 1), (0, 1)), mode='edge')
    top = add(p[:-1, :-1] >> 1, p[:-1, 1:] >> 1)
    bottom = add(p[1:, :-1] >> 1, p[1:, 1:] >> 1)
    return add(top >> 1, bottom >> 1)

def apply(operation, img, add):
    if img.ndim == 2:
        return operation(img, add).astype(np.uint8)
    return np.stack([operation(img[..., c], add) for c in range(img.shape[-1])], axis=-1).astype(np.uint8)

def evaluate(operation, img):
    exact_img = apply(operation, img, lambda x, y: add_exact(x, y, N_BITS))
    channel_axis = -1 if img.ndim == 3 else None
    results = {}
    for name, func in ADDERS:
        for k in K_VALUES:
            approx_img = apply(operation, img, lambda x, y: func(x, y, k, N_BITS))
            diff = approx_img.astype(np.int32) - exact_img.astype(np.int32)
            results[(name, k)] = {
                'img': approx_img,
                'psnr': psnr(exact_img, approx_img, data_range=255) if diff.any() else float('inf'),
                'ssim': ssim(exact_img, approx_img, data_range=255, channel_axis=channel_axis),
                'mae': np.abs(diff).mean(),
                'me': diff.mean(),
                'max': np.abs(diff).max(),
            }
    return exact_img, results

def fmt(value, digits):
    return f"{value:.{digits}f}".replace(".", ",")

def show(ax, img):
    ax.imshow(img, cmap='gray', vmin=0, vmax=255)

def create_panels(label, img, exact_img, results, out_dir):
    os.makedirs(out_dir, exist_ok=True)

    # mesma escala de erro nos quatro painéis
    err_maps = {}
    for name, _ in ADDERS:
        err = np.abs(exact_img.astype(np.int32) - results[(name, K_MAP)]['img'].astype(np.int32))
        err_maps[name] = err.max(axis=-1) if err.ndim == 3 else err
    err_max = max(e.max() for e in err_maps.values())

    for name, _ in ADDERS:
        fig, axes = plt.subplots(2, 3, figsize=(12, 8))
        axes = axes.flatten()

        show(axes[0], img)
        axes[0].set_title("Imagem Original", fontsize=16, fontweight='bold')

        show(axes[1], exact_img)
        axes[1].set_title(f"{label} (RCA)\n[ N = {N_BITS} bits ]", fontsize=16, fontweight='bold')

        for idx, k in enumerate(K_PANEL):
            r = results[(name, k)]
            show(axes[idx + 2], r['img'])
            axes[idx + 2].set_title(f"{name} (K={k})\nPSNR: {fmt(r['psnr'], 1)} dB   SSIM: {fmt(r['ssim'], 4)}", fontsize=16)

        ax_err = axes[5]
        im = ax_err.imshow(err_maps[name], cmap='hot', vmin=0, vmax=max(err_max, 1))
        ax_err.set_title(f"Mapa de Calor do Erro\n{name} (K={K_MAP})", fontsize=16, fontweight='bold')

        cbar = plt.colorbar(im, ax=ax_err, fraction=0.046, pad=0.04)
        cbar.ax.tick_params(labelsize=13)
        cbar.set_label("Erro absoluto (níveis de intensidade)", fontsize=13)

        for ax in axes:
            ax.axis('off')

        plt.tight_layout()
        plt.savefig(os.path.join(out_dir, f"{name}_visual_analysis.png"), dpi=300, bbox_inches='tight')
        plt.close()

if __name__ == "__main__":
    # peppers: banco USC-SIPI
    tests = [
        ('sum', neighbor_sum, "Soma Exata", 'cameraman', data.camera()),
        ('filter', mean_filter, "Filtro Exato", 'peppers', io.imread("../../data/images/peppers.tiff")),
    ]

    rows = []
    for test, operation, label, img_name, img in tests:
        exact_img, results = evaluate(operation, img)
        create_panels(label, img, exact_img, results, f"../../plots/visual_benchmark/{test}")
        for (name, k), r in results.items():
            rows.append([test, img_name, name.lower(), N_BITS, k, f"{r['psnr']:.4f}", f"{r['ssim']:.6f}",
                         f"{r['mae']:.6f}", f"{r['me']:.6f}", int(r['max'])])

    with open("../../results/visual_metrics.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(['test', 'image', 'architecture', 'n_bits', 'k', 'psnr_db', 'ssim', 'mae', 'mean_error', 'max_error'])
        writer.writerows(rows)

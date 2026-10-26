import csv
import os
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor

import numpy as np
from skimage import io

from generate_panels import ADDERS, N_BITS, create_panels, evaluate, mean_filter

DATASET_DIR = "../../data/images/dataset_512x512"
PANEL_DIR = "../../plots/visual_benchmark/dataset"
METRICS_CSV = "../../results/dataset_filter_metrics.csv"
SUMMARY_CSV = "../../results/dataset_filter_summary.csv"
PANEL_DPI = 150


def image_ids():
    names = [f for f in os.listdir(DATASET_DIR) if f.endswith(".ppm")]
    return sorted((os.path.splitext(f)[0] for f in names), key=int)


def load(image_id):
    return io.imread(os.path.join(DATASET_DIR, f"{image_id}.ppm"))


def process(image_id):
    img = load(image_id)
    exact_img, results = evaluate(mean_filter, img)
    create_panels("Filtro Exato", img, exact_img, results, os.path.join(PANEL_DIR, image_id), dpi=PANEL_DPI)
    return [[image_id, name.lower(), N_BITS, k, f"{r['psnr']:.4f}", f"{r['ssim']:.6f}",
             f"{r['mse']:.6f}", f"{r['mae']:.6f}", f"{r['me']:.6f}", int(r['max'])]
            for (name, k), r in results.items()]


def write_metrics(rows):
    with open(METRICS_CSV, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(['image', 'architecture', 'n_bits', 'k', 'psnr_db', 'ssim', 'mse', 'mae', 'mean_error', 'max_error'])
        writer.writerows(rows)


def write_summary(rows):
    groups = defaultdict(list)
    for row in rows:
        groups[(row[1], row[3])].append(row)

    archs = [name.lower() for name, _ in ADDERS]
    keys = sorted(groups, key=lambda g: (archs.index(g[0]), g[1]))

    with open(SUMMARY_CSV, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(['architecture', 'n_bits', 'k', 'images', 'psnr_mean', 'psnr_min', 'psnr_max',
                         'ssim_mean', 'ssim_min', 'mse_mean', 'mse_max'])
        for arch, k in keys:
            g = groups[(arch, k)]
            psnr = np.array([float(r[4]) for r in g])
            ssim = np.array([float(r[5]) for r in g])
            mse = np.array([float(r[6]) for r in g])
            writer.writerow([arch, N_BITS, k, len(g), f"{psnr.mean():.4f}", f"{psnr.min():.4f}", f"{psnr.max():.4f}",
                             f"{ssim.mean():.6f}", f"{ssim.min():.6f}", f"{mse.mean():.6f}", f"{mse.max():.6f}"])


if __name__ == "__main__":
    ids = image_ids()
    with ProcessPoolExecutor() as pool:
        rows = [row for result in pool.map(process, ids) for row in result]
    write_metrics(rows)
    write_summary(rows)
    print(f"{len(ids)} imagens avaliadas: {METRICS_CSV}, {SUMMARY_CSV} e {PANEL_DIR}")

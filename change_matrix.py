import rasterio
import numpy as np
import csv

PIXEL_AREA_KM2 = (30 * 30) / 1_000_000
CLASS_NAMES = {0: "Water", 1: "Bare/Degraded", 2: "ModerateVeg", 3: "DenseVeg/Mangrove"}
N = len(CLASS_NAMES)


def load(epoch):
    with rasterio.open(f"data/classified/ogoniland_{epoch}_final.tif") as src:
        return src.read(1)


def transition_matrix(a, b):
    valid = (a >= 0) & (b >= 0)
    a_v = a[valid]
    b_v = b[valid]
    matrix = np.zeros((N, N), dtype=np.int64)
    for i in range(N):
        for j in range(N):
            matrix[i, j] = np.sum((a_v == i) & (b_v == j))
    return matrix


def print_and_save(matrix, from_label, to_label):
    area = matrix * PIXEL_AREA_KM2
    print(f"\n=== Transition {from_label} -> {to_label} (km^2) ===")
    header = "From\\To".ljust(20) + "".join(name.rjust(18) for name in CLASS_NAMES.values())
    print(header)
    for i in range(N):
        row = CLASS_NAMES[i].ljust(20) + "".join(f"{area[i, j]:18.2f}" for j in range(N))
        print(row)

    out_path = f"data/classified/transition_{from_label}_{to_label}.csv"
    with open(out_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["From\\To"] + list(CLASS_NAMES.values()))
        for i in range(N):
            writer.writerow([CLASS_NAMES[i]] + [f"{area[i, j]:.2f}" for j in range(N)])
    print(f"Saved: {out_path}")

    print("\nTop transitions (excluding no-change diagonal):")
    off_diag = [(area[i, j], CLASS_NAMES[i], CLASS_NAMES[j]) for i in range(N) for j in range(N) if i != j]
    off_diag.sort(reverse=True)
    for val, from_c, to_c in off_diag[:5]:
        print(f"  {from_c} -> {to_c}: {val:.2f} km^2")


img1990 = load("1990")
img2010 = load("2010")
img2023 = load("2023")

print_and_save(transition_matrix(img1990, img2010), "1990", "2010")
print_and_save(transition_matrix(img2010, img2023), "2010", "2023")
print_and_save(transition_matrix(img1990, img2023), "1990", "2023")

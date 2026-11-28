"""
Student 4 - Mission 5B: Leakage-Free Nearest-Centroid Classifier Evaluation.

Builds 80-dimensional clip-level embeddings:
  concat([mean(F, axis=0), std(F, axis=0)]) across 49 frames x 40 mel bands.

Splits strictly by clip_id (stratified 2/3 train = 96 clips, 1/3 test = 48 clips,
random_seed=42) to prevent intra-clip speaker/room leakage.

Standardises using training-split Laptop float32 statistics (for 16 kHz runs),
computes 6 class centroids on Laptop float32 training clips, and evaluates:
  1. Laptop float32 (16 kHz, antialias=True)
  2. ESP32 16 kHz int16 S=1.0
  3. ESP32 16 kHz int8 S=1.0
  4. ESP32 16 kHz int8 S=0.25
  5. ESP32 8 kHz int16 S=1.0 (unfiltered; trained on 8 kHz reference centroids)

Outputs:
  - student4_validation/outputs/mission5_classifier_results.json
  - student4_validation/outputs/plots/mission5_confusion_matrices.png
"""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any, Dict, List, Tuple

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from sklearn.metrics import accuracy_score, confusion_matrix, precision_recall_fscore_support
from sklearn.model_selection import train_test_split

from student4_validation.src.compare_features import try_generate_8k_aa_reference  # type: ignore

REPO_ROOT = Path(__file__).resolve().parents[2]
CLASSES = ["on", "off", "stop", "go", "_unknown", "_silence"]


def clip_embeddings(features_3d: np.ndarray) -> np.ndarray:
    """Convert (N_clips, frames, 40) features into (N_clips, 80) [mean, std] vectors."""
    if features_3d.ndim != 3:
        raise ValueError(f"Expected 3D array (clips, frames, bands), got {features_3d.shape}")
    mu = np.mean(features_3d.astype(np.float64), axis=1)
    sd = np.std(features_3d.astype(np.float64), axis=1)
    return np.concatenate([mu, sd], axis=1)


def make_clip_split(labels: np.ndarray, test_size: float = 1.0 / 3.0, seed: int = 42) -> Tuple[np.ndarray, np.ndarray]:
    """Stratified clip-level split returning disjoint train_idx and test_idx."""
    idx = np.arange(len(labels))
    train_idx, test_idx = train_test_split(
        idx,
        test_size=test_size,
        random_state=seed,
        stratify=labels,
    )
    assert len(set(train_idx) & set(test_idx)) == 0, "Train/test clip split must be disjoint"
    return np.sort(train_idx), np.sort(test_idx)


def fit_nearest_centroid(
    X_train: np.ndarray,
    y_train: np.ndarray,
    classes: List[str],
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Standardize using train_idx only and compute one centroid per class."""
    mu = np.mean(X_train, axis=0)
    sd = np.maximum(np.std(X_train, axis=0), 1e-6)
    Z_train = (X_train - mu) / sd
    centroids = np.stack([np.mean(Z_train[y_train == cls], axis=0) for cls in classes], axis=0)
    return mu, sd, centroids


def evaluate_nearest_centroid(
    setting_name: str,
    X_test: np.ndarray,
    y_test: np.ndarray,
    mu: np.ndarray,
    sd: np.ndarray,
    centroids: np.ndarray,
    classes: List[str],
) -> Dict[str, Any]:
    Z_test = (X_test - mu) / sd
    dists = np.linalg.norm(Z_test[:, None, :] - centroids[None, :, :], axis=2)
    pred_idx = np.argmin(dists, axis=1)
    y_pred = np.array([classes[i] for i in pred_idx])

    acc = float(accuracy_score(y_test, y_pred))
    prec, rec, f1, _ = precision_recall_fscore_support(
        y_test, y_pred, labels=classes, average="macro", zero_division=0
    )
    cm = confusion_matrix(y_test, y_pred, labels=classes)

    return {
        "setting": setting_name,
        "accuracy": round(acc, 4),
        "precision_macro": round(float(prec), 4),
        "recall_macro": round(float(rec), 4),
        "f1_macro": round(float(f1), 4),
        "confusion_matrix": cm.astype(int).tolist(),
    }


def save_confusion_plots(evaluations: List[Dict[str, Any]], plot_dir: Path) -> None:
    plot_dir.mkdir(parents=True, exist_ok=True)
    n = len(evaluations)
    cols = 3
    rows = int(np.ceil(n / cols))
    fig, axes = plt.subplots(rows, cols, figsize=(14, 4.4 * rows))
    axes_flat = list(np.ravel(axes))

    for ax, ev in zip(axes_flat, evaluations):
        cm = np.array(ev["confusion_matrix"])
        ax.imshow(cm, cmap="Blues", vmin=0, vmax=max(1, cm.max()))
        ax.set_title(f"{ev['setting']}\nAcc={ev['accuracy']*100:.1f}% | F1={ev['f1_macro']*100:.1f}%", fontsize=9.5)
        ax.set_xticks(range(len(CLASSES)))
        ax.set_yticks(range(len(CLASSES)))
        ax.set_xticklabels(CLASSES, rotation=35, ha="right", fontsize=8)
        ax.set_yticklabels(CLASSES, fontsize=8)
        ax.set_xlabel("Predicted", fontsize=8.5)
        ax.set_ylabel("True", fontsize=8.5)
        for i in range(cm.shape[0]):
            for j in range(cm.shape[1]):
                val = cm[i, j]
                ax.text(
                    j, i, str(val),
                    ha="center", va="center",
                    color="white" if val > cm.max() * 0.5 else "black",
                    fontsize=8,
                )

    for ax in axes_flat[n:]:
        ax.axis("off")

    fig.suptitle("Nearest-Centroid Confusion Matrices (48 Stratified Test Clips, seed=42)")
    fig.tight_layout()
    fig.savefig(plot_dir / "mission5_confusion_matrices.png", dpi=150)
    plt.close(fig)


def main() -> None:
    with np.load(REPO_ROOT / "student2_python/feature_arrays/python_ref_clips_16k_i16_S1.0_speed1.npz") as py_16k:
        clip_ids = py_16k["clip_ids"]
        labels = py_16k["labels"]
        py_16k_f32 = py_16k["features_orig_f32"]

    train_idx, test_idx = make_clip_split(labels, test_size=1.0 / 3.0, seed=42)

    X_laptop_16k = clip_embeddings(py_16k_f32)
    mu_16, sd_16, cent_16 = fit_nearest_centroid(X_laptop_16k[train_idx], labels[train_idx], CLASSES)

    evaluations: List[Dict[str, Any]] = []
    evaluations.append(
        evaluate_nearest_centroid(
            "Laptop float32 (16 kHz, AA=True)",
            X_laptop_16k[test_idx],
            labels[test_idx],
            mu_16,
            sd_16,
            cent_16,
            CLASSES,
        )
    )

    esp_16k_runs = [
        ("ESP32 16k int16 S=1.0", "student1_esp32/feature_arrays/esp32_clips_16k_i16_S1.0_speed1.npz"),
        ("ESP32 16k int8 S=1.0", "student1_esp32/feature_arrays/esp32_clips_16k_i8_S1.0.npz"),
        ("ESP32 16k int8 S=0.25", "student1_esp32/feature_arrays/esp32_clips_16k_i8_S0.25.npz"),
    ]
    for title, rel in esp_16k_runs:
        with np.load(REPO_ROOT / rel) as d:
            assert np.array_equal(d["clip_ids"], clip_ids), f"clip_id mismatch in {rel}"
            assert np.array_equal(d["labels"], labels), f"label mismatch in {rel}"
            X_esp = clip_embeddings(d["features"])
        evaluations.append(
            evaluate_nearest_centroid(title, X_esp[test_idx], labels[test_idx], mu_16, sd_16, cent_16, CLASSES)
        )

    # 8 kHz domain: use 8 kHz antialias=True reference if speech_pool.npz exists, else 8k_noaa float32 reference
    f8_aa = try_generate_8k_aa_reference()
    with np.load(REPO_ROOT / "student2_python/feature_arrays/python_ref_clips_8k_i16_S1.0_noaa.npz") as py_8k_noaa:
        assert np.array_equal(py_8k_noaa["clip_ids"], clip_ids)
        assert np.array_equal(py_8k_noaa["labels"], labels)
        py_8k_f32 = py_8k_noaa["features_orig_f32"]

    with np.load(REPO_ROOT / "student1_esp32/feature_arrays/esp32_clips_8k_i16_S1.0_noaa.npz") as esp_8k:
        assert np.array_equal(esp_8k["clip_ids"], clip_ids)
        assert np.array_equal(esp_8k["labels"], labels)
        esp_8k_feats = esp_8k["features"]

    if f8_aa is not None:
        X_8k_train_ref = clip_embeddings(f8_aa)
        label_8k = "ESP32 8k int16 S=1.0 (No AA vs 8k AA Ref)"
    else:
        X_8k_train_ref = clip_embeddings(py_8k_f32)
        label_8k = "ESP32 8k int16 S=1.0 (No AA vs 8k Ref)"

    mu_8, sd_8, cent_8 = fit_nearest_centroid(X_8k_train_ref[train_idx], labels[train_idx], CLASSES)
    X_esp_8k = clip_embeddings(esp_8k_feats)
    evaluations.append(
        evaluate_nearest_centroid(label_8k, X_esp_8k[test_idx], labels[test_idx], mu_8, sd_8, cent_8, CLASSES)
    )

    out_dir = REPO_ROOT / "student4_validation" / "outputs"
    out_dir.mkdir(parents=True, exist_ok=True)
    save_confusion_plots(evaluations, out_dir / "plots")

    # Persist trained Nearest-Centroid model parameters for full reproducibility
    model_path = out_dir / "nearest_centroid_model.npz"
    np.savez_compressed(
        model_path,
        classes=np.array(CLASSES),
        mu_16k=mu_16,
        sd_16k=sd_16,
        centroids_16k=cent_16,
        mu_8k=mu_8,
        sd_8k=sd_8,
        centroids_8k=cent_8,
        train_idx=train_idx,
        test_idx=test_idx,
        random_seed=np.int32(42),
    )

    payload = {
        "split": {
            "method": "stratified_clip_level",
            "train_clips": int(len(train_idx)),
            "test_clips": int(len(test_idx)),
            "random_seed": 42,
            "train_class_distribution": {c: int(np.sum(labels[train_idx] == c)) for c in CLASSES},
            "test_class_distribution": {c: int(np.sum(labels[test_idx] == c)) for c in CLASSES},
        },
        "classes": CLASSES,
        "evaluations": evaluations,
    }
    out_path = out_dir / "mission5_classifier_results.json"
    out_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    csv_path = out_dir / "mission5_classifier_results.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["setting", "accuracy", "precision_macro", "recall_macro", "f1_macro"])
        for ev in evaluations:
            writer.writerow([
                ev["setting"], ev["accuracy"], ev["precision_macro"], ev["recall_macro"], ev["f1_macro"],
            ])

    print(f"Wrote {out_path}, {csv_path}, and {model_path}")


if __name__ == "__main__":
    main()

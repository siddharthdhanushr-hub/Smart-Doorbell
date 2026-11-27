"""
Student 4 - Mission 5A: ESP32 vs Python Reference Feature Comparison.

Computes MAE, MSE, RMSE, MaxAbs, per-band (40) MAE, and per-class (6) MAE
across all 4 recorded hardware settings:
  - 16k_i16_S1.0_speed1
  - 16k_i8_S1.0
  - 16k_i8_S0.25
  - 8k_i16_S1.0_noaa

Note on 8k_i16_S1.0_noaa:
  When starter_files/speech_pool.npz is present, computes the 8 kHz filtered
  (antialias=True) float32 reference per Mission 5 spec. When speech_pool.npz
  is absent, uses the committed python_ref_clips_8k_i16_S1.0_noaa.npz float32
  reference and records the baseline explicitly in metadata.

Outputs:
  - student4_validation/outputs/mission5_feature_comparison.json
  - student4_validation/outputs/plots/mission5_diff_heatmaps.png
  - student4_validation/outputs/plots/mission5_per_band_mae.png
  - student4_validation/outputs/plots/mission5_per_class_mae.png
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from student2_python.src.paths import resolve_starter_dir  # type: ignore

CLASSES = ["on", "off", "stop", "go", "_unknown", "_silence"]

SETTINGS = [
    (
        "16k_i16_S1.0_speed1",
        "student1_esp32/feature_arrays/esp32_clips_16k_i16_S1.0_speed1.npz",
        "student2_python/feature_arrays/python_ref_clips_16k_i16_S1.0_speed1.npz",
    ),
    (
        "16k_i8_S1.0",
        "student1_esp32/feature_arrays/esp32_clips_16k_i8_S1.0.npz",
        "student2_python/feature_arrays/python_ref_clips_16k_i8_S1.0.npz",
    ),
    (
        "16k_i8_S0.25",
        "student1_esp32/feature_arrays/esp32_clips_16k_i8_S0.25.npz",
        "student2_python/feature_arrays/python_ref_clips_16k_i8_S0.25.npz",
    ),
    (
        "8k_i16_S1.0_noaa",
        "student1_esp32/feature_arrays/esp32_clips_8k_i16_S1.0_noaa.npz",
        "student2_python/feature_arrays/python_ref_clips_8k_i16_S1.0_noaa.npz",
    ),
]


def compute_error_metrics(
    esp32_arr: np.ndarray,
    ref_arr: np.ndarray,
    labels: np.ndarray,
) -> Dict[str, Any]:
    """Compute MAE, MSE, RMSE, MaxAbs, per-band MAE (40), and per-class MAE (6)."""
    if esp32_arr.shape != ref_arr.shape:
        raise ValueError(f"Shape mismatch: {esp32_arr.shape} vs {ref_arr.shape}")
    if not (np.all(np.isfinite(esp32_arr)) and np.all(np.isfinite(ref_arr))):
        raise ValueError("Feature arrays contain NaN or Inf values")

    diff = esp32_arr.astype(np.float64) - ref_arr.astype(np.float64)
    abs_diff = np.abs(diff)
    sq_diff = diff ** 2

    mae = float(np.mean(abs_diff))
    mse = float(np.mean(sq_diff))
    rmse = float(np.sqrt(mse))
    max_abs = float(np.max(abs_diff))

    per_band_mae = [round(float(v), 6) for v in np.mean(abs_diff, axis=(0, 1))]
    per_class_mae: Dict[str, float] = {}
    for cls in CLASSES:
        mask = labels == cls
        per_class_mae[cls] = round(float(np.mean(abs_diff[mask])), 6)

    return {
        "mae_db": round(mae, 6),
        "mse_db2": round(mse, 6),
        "rmse_db": round(rmse, 6),
        "max_abs_db": round(max_abs, 6),
        "per_band_mae_db": per_band_mae,
        "per_class_mae_db": per_class_mae,
    }


def try_generate_8k_aa_reference() -> np.ndarray | None:
    """Return (144, 49, 40) float32 8 kHz antialias=True reference if speech_pool.npz exists."""
    starter_dir = resolve_starter_dir(REPO_ROOT)
    if not (starter_dir / "speech_pool.npz").exists():
        return None

    if str(starter_dir) not in sys.path:
        sys.path.insert(0, str(starter_dir))
    import team_audio as ta  # type: ignore
    from student2_python.logmel.reference_logmel import features  # type: ignore

    feats = []
    for cid, _ in ta.clip_list(1):
        x8_aa = ta.get_clip(1, cid, fs=8000, antialias=True)
        f8_aa, _ = features(x8_aa, fs=8000, win=240, hop=160, nfft=256, mels=40, mfcc=0)
        feats.append(f8_aa)
    return np.stack(feats, axis=0)


def save_comparison_plots(
    results: Dict[str, Dict[str, Any]],
    mean_abs_heatmaps: List[Tuple[str, np.ndarray]],
    plot_dir: Path,
) -> None:
    plot_dir.mkdir(parents=True, exist_ok=True)

    # 1. Mean |ESP32 - Ref| heatmaps (40 mel bands x 49 frames)
    fig, axes = plt.subplots(2, 2, figsize=(12, 7.5), sharex=True, sharey=True)
    for ax, (tag, hm) in zip(axes.flat, mean_abs_heatmaps):
        im = ax.imshow(hm.T, origin="lower", aspect="auto", cmap="magma")
        ax.set_title(f"{tag} | MAE={results[tag]['mae_db']:.4f} dB")
        ax.set_xlabel("Frame (0..48)")
        ax.set_ylabel("Mel Band (0..39)")
        fig.colorbar(im, ax=ax, label="Mean |Diff| (dB)")
    fig.suptitle("ESP32 vs Python Reference Mean Absolute Log-Mel Difference (144 Clips)")
    fig.tight_layout()
    fig.savefig(plot_dir / "mission5_diff_heatmaps.png", dpi=150)
    plt.close(fig)

    # 2. Per-band MAE line plot
    fig, ax = plt.subplots(figsize=(10, 4.5))
    bands = np.arange(40)
    colors = {"16k_i16_S1.0_speed1": "#10b981", "16k_i8_S1.0": "#0284c7", "16k_i8_S0.25": "#f59e0b", "8k_i16_S1.0_noaa": "#e11d48"}
    for tag, metrics in results.items():
        ax.plot(bands, metrics["per_band_mae_db"], marker=".", label=tag, color=colors.get(tag))
    ax.set_title("Per-Mel-Band MAE Across All 4 Hardware Settings")
    ax.set_xlabel("HTK Mel Band Index (0..39)")
    ax.set_ylabel("MAE (dB)")
    ax.grid(True, alpha=0.3)
    ax.legend(fontsize=8.5)
    fig.tight_layout()
    fig.savefig(plot_dir / "mission5_per_band_mae.png", dpi=150)
    plt.close(fig)

    # 3. Per-class MAE grouped bar chart
    fig, ax = plt.subplots(figsize=(10, 4.5))
    x = np.arange(len(CLASSES))
    width = 0.2
    tags = list(results.keys())
    for idx, tag in enumerate(tags):
        vals = [results[tag]["per_class_mae_db"][c] for c in CLASSES]
        ax.bar(x + (idx - 1.5) * width, vals, width=width, label=tag, color=colors.get(tag))
    ax.set_xticks(x)
    ax.set_xticklabels(CLASSES)
    ax.set_title("Per-Class MAE Across All 4 Hardware Settings")
    ax.set_xlabel("Doorbell Command Class")
    ax.set_ylabel("MAE (dB)")
    ax.grid(axis="y", alpha=0.3)
    ax.legend(fontsize=8.5)
    fig.tight_layout()
    fig.savefig(plot_dir / "mission5_per_class_mae.png", dpi=150)
    plt.close(fig)


def main() -> None:
    f8_aa_ref = try_generate_8k_aa_reference()
    results: Dict[str, Dict[str, Any]] = {}
    mean_abs_heatmaps: List[Tuple[str, np.ndarray]] = []

    for tag, esp_rel, py_rel in SETTINGS:
        esp_d = np.load(REPO_ROOT / esp_rel)
        py_d = np.load(REPO_ROOT / py_rel)

        esp_feat = esp_d["features"]
        labels = esp_d["labels"]
        assert np.array_equal(esp_d["clip_ids"], py_d["clip_ids"]), f"clip_id mismatch in {tag}"

        if tag == "8k_i16_S1.0_noaa" and f8_aa_ref is not None:
            ref_orig = f8_aa_ref
            baseline_note = "8 kHz filtered (antialias=True) Python float32 reference"
        elif tag == "8k_i16_S1.0_noaa":
            ref_orig = py_d["features_orig_f32"]
            baseline_note = "8 kHz unfiltered (antialias=False) Python float32 reference (speech_pool.npz absent)"
        else:
            ref_orig = py_d["features_orig_f32"]
            baseline_note = "16 kHz filtered (antialias=True) Python float32 reference"

        metrics = compute_error_metrics(esp_feat, ref_orig, labels)
        quant_metrics = compute_error_metrics(esp_feat, py_d["features_quantised"], labels)
        metrics["vs_quantised_numpy"] = {
            "mae_db": quant_metrics["mae_db"],
            "mse_db2": quant_metrics["mse_db2"],
            "rmse_db": quant_metrics["rmse_db"],
            "max_abs_db": quant_metrics["max_abs_db"],
        }
        metrics["reference_baseline"] = baseline_note
        results[tag] = metrics

        hm = np.mean(np.abs(esp_feat.astype(np.float64) - ref_orig.astype(np.float64)), axis=0)
        mean_abs_heatmaps.append((tag, hm))

    out_dir = REPO_ROOT / "student4_validation" / "outputs"
    out_dir.mkdir(parents=True, exist_ok=True)
    save_comparison_plots(results, mean_abs_heatmaps, out_dir / "plots")

    out_path = out_dir / "mission5_feature_comparison.json"
    out_path.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(f"Wrote {out_path}")


if __name__ == "__main__":
    main()

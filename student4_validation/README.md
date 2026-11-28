# Student 4 — Validation & ML Evaluation (`student4_validation/`)

**Owner:** Student 4 (`Saakshi-babu`, `saakshibabu025@gmail.com`)  
**Team:** 1 (`Paradise`) · **Board Access Required:** **None**

---

## 1. Scripts & Outputs

| Script | Purpose | Outputs |
|---|---|---|
| `src/validate_dataset_and_packets.py` | Audits `144` clips / `7,056` clean frames / `143` excluded straddling frames, compares `skip=(10, 11, 200)` before vs after fix, and summarizes `COM11` vs `COM12` speed-ramp limits | `outputs/mission4_validation_summary.json`, `outputs/plots/mission4_*.png` |
| `src/compare_features.py` | Computes `MAE`, `MSE`, `RMSE`, `MaxAbs`, per-band (40), and per-class (6) error across all 4 hardware runs (`16k_i16`, `16k_i8_S1.0`, `16k_i8_S0.25`, `8k_i16_noaa`) | `outputs/mission5_feature_comparison.json`, `outputs/mission5_feature_comparison.csv`, `outputs/plots/mission5_*.png` |
| `src/nearest_centroid_eval.py` | Evaluates leakage-free stratified clip-level Nearest-Centroid classifier (`96` train / `48` test, `seed=42`) on `80`-dim `[mean, std]` embeddings | `outputs/mission5_classifier_results.json`, `outputs/mission5_classifier_results.csv`, `outputs/nearest_centroid_model.npz`, `outputs/plots/mission5_confusion_matrices.png` |

---

## 2. How to Run

From the repository root (`Smart-Doorbell/`):

```powershell
# Run all three analysis pipelines
py -m student4_validation.src.validate_dataset_and_packets
py -m student4_validation.src.compare_features
py -m student4_validation.src.nearest_centroid_eval

# Run unit tests (and full repo pytest suite if desired)
py -m pytest student4_validation/tests -v
```

> **Note on `8 kHz antialias=True` reference:** If `starter_files/speech_pool.npz` is present locally, `compare_features.py` and `nearest_centroid_eval.py` automatically generate the `8 kHz antialias=True` Python float32 baseline. If `speech_pool.npz` is absent, they fall back transparently to `student2_python/feature_arrays/python_ref_clips_8k_i16_S1.0_noaa.npz` (`features_orig_f32`) and record the exact baseline used in JSON metadata.

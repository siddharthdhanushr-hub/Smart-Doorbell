# Student 4 Integration Review — Dataset Validation, Feature Parity & ML Evaluation

**Component:** `student4_validation/` · **Owner:** Student 4 (`Saakshi-babu`)  
**Stage B Status:** **PASS** *(Re-run cleanly in Stage B with `speech_pool.npz` present, resolving the `8 kHz` fallback)*

---

## 1. Dataset & Packet Validation (`src/validate_dataset_and_packets.py`)

Audits `dataset/dataset_manifest.csv`, `dataset/dataset_validation.json`, `dataset/doorbell_team1_esp32_features.npz`, and Stage A hardware logs:
- **Clip Integrity:** `144 / 144` valid (`24` clips per class across 6 classes), `0` invalid, `0` clipped, `0` metadata errors, `0` non-silence duplicate recordings.
- **Clean Dataset Verification:** `7,056` finite `(7056, 40)` `float32` frames (`1,176` per class across `144` unique `clip_id`s), `143` boundary-straddling frames excluded (`np.max(first_sample % 16000) <= 15360`).
- **144-Clip Streaming Loss Accounting:** `7,200` data packets sent, `7,201` `frames_ok` (`7,200` + `1` END), `0` `seq_gaps`, `0` `dup`, `0` `bad_crc`, `0` `bad_crc_back`, `0` `lost_features`, and `all_4_runs_zero_packet_loss: true`.
- **Controlled `skip=(10, 11, 200)` Audit:** Correctly plots and verifies `0`-sample tail shift (`159,360 == ((160000 - 480) // 320) * 320`) after firmware fix vs `-960` shift before fix (`158,400`), while noting raw JSON metadata stored `expected_last_first_sample: 159520` (`BUG-05`).
- **Port Speed Limits:** `usb_com11_max_zero_loss_speed = 6.0x`, `com12_921600_max_lag_free_speed = 2.5x`, `com12_2000000_max_lag_free_speed = 6.0x`.

---

## 2. Feature Comparison (`src/compare_features.py`)

Re-executed during Stage B with `../edge_ai_assignment2/speech_pool.npz` available, upgrading `8k_i16_S1.0_noaa` from Stage A's `antialias=False` fallback (`0.002828 dB`) to the true **Mission 5 `8 kHz filtered (antialias=True)` reference**:

| Setting | Reference Baseline | MAE (dB) | MSE (dB²) | RMSE (dB) | Max \|Diff\| (dB) | Quantised NumPy MAE (dB) |
|---|---|---:|---:|---:|---:|---:|
| `16k_i16_S1.0_speed1` | `16 kHz filtered (antialias=True)` | `0.003914` | `0.000037` | `0.006064` | `0.124218` | `0.000002` (`max 0.000137`) |
| `16k_i8_S1.0` | `16 kHz filtered (antialias=True)` | `1.089735` | `2.530749` | `1.590833` | `16.425510` | `0.000002` |
| `16k_i8_S0.25` | `16 kHz filtered (antialias=True)` | `0.821018` | `6.509584` | `2.551389` | `34.247005` | `0.000001` |
| `8k_i16_S1.0_noaa` | **`8 kHz filtered (antialias=True)`** | **`8.050974`** | **`129.391002`** | **`11.375017`** | **`53.593886`** | `0.000002` |

- Peak per-band errors on `8k_i16_S1.0_noaa` hit **`27.2437 dB`**, **`31.0788 dB`**, and **`20.7926 dB`** in HTK mel bands 12–14 due to `7,348 Hz` tone aliasing into `652 Hz`.
- All plots regenerated cleanly in `student4_validation/outputs/plots/` (`mission5_diff_heatmaps.png`, `mission5_per_band_mae.png`, `mission5_per_class_mae.png`, `mission5_confusion_matrices.png`).

---

## 3. Nearest-Centroid Classification & Leakage Prevention (`src/nearest_centroid_eval.py`)

- **Zero-Leakage Split:** Stratified **clip-level** split (`train_clips = 96` [16/class], `test_clips = 48` [8/class], `random_seed = 42`). Never splits frames from the same 1-s clip across train/test.
- **Embeddings & Standardization:** `80`-dim clip vector `[mean(40), std(40)]` standardized using training split statistics only (`mu`, `sd`).
- **Stage B Results (`mission5_classifier_results.json`):**

| Evaluation Setting | Accuracy | Precision (Macro) | Recall (Macro) | F1 (Macro) |
|---|---:|---:|---:|---:|
| `Laptop float32 (16 kHz, AA=True)` | `0.7500` | `0.7495` | `0.7500` | `0.7356` |
| `ESP32 16k int16 S=1.0` | `0.7500` | `0.7495` | `0.7500` | `0.7356` |
| `ESP32 16k int8 S=1.0` | `0.6875` | `0.6968` | `0.6875` | `0.6532` |
| `ESP32 16k int8 S=0.25` | `0.6667` | `0.6462` | `0.6667` | `0.6289` |
| `ESP32 8k int16 S=1.0 (No AA vs 8k AA Ref)` | **`0.2500`** | **`0.1324`** | **`0.2500`** | **`0.1642`** |

---

## 4. Unit & Stage B Integration Tests

- `student4_validation/tests/test_metrics_and_split.py` (`5/5` passed): exact metric formulas, NaN/shape rejection, stratified split zero leakage, separable cluster check, and reproducibility + Mission 4 log checks.
- `student4_validation/tests/test_stage_b_integration.py` (`2/2` passed, added in Stage B): enforces existence of every path in `shared/frontend_api_contract.json` (`v1.1.0`) and verifies `mission5_feature_comparison.json` uses `"8 kHz filtered (antialias=True) Python float32 reference"` (`mae_db > 5.0`).

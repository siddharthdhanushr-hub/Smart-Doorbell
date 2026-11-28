# Final Dataset & Machine Learning Evaluation Report (Phase 4)

**Sources Audited:** `dataset/*`, `student4_validation/src/*`, `student4_validation/outputs/*`  
**Stage C Verdict:** **PASS**

---

## 1. Final 144-Clip Dataset Integrity Summary

- **Clips & Class Balance:** `144 / 144` clips valid (`24` clips × `6` classes: `on`, `off`, `stop`, `go`, `_unknown`, `_silence`).
- **Audio Properties:** `16,000 Hz`, mono, `1.0 s` (`16,000` samples/clip), `float32`, `0` missing files, `0` corrupt/NaN values, `0` clipped recordings (`max_abs = 0.67562`), `0` duplicate pool recordings among the 120 word clips (`speech_pool.npz`: 780 recordings).
- **Clean Labelled Feature Dataset (`doorbell_team1_esp32_features.npz` & `.csv`):**
  - Raw stream emitted `7,199` frames (`2,304,000` samples total across `144 s`).
  - `143` frames crossing consecutive 1-s boundaries (`first_sample % 16000 > 15360`) excluded cleanly.
  - **`7,056` clean single-label `(7056, 40)` `float32` frames** exported (`49` frames/clip = `1,176` frames per class).

---

## 2. Final Python vs ESP32 Feature Comparison (`mission5_feature_comparison.json`)

| Hardware Setting | Reference Baseline | MAE (dB) | MSE (dB²) | RMSE (dB) | Max \|Diff\| (dB) | vs Quantised NumPy MAE |
|---|---|---:|---:|---:|---:|---:|
| `16k_i16_S1.0_speed1` | `16 kHz filtered (AA=True) f32` | `0.003914` | `0.000037` | `0.006064` | `0.124218` | `0.000002 dB` |
| `16k_i8_S1.0` | `16 kHz filtered (AA=True) f32` | `1.089735` | `2.530749` | `1.590833` | `16.425510` | `0.000002 dB` |
| `16k_i8_S0.25` | `16 kHz filtered (AA=True) f32` | `0.821018` | `6.509584` | `2.551389` | `34.247005` | `0.000001 dB` |
| `8k_i16_S1.0_noaa` | `8 kHz filtered (AA=True) f32` | **`8.050974`** | **`129.391002`** | **`11.375017`** | **`53.593886`** | `0.000002 dB` |

- `int16 S=1.0` introduces `< 0.004 dB` total error over floating-point Python reference (`0.000002 dB` pure FFT math delta).
- `int8 S=0.25` clips loud speech peaks (reaching `34.25 dB` max error on speech while lowering silence quantization noise to `0.31 dB`).
- `8 kHz No-AA` aliases the `7,348 Hz` room tone down into `652 Hz`, producing `27.24`, `31.08`, and `20.79 dB` MAE spikes in mel bands 12–14.

---

## 3. Classifier Training, Split & Evaluation (`mission5_classifier_results.json`)

- **Model & Feature Representation:** Clip-level Nearest Centroid (`euclidean`) trained on `80`-dim `[mean(40), std(40)]` features, standardized with training split `(mu, sd)` only.
- **Data Leakage Prevention:** Deterministic stratified clip-level split (`train = 96` clips [16/class], `test = 48` clips [8/class], `random_seed = 42`). Verified `0` shared `clip_id`s between train and test (`test_stratified_clip_split_zero_leakage`).
- **Measured Classifier Metrics:**

| Evaluation Condition | Accuracy | Macro Precision | Macro Recall | Macro F1 |
|---|---:|---:|---:|---:|
| **Laptop float32 (`16 kHz`, `AA=True`)** | `0.7500` | `0.7495` | `0.7500` | `0.7356` |
| **ESP32 `16k int16 S=1.0`** | **`0.7500`** | **`0.7495`** | **`0.7500`** | **`0.7356`** |
| **ESP32 `16k int8 S=1.0`** | `0.6875` | `0.6968` | `0.6875` | `0.6532` |
| **ESP32 `16k int8 S=0.25`** | `0.6667` | `0.6462` | `0.6667` | `0.6289` |
| **ESP32 `8k int16` (No AA vs `8k AA` Ref)** | **`0.2500`** | **`0.1324`** | **`0.2500`** | **`0.1642`** |

- **Confusion Matrix Patterns (`mission5_classifier_results.json`):**
  - On `16k int16 S=1.0`: `off` (`8/8`) and `_silence` (`8/8`) classify at 100%, `on` and `stop` at `7/8`, while `go` (`2/8`) and `_unknown` (`4/8`) show expected confusion (`4` `go` test clips mapped to `on`, `4` `_unknown` mapped to `go`) given single-centroid temporal pooling (without CNN/sequential modelling).
  - Live Stage C end-to-end inference on `6` representative test-split clips from `COM11` achieved `6/6` exact predictions.

---

## 4. Dataset & Classifier Limitations

1. Audio is deterministically synthesized from `speech_pool.npz` rather than recorded from a physical I2S/PDM microphone in real rooms.
2. Small sample count (`96` train / `48` test clips) with mean+std pooling discards sub-word word-onset temporal order (`go` vs `on`).
3. `int8 S=0.25` quantization degrades precision (`0.6462`) via peak clipping, while un-filtered `8 kHz` audio destroys clean-trained accuracy (`75% → 25%`).

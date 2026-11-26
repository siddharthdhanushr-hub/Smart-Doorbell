# Student 4 — Detailed Implementation & Integration Guide
## Data Science, Validation & ML Engineer (Missions 4 & 5)

**Team:** 1 (`Paradise`) · **Primary Spec:** `../edge_ai_assignment2/README.md` (Missions 4 & 5)  
**Board Access Required:** **None.** Student 1 (Siddharth) has already completed all physical ESP32-S3 runs and published every raw log and feature array on branch `siddharth`.

---

## 1. Git & Environment Setup

```powershell
# 1. Pull latest verified deliverables from Student 1 & Student 2
git fetch origin
git checkout -b student4 origin/siddharth

# 2. Install Python dependencies (already matches Student 2 env)
py -m pip install -r student2_python/requirements.txt
# Core libs: numpy, pandas, scipy, scikit-learn, matplotlib, pytest
```

> **Ownership boundary:** Do **not** edit `edge_ai_assignment2/team_audio.py`, `edge_ai_assignment2/speech_pool.npz`, `student1_esp32/`, or `student2_python/`. Put all your code, plots, and exported CSV/JSON outputs inside `student4_validation/`.

---

## 2. Exact Inputs Ready for You (Verified Inventory)

All paths below are relative to the `Smart-Doorbell/` repo root (also indexed in `shared/frontend_api_contract.json`):

### A. Shared Configurations
- `shared/hardware_config.json` — ESP32-S3 N16R8 specs, `COM11` (native USB) & `COM12` (UART bridge), measured `INFO`.
- `shared/audio_config.json` — 6 classes (`on`, `off`, `stop`, `go`, `_unknown`, `_silence`), `144` clips (`24`/class), allowed `fs`, quantisation formula.
- `shared/logmel_config.json` — `fs=16000`, `win=480`, `hop=320`, `nfft=512`, `mels=40`, `mfcc=0`, HTK `20 Hz..fs/2`, `10*log10(max(band, 1e-10))`.

### B. Dataset & Manifest (Mission 4)
- `dataset/dataset_manifest.csv` — All 144 clips (`clip_id`, `source`, `label`, `sample_rate`, `num_channels`, `duration_s`, `sample_count`, `format`, `antialias`, `pool_index`, `pool_word`, `pool_voice`, `peak_abs`, `rms`, `clipped`, `valid`).
- `dataset/dataset_validation.json` — Summary (`144/144` valid, `0` duplicates, Team 1 room acoustics: `7347.98 Hz` whine, `100 Hz` hum, `0.007695` noise std).
- `dataset/doorbell_team1_esp32_features.npz` & `.csv` — Clean labelled ESP32 dataset (`7,056` frames = `144 × 49`, `1,176` frames/class; `143` inter-clip straddling frames excluded). Keys in `.npz`: `features (7056, 40)`, `clip_id (7056,)`, `label (7056,)`, `first_sample (7056,)`, `compute_us (7056,)`.
- `dataset/data_card.md` — Drafted data card (review and enrich with your final validation/loss summary).

### C. Packet / Frame & Controlled Data-Loss Logs (Mission 4)
- `student1_esp32/logs/mission4_skip_before_fix.json` — `skip=(10, 11, 200)` **before** firmware gap fix (`samples=159,040`, last `first_sample=158,400`, shifted `-960` samples).
- `student1_esp32/logs/mission4_skip_after_fix.json` — `skip=(10, 11, 200)` **after** firmware gap fix (`seq_gaps=3`, `samples=160,000`, last `first_sample=159,360`, **`0`-sample shift**).
- `student1_esp32/logs/mission4_com_speed_ramp.json` — `COM12` speed ramp (`1×..4×` @ `921,600` baud; `2×..8×` @ `2,000,000` baud).
- `student1_esp32/logs/mission3_optimized_results.json` — `COM11` (USB) speed sweep (`2×..10×` for `feat=False` & `feat=True`: `6×` max zero-loss, `8×` overflows 32 KB RX buffer).
- `student1_esp32/logs/phase5_144clips_all_runs.json` — Full 144-clip run logs (`speed=1.0` primary + 3 Mission 5 settings).

### D. Aligned ESP32 vs Python Feature Arrays (Mission 5)
Each pair shares exact `(144, 49, 40)` clip-aligned arrays (`clip_ids` = `0..143`, `labels` = matching class names):

| Setting | ESP32 Array (`.npz`, key `features`) | Python Array (`.npz`, keys `features_orig_f32`, `features_quantised`) |
|---|---|---|
| `16 kHz, i16, S=1.0` (`speed=1.0`) | `student1_esp32/feature_arrays/esp32_clips_16k_i16_S1.0_speed1.npz` | `student2_python/feature_arrays/python_ref_clips_16k_i16_S1.0_speed1.npz` |
| `16 kHz, i8, S=1.0` (`speed=4.0`) | `student1_esp32/feature_arrays/esp32_clips_16k_i8_S1.0.npz` | `student2_python/feature_arrays/python_ref_clips_16k_i8_S1.0.npz` |
| `16 kHz, i8, S=0.25` (`speed=4.0`) | `student1_esp32/feature_arrays/esp32_clips_16k_i8_S0.25.npz` | `student2_python/feature_arrays/python_ref_clips_16k_i8_S0.25.npz` |
| `8 kHz, i16, S=1.0` (`antialias=False`) | `student1_esp32/feature_arrays/esp32_clips_8k_i16_S1.0_noaa.npz` | `student2_python/feature_arrays/python_ref_clips_8k_i16_S1.0_noaa.npz` |

> **Important Note for `8k_i16_S1.0_noaa`:** In `python_ref_clips_8k_i16_S1.0_noaa.npz`, `features_orig_f32` was computed on `8 kHz` **unfiltered** audio (`antialias=False`). Faculty `README.md` (Mission 5, bullet 3) explicitly asks to compare the `8 kHz` unfiltered board features against **filtered `8 kHz` (`antialias=True`)** laptop features! Generate that reference easily using:
> ```python
> import sys; sys.path.insert(0, "../edge_ai_assignment2")
> import team_audio as ta
> from student2_python.logmel.reference_logmel import features
> x8_aa = ta.get_clip(1, cid, fs=8000, antialias=True)
> f8_aa, _ = features(x8_aa, fs=8000, win=240, hop=160, nfft=256, mels=40, mfcc=0)
> ```

---

## 3. Recommended Folder Structure (`student4_validation/`)

```text
student4_validation/
├── src/
│   ├── validate_dataset_and_packets.py   # Mission 4: manifest, skip before/after, COM vs USB ramp
│   ├── compare_features.py               # Mission 5: MAE/MSE/RMSE overall, per-band, per-class + heatmaps
│   └── nearest_centroid_eval.py          # Mission 5: 2/3-1/3 clip-split nearest centroid + confusion matrix
├── tests/
│   └── test_metrics_and_split.py         # Unit tests on MAE/MSE/RMSE and zero-leakage clip split
├── outputs/
│   ├── mission4_validation_summary.json  # Handover for Student 3
│   ├── mission5_feature_comparison.json  # Handover for Student 3
│   ├── mission5_classifier_results.json  # Handover for Student 3
│   └── plots/                            # PNGs: loss chart, diff heatmaps, per-band error, confusion matrix
└── README.md
```

---

## 4. Exact Implementation Blueprint

### Part 1 — Mission 4: Dataset & Packet Integrity (`validate_dataset_and_packets.py`)
1. **Dataset audit:** Load `dataset/dataset_manifest.csv` and `dataset/doorbell_team1_esp32_features.npz`. Verify:
   - `144` unique `clip_id`s (`0..143`), `24` per class, `0` invalid/NaN/duplicate pool recordings.
   - Clean frame count = `7,056` (`49` frames/clip × `144`), `1,176` frames/class; document the `143` excluded straddling frames (`first_sample = c*16000 + 15680`).
2. **Controlled packet loss (`skip=(10, 11, 200)`):**
   - Compare `mission4_skip_before_fix.json` (`seq_gaps=3`, `samples=159040`, `tail_shift = -960` samples) vs `mission4_skip_after_fix.json` (`seq_gaps=3`, `samples=160000`, `tail_shift = 0` samples).
   - Explain why `lost_features = 5` in `after_fix` even though `3` packets were skipped: packets `10, 11` (`640` samples) and packet `200` (`320` samples) disrupted overlapping 480-sample windows across those 2 gaps (`3 + 2 = 5` frames touching missing data dropped, while all remaining `494` frames kept exact `first_sample` alignment!).
3. **Port speed-limit comparison:**
   - Parse `mission4_com_speed_ramp.json` (`COM12`) and `mission3_optimized_results.json` (`COM11`).
   - Show loss rate `= (expected_samples - samples_rx) / expected_samples * 100%` and `max_lag_s` vs `speed`.
   - Highlight the key hardware insight: `COM11` (USB) has `0` loss up to `6×` (`192 kB/s`) and drops packets at `>= 8×` (`32 KB` RX overflow), whereas `COM12` (UART) never drops bytes (`0` loss) because UART TX backpressure caps speed at `~90.8 kB/s` (`921.6k`) / `~196 kB/s` (`2M`), causing `lag_s_max` to rise instead.

### Part 2 — Mission 5A: Feature Comparison (`compare_features.py`)
1. Load each `(144, 49, 40)` pair (`esp32` vs `python_orig_f32` and `esp32` vs `python_quantised`). Assert `esp32.shape == py.shape` and `np.all(np.isfinite(esp32))`.
2. Compute for each setting:
   - `MAE = mean(|E - P|)` (dB)
   - `MSE = mean((E - P)^2)` (dB²)
   - `RMSE = sqrt(MSE)` (dB)
   - `MaxAbs = max(|E - P|)` (dB)
   - **Per-band error** (mean & worst over `(clips, frames)` → shape `(40,)`)
   - **Per-class error** (mean & worst over `(24 clips, 49 frames, 40 bands)` → `6` classes)
3. Separate causes explicitly:
   - `esp32` vs `python_quantised` isolates **board math / FFT precision error** (`~0.000002 dB` MAE).
   - `esp32` vs `python_orig_f32` captures **quantisation + clipping + aliasing + math** (`0.0039 dB` for `16k i16`, `1.09 dB` for `16k i8 S=1.0`, `0.82 dB` for `16k i8 S=0.25`, and large low-band error at `652 Hz` for `8k no-AA` vs `8k AA`!).
4. Generate plots:
   - Difference heatmaps (`40 bands × 49 frames` averaged across clips or for sample clip `id=0` and `_silence id=120`) for all 4 settings.
   - Per-band & per-class MAE/RMSE bar plots.

### Part 3 — Mission 5B: Nearest-Centroid Classifier (`nearest_centroid_eval.py`)
Follow `README.md` Section 3 (Mission 5) + Section 5 Clues exactly:
1. **Clip-level feature vector (`X` shape `(144, 80)`):**
   - For each clip `c` (`49 × 40` matrix `F`), compute `mean(F, axis=0)` (`40`) and `std(F, axis=0)` (`40`), concatenate → `80` features per clip.
2. **Leakage-free train/test split:**
   ```python
   from sklearn.model_selection import train_test_split
   idx = np.arange(144)
   train_idx, test_idx = train_test_split(
       idx, test_size=1/3, random_state=42, stratify=labels
   )  # 96 train clips (16/class), 48 test clips (8/class)
   ```
   > Why clip-level split? Frames within a 1-s clip share speaker, word utterance, and noise realization; splitting frames randomly leaks speaker/recording identity across train and test.
3. **Standardisation (fit ONLY on `train_idx` of laptop `f32` features):**
   ```python
   mu = X_laptop[train_idx].mean(axis=0)
   sd = np.maximum(X_laptop[train_idx].std(axis=0), 1e-6)
   ```
4. **Nearest-Centroid Classifier:**
   - Compute 6 class centroids `C[cls] = mean(Z_train[labels[train_idx] == cls], axis=0)` on standardised laptop `f32` training clips.
   - Predict `argmin_cls ||z - C[cls]||_2` on `test_idx` for:
     1. Laptop `f32` (`16 kHz, antialias=True`) — baseline
     2. Board `16 kHz, i16, S=1.0`
     3. Board `16 kHz, i8, S=1.0`
     4. Board `16 kHz, i8, S=0.25`
     5. Board `8 kHz, i16, S=1.0, antialias=False` (use `X_8k` standardized with `8 kHz` laptop `antialias=True` `mu, sd` or evaluate cross-domain shift clearly documented!)
5. Report `accuracy`, `precision`, `recall`, `f1_score` (`macro` and `weighted` + per-class), and `confusion_matrix` (`6×6`, `CLASSES` order).

---

## 5. Exact JSON Handover Schemas for Student 3

Save these 3 JSON files in `student4_validation/outputs/` so Student 3 can ingest them directly:

1. `student4_validation/outputs/mission4_validation_summary.json`
   ```json
   {
     "dataset": {"total_clips": 144, "valid_clips": 144, "clean_frames": 7056, "excluded_straddling_frames": 143, "frames_per_class": 1176},
     "controlled_skip_test": {"skip_packets": [10, 11, 200], "before_fix_tail_shift_samples": -960, "after_fix_tail_shift_samples": 0},
     "port_limits": {"usb_com11_max_zero_loss_speed": 6.0, "com12_921600_max_lag_free_speed": 2.5, "com12_2000000_max_lag_free_speed": 6.0}
   }
   ```
2. `student4_validation/outputs/mission5_feature_comparison.json`
   - Array/dict keyed by setting (`16k_i16_S1.0_speed1`, `16k_i8_S1.0`, `16k_i8_S0.25`, `8k_i16_S1.0_noaa`) containing `mae_db`, `mse_db2`, `rmse_db`, `max_abs_db`, `per_band_mae_db` (len 40), `per_class_mae_db` (dict of 6 classes).
3. `student4_validation/outputs/mission5_classifier_results.json`
   - `split`: `{"method": "stratified_clip_level", "train_clips": 96, "test_clips": 48, "random_seed": 42}`
   - `classes`: `["on", "off", "stop", "go", "_unknown", "_silence"]`
   - `evaluations`: list of dicts per setting (`accuracy`, `precision_macro`, `recall_macro`, `f1_macro`, `confusion_matrix` 6×6).

---

## 6. Acceptance Checklist Before Handing Over to Student 3
- [ ] `pytest` unit tests pass on synthetic known arrays for MAE/MSE/RMSE and clip-split zero-leakage check.
- [ ] `8 kHz` unfiltered board comparison uses `8 kHz` **filtered (`antialias=True`)** laptop features as baseline.
- [ ] All plots include axis labels, units (`dB`, `frames`, `ms`), and setting tags.
- [ ] Commit and push `student4_validation/` to your branch (`student4`) and notify Student 3.

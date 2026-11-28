# Student 4 — Stage A Data Science, Validation & ML Review Report

**Project:** Smart Doorbell — Edge AI (`Team 1: Paradise`)  
**Scope:** Stage A Review, Verification, Bug Fixing, and Stabilization of `student4_validation/`  
**Review Date:** 2026-11-28  
**Branch Reviewed:** `student4`

---

## 1. Tasks Reviewed

1. **Dataset Validation (`student4_validation/src/validate_dataset_and_packets.py`, `student2_python/src/dataset_inspect.py`):**
   * Manifest schema & clip audit (`dataset/dataset_manifest.csv`, `dataset/dataset_validation.json`).
   * Clean ESP32 dataset audit (`dataset/doorbell_team1_esp32_features.npz` & `.csv`) and straddling-frame exclusion (`143` frames).
   * Label balance (`24` clips / `1,176` clean frames per class), duplicate pool detection, clipping/corrupted audio check, metadata validation, and `dataset/data_card.md`.
2. **Packet / Frame Integrity Analysis (`validate_dataset_and_packets.py`):**
   * Full 144-clip stream accounting (`phase5_144clips_all_runs.json` across all 4 hardware settings).
   * Controlled `skip=(10, 11, 200)` before-fix vs after-fix logs (`mission4_skip_before_fix.json`, `mission4_skip_after_fix.json`).
   * Transport speed-limit sweeps (`mission3_optimized_results.json` for USB `COM11`; `mission4_com_speed_ramp.json` for UART `COM12`).
3. **Feature Comparison (`student4_validation/src/compare_features.py`):**
   * Shape, clip ID, label, and finite-value alignment across all 4 `.npz` pairs (`16k_i16_S1.0_speed1`, `16k_i8_S1.0`, `16k_i8_S0.25`, `8k_i16_S1.0_noaa`).
   * Overall `MAE`, `MSE`, `RMSE`, `MaxAbs`, per-band (`40`), per-class (`6`), and `vs_quantised_numpy` calculations + generated plots.
4. **Machine Learning (`student4_validation/src/nearest_centroid_eval.py`):**
   * `80`-dim clip embedding (`[mean, std]` across `49 × 40`), stratified clip-level split (`96` train / `48` test, `seed=42`), train-only standardization, Nearest-Centroid fitting, accuracy, macro precision/recall/F1, and `6 × 6` confusion matrices.
5. **Reproducibility & Outputs (`student4_validation/outputs/`, `tests/test_metrics_and_split.py`, `README.md`):**
   * Deterministic seeding, saved JSON/CSV/NPZ/PNG artifacts, unit tests, and input/output path handling.

---

## 2. Tests Performed

1. **Independent From-Scratch Numerical Verification:** Python script independently recomputing dataset-to-clip NPZ parity, `MAE`/`MSE`/`RMSE` directly from raw `.npz` arrays, and `Accuracy`/`Macro Precision`/`Macro Recall`/`Macro F1` directly from the `6 × 6` confusion matrices.
2. **Pipeline Re-Execution (After Bug Fixes):**
   * `py -m student4_validation.src.validate_dataset_and_packets`
   * `py -m student4_validation.src.compare_features`
   * `py -m student4_validation.src.nearest_centroid_eval`
3. **Unit & Integration Test Suite:** `py -m pytest student4_validation/tests -v` (`5` tests covering synthetic metrics, invalid-input guards, zero-leakage stratified split, separable-cluster evaluation, split determinism, and real log integrity).
4. **Full Repository Python Test Suite Check:** `py -m pytest -v` (Student 2's 9-test suite, to verify environment & `speech_pool.npz` dependency status).
5. **Saved Model & Output Artifact Inspection:** Verified shapes/dtypes in `student4_validation/outputs/nearest_centroid_model.npz`, CSV exports, JSON schemas, and PNG plots.

---

## 3. Passed Tests

* **Student 4 Unit & Integrity Tests (`py -m pytest student4_validation/tests -v`):** **5/5 passed** (`7.93 s`):
  * `test_compute_error_metrics_exact_known_arrays` — PASSED
  * `test_compute_error_metrics_rejects_nan_and_mismatch` — PASSED
  * `test_stratified_clip_split_zero_leakage` — PASSED
  * `test_nearest_centroid_separable_clusters` — PASSED
  * `test_split_reproducibility_and_real_logs_integrity` — PASSED
* **Pipeline Re-Execution:** All 3 Student 4 scripts completed with exit code `0`, producing updated JSONs, CSVs, `nearest_centroid_model.npz`, and 6 PNG plots.
* **Student 2 Core Codec/Log-Mel Tests (`py -m pytest -v`):** **7/9 passed** (all codec, CRC/skip framing, and HTK log-mel reference tests passed).

---

## 4. Failed Tests

* **2 Tests in Student 2's Suite (`py -m pytest -v`):**
  * `student2_python/tests/test_api_server.py::test_api_endpoints_without_board` (failed at `GET /api/clips/0` with HTTP `500`)
  * `student2_python/tests/test_phase2_codec_and_protocol.py::test_clip_loader_team1`
  * **Root Cause:** Both require `starter_files/speech_pool.npz` (~13 MB, git-ignored), which is not present locally on this machine (`FileNotFoundError: speech_pool.npz must be in the same folder as team_audio.py`). **Not a Student 4 code defect.**

---

## 5. Calculation Verification

### Dataset & Frame Alignment
* `dataset/doorbell_team1_esp32_features.npz` (`(7056, 40)`) vs `esp32_clips_16k_i16_S1.0_speed1.npz` (`(144, 49, 40)` reshaped): **max absolute difference = `0.0`** (bit-identical).
* `dataset/doorbell_team1_esp32_features.csv` row count: **`7,056` rows** (`144 × 49`), `first_sample % 16000` ranges `0..15360` (`143` straddling frames at `15680` confirmed excluded).

### Feature Error Parity (`ESP32` vs `Python Reference float32`)
| Setting | Verified `MAE` (dB) | Verified `MSE` (dB²) | Verified `RMSE` (dB) | `MaxAbs` (dB) |
|---|---|---|---|---|
| `16k_i16_S1.0_speed1` | `0.003914` | `0.000037` | `0.006064` | `0.124218` |
| `16k_i8_S1.0` | `1.089735` | `2.530749` | `1.590833` | `16.425510` |
| `16k_i8_S0.25` | `0.821018` | `6.509584` | `2.551389` | `34.247005` |
| `8k_i16_S1.0_noaa` *(vs 8k no-AA)* | `0.002828` | `0.000019` | `0.004357` | `0.076488` |

### Nearest-Centroid Classifier (`96` Train / `48` Test, `seed=42`, Zero Clip Overlap)
| Setting | `Accuracy` | `Macro Precision` | `Macro Recall` | `Macro F1` |
|---|---|---|---|---|
| `Laptop float32 (16 kHz, AA=True)` | `0.7500` | `0.7495` | `0.7500` | `0.7356` |
| `ESP32 16k int16 S=1.0` | `0.7500` | `0.7495` | `0.7500` | `0.7356` |
| `ESP32 16k int8 S=1.0` | `0.6875` | `0.6968` | `0.6875` | `0.6532` |
| `ESP32 16k int8 S=0.25` | `0.6667` | `0.6462` | `0.6667` | `0.6289` |
| `ESP32 8k int16 S=1.0 (No AA vs 8k Ref)` | `0.6250` | `0.6492` | `0.6250` | `0.6137` |

*(All `MAE`, `MSE`, `RMSE`, `Accuracy`, `Precision`, `Recall`, `F1`, and `6 × 6` confusion matrix sums `= 48` matched independent NumPy recalculations.)*

---

## 6. Bugs Discovered

1. **Incomplete Dataset & Packet Metadata Audits (`validate_dataset_and_packets.py`):** `audit_dataset()` did not verify `clipped == 'True'`, `sample_rate`/`num_channels`/`sample_count`, `label in CLASSES`, `first_sample % 16000 <= 15360`, or all 4 runs in `phase5_144clips_all_runs.json` (`dup`, `bad_crc_back`, `seq_gaps`, `lost_features`); `analyze_skip_experiment()` omitted `dup`, `bad_crc`, `packet_loss_pct`, and `feature_loss_pct`; `save_plots()` subtracted an unexplained `- 160` constant; and `load_json()`/`audit_dataset()` lacked explicit missing-file diagnostics.
2. **Missing Label/Dimension Alignment & CSV Export (`compare_features.py`):** Did not assert `esp_d["labels"] == py_d["labels"]` or `(144, 49, 40)` dimensions, did not close `np.load` file handles via context managers, and did not export a CSV summary table.
3. **Missing 8 kHz Alignment Assertions, Saved Model File & CSV Export (`nearest_centroid_eval.py`):** Did not assert `clip_ids`/`labels` equality on the 8 kHz `.npz` files, did not persist trained standardization/centroid parameters to disk for reproducibility, did not include per-split class counts in `split` metadata, and did not export a classifier summary CSV.
4. **Limited Reproducibility & Real-Log Assertions in Unit Tests (`test_metrics_and_split.py`):** Lacked automated tests verifying seed-42 split determinism and real-log packet/port integrity metrics.

---

## 7. Bugs Fixed

| File | Fix Applied |
|---|---|
| `student4_validation/src/validate_dataset_and_packets.py` | Added explicit `FileNotFoundError` guards, `clipped_clips`/`metadata_errors`/`first_sample` alignment checks, 4-run packet integrity verification (`all_4_runs_zero_packet_loss`), `dup`/`bad_crc`/`packet_loss_pct`/`feature_loss_pct` in skip analysis, and explicit `((160000 - 480) // 320) * 320` formula in `save_plots()`. |
| `student4_validation/src/compare_features.py` | Added `FileNotFoundError` checks, `with np.load(...)` context managers, `(144, 49, 40)` and `labels` alignment assertions, and exported `outputs/mission5_feature_comparison.csv`. |
| `student4_validation/src/nearest_centroid_eval.py` | Added `clip_ids` and `labels` assertions across all `16 kHz` and `8 kHz` `.npz` inputs, recorded `train_class_distribution`/`test_class_distribution`, persisted trained model parameters (`outputs/nearest_centroid_model.npz`), and exported `outputs/mission5_classifier_results.csv`. |
| `student4_validation/tests/test_metrics_and_split.py` | Added `test_split_reproducibility_and_real_logs_integrity()` validating deterministic splits, zero clipping/metadata errors, skip loss percentages, and `COM11`/`COM12` speed thresholds. |
| `student4_validation/README.md` | Updated output table with `mission5_feature_comparison.csv`, `mission5_classifier_results.csv`, and `nearest_centroid_model.npz`. |

---

## 8. Tests Not Performed

1. **8 kHz Unfiltered vs 8 kHz Filtered (`antialias=True`) Python Reference Execution:** Could not execute the `antialias=True` `8 kHz` generation path (`try_generate_8k_aa_reference()`) because `starter_files/speech_pool.npz` is absent on this machine.
2. **Live Student 2 `dataset_inspect.py` Re-Generation:** `dataset_inspect.py` requires `speech_pool.npz` and was not re-run; the committed `dataset/dataset_manifest.csv` and `dataset/dataset_validation.json` were audited directly instead.

---

## 9. Remaining Issues

1. **Absence of `starter_files/speech_pool.npz`:** Until `speech_pool.npz` is placed in `starter_files/`, `8k_i16_S1.0_noaa` compares against the committed `8k_noaa` `float32` baseline (`reference_baseline` explicitly flags `"speech_pool.npz absent"`). Placing `speech_pool.npz` in `starter_files/` and re-running `compare_features.py` + `nearest_centroid_eval.py` upgrades that single comparison to `8 kHz (antialias=True)`.
2. **Uncommitted Stage A Review Updates:** The Stage A fixes in `student4_validation/` and this report (`student4_stage_A_review.md`) currently sit uncommitted in the working tree on branch `student4`.

---

## 10. Readiness for Stage B Integration

**Status: READY FOR STAGE B** (with the `speech_pool.npz` note transparently documented and pending commit/PR merge of these Stage A updates).  
All dataset audits, packet integrity calculations, `MAE`/`MSE`/`RMSE` metrics, leakage-free Nearest-Centroid evaluations, saved model parameters, CSV/JSON summaries, PNG plots, and `5/5` pytest tests are verified and reproducible.

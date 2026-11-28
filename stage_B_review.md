# Stage B Review — Full-System Cross-Module Integration (`Team 1 Paradise`)

**Repository:** `https://github.com/siddharthdhanushr-hub/Smart-Doorbell.git`  
**Baseline Reviewed:** `origin/main` at commit `ded36aa` (merged PRs #1–#10 across Students 1–4)  
**Reviewer / Hardware Host Environment:** Windows 11, Python `3.14.7` (`pytest 9.1.1`), Node.js / Vite `v6.4.6`, sibling starter assets `../edge_ai_assignment2/speech_pool.npz` present

---

## 1. Cross-Module Integration Scope Reviewed

| Module | Owner | Primary Interfaces Verified in Stage B | Stage A Status |
|---|---|---|---|
| `student1_esp32/` | Student 1 | Firmware (`doorbell_board.ino`, `features.h`, `partitions.csv`), `logs/*.json`, `feature_arrays/*.npz`, `benchmarks/*.csv` | Audited (`student1_stage_A_review.md`) |
| `student2_python/` | Student 2 | `audio_codec.py`, `reference_logmel.py`, `batch_pipeline.py`, `api/server.py` (Flask `/api/*`), `feature_arrays/*.npz` | Audited (`student2_stage_A_review.md`) |
| `student3_frontend/` | Student 3 | React 19 + TypeScript + Vite 6 dashboard (10 pages), `/api/*` proxy to Flask `:5000`, `/repo/*` Vite middleware bridge, `recordedSnapshot.ts` fallback | Audited (`student3_stage_A_review.md`) |
| `student4_validation/` | Student 4 | `validate_dataset_and_packets.py`, `compare_features.py`, `nearest_centroid_eval.py`, `outputs/*.json` & `outputs/plots/*.png` | Audited (`student4_stage_A_review.md`) |
| `shared/` & `dataset/` | Shared | `frontend_api_contract.json`, `{hardware,audio,logmel}_config.json`, `communication_protocol.json`, `dataset_manifest.csv`, `doorbell_team1_esp32_features.npz` | Cross-checked in Stage B |

---

## 2. End-to-End Tests & Verification Executed in Stage B

### 2.1 Combined Python Unit & Integration Suite
1. **Baseline (`main` @ `ded36aa`):**
   - `C:\WINDOWS\py.exe -m pytest -v student2_python/tests student4_validation/tests` → **16 passed in 13.19s**.
2. **Post-Edit Final Run (with new Stage B contract & output assertions):**
   - `C:\WINDOWS\py.exe -m pytest -v student2_python/tests student4_validation/tests` → **18 passed in 7.58s**:
     - `student2_python/tests/test_api_server.py` (`1` test): Flask endpoints work offline without physical ESP32 hardware and load real `speech_pool.npz` waveforms.
     - `student2_python/tests/test_phase2_codec_and_protocol.py` (`6` tests): quantisation (`f32`, `i16`, `i8`), CRC-32 framing, `MockBoard` skip semantics, team-1 clip loading, and mock batch pipeline.
     - `student2_python/tests/test_phase4_reference_logmel.py` (`4` tests): pure-NumPy HTK log-mel bounds, orthonormal MFCC DCT, input guardrails.
     - `student4_validation/tests/test_metrics_and_split.py` (`5` tests): exact MAE/MSE/RMSE checks, stratified clip-level 96/48 split (`zero_leakage`), real Mission 4 log invariants.
     - `student4_validation/tests/test_stage_b_integration.py` (`2` new tests): every file listed in `shared/frontend_api_contract.json` exists on disk, and Student 4 `mission5_feature_comparison.json` uses the true `8 kHz filtered (antialias=True)` baseline.

### 2.2 Student 4 Pipeline Re-Execution (`speech_pool.npz` Available)
Teammates (Students 2–4) did not have `speech_pool.npz` locally during Stage A, causing `8k_i16_S1.0_noaa` in `main` (`ded36aa`) to fall back to `"8 kHz unfiltered (antialias=False) Python float32 reference (speech_pool.npz absent)"`. Re-running all three Student 4 modules in this environment (where `../edge_ai_assignment2/speech_pool.npz` resolves automatically) produced the complete Mission 4 & 5 results:

- `py -m student4_validation.src.validate_dataset_and_packets` → **PASSED** (`144` valid clips, `24`/class, `0` invalid, `0` clipped, `0` duplicates, `0` metadata errors, `7,056` clean frames, `143` excluded straddling frames, `all_4_runs_zero_packet_loss: true`).
- `py -m student4_validation.src.compare_features` → **PASSED** (upgraded `8k_i16_S1.0_noaa` to true `8 kHz filtered (antialias=True) Python float32 reference`).
- `py -m student4_validation.src.nearest_centroid_eval` → **PASSED** (updated 5-setting evaluation + confusion matrices + model `.npz`).

#### Updated Mission 5 Feature Comparison (`student4_validation/outputs/mission5_feature_comparison.json`)

| Setting | Reference Baseline | MAE (dB) | RMSE (dB) | Max \|Diff\| (dB) | vs Quantised NumPy MAE (dB) |
|---|---|---:|---:|---:|---:|
| `16k_i16_S1.0_speed1` | `16 kHz filtered (antialias=True)` | `0.003914` | `0.006064` | `0.124218` | `0.000002` (`max 0.000137`) |
| `16k_i8_S1.0` | `16 kHz filtered (antialias=True)` | `1.089735` | `1.590833` | `16.425510` | `0.000002` |
| `16k_i8_S0.25` | `16 kHz filtered (antialias=True)` | `0.821018` | `2.551389` | `34.247005` | `0.000001` |
| `8k_i16_S1.0_noaa` | **`8 kHz filtered (antialias=True)`** *(upgraded)* | **`8.050974`** | **`11.375017`** | **`53.593886`** | `0.000002` |

Notice bands 12–14 jump to **`27.24 dB`**, **`31.08 dB`**, and **`20.79 dB`** MAE because Team 1's `7,348 Hz` room whine aliases below Nyquist into ~`652 Hz` when `antialias=False`.

#### Updated Mission 5 Nearest-Centroid Classifier Results (`student4_validation/outputs/mission5_classifier_results.json`)
Stratified clip-level split (`train_clips = 96` [16/class], `test_clips = 48` [8/class], `random_seed = 42`):

| Evaluation Setting | Accuracy | Precision (Macro) | Recall (Macro) | F1 (Macro) |
|---|---:|---:|---:|---:|
| `Laptop float32 (16 kHz, AA=True)` | `0.7500` | `0.7495` | `0.7500` | `0.7356` |
| `ESP32 16k int16 S=1.0` | `0.7500` | `0.7495` | `0.7500` | `0.7356` |
| `ESP32 16k int8 S=1.0` | `0.6875` | `0.6968` | `0.6875` | `0.6532` |
| `ESP32 16k int8 S=0.25` | `0.6667` | `0.6462` | `0.6667` | `0.6289` |
| `ESP32 8k int16 S=1.0 (No AA vs 8k AA Ref)` *(upgraded)* | **`0.2500`** | **`0.1324`** | **`0.2500`** | **`0.1642`** |

When the classifier is trained on clean `8 kHz antialias=True` audio and tested with aliased `antialias=False` ESP32 features, test accuracy collapses from **`75.0%` → `25.0%`**, quantitatively proving the Mission 5 aliasing hazard.

### 2.3 Frontend Build & Live Flask ↔ Vite End-to-End Probe
- **Dependencies (`student3_frontend/`):** `npm install` (`added 84 packages, found 0 vulnerabilities`).
- **Final Production Build (post-edit):** `npm run build` (`tsc -b && vite build`) → **PASSED** (`1652 modules transformed`, `dist/assets/index-D3RxYdlo.js 347.25 kB`, `built in 8.30s`).
- **Live Server-to-Frontend HTTP Probe (`server.py` `:5000` + Vite dev `:5174` `--host 127.0.0.1`):**
  - `GET http://127.0.0.1:5174/` → `200 [text/html] (717 B)`
  - `GET http://127.0.0.1:5174/api/health` → `200 [application/json] (129 B)` (proxied to Flask `:5000`)
  - `GET http://127.0.0.1:5174/api/configs` → `200 [application/json] (8,216 B)`
  - `GET http://127.0.0.1:5174/api/clips/12?fs=16000&antialias=true` → `200 [application/json] (419,517 B)`
  - `GET http://127.0.0.1:5174/repo/shared/frontend_api_contract.json` → `200 [application/json] (3,317 B)`
  - `GET http://127.0.0.1:5174/repo/student4_validation/outputs/mission4_validation_summary.json` → `200 [application/json] (5,110 B)`
  - `GET http://127.0.0.1:5174/repo/student4_validation/outputs/mission5_feature_comparison.json` → `200 [application/json] (5,036 B)`
  - `GET http://127.0.0.1:5174/repo/student4_validation/outputs/mission5_classifier_results.json` → `200 [application/json] (4,839 B)`
  - `GET http://127.0.0.1:5174/repo/student4_validation/outputs/plots/mission5_confusion_matrices.png` → `200 [image/png] (176,910 B)`

---

## 3. Discrepancies & Integration Gaps Found and Resolved

| # | Finding Across Modules | Severity | Resolution in Stage B |
|---|---|---|---|
| 1 | `mission5_feature_comparison.json` & `mission5_classifier_results.json` on `main` had `8k_i16_S1.0_noaa` evaluated against `antialias=False` fallback because `speech_pool.npz` was missing on teammates' laptops. | **High** (incorrect Mission 5 conclusion) | Re-ran `student4_validation.src.{validate_dataset_and_packets,compare_features,nearest_centroid_eval}` with `speech_pool.npz` present; committed true `8 kHz antialias=True` results + regenerated PNGs. |
| 2 | `shared/frontend_api_contract.json` (`1.0.0`) omitted Student 4's `student4_validation/outputs/*.json`, `.csv`, `plots/*.png`, and Vite's `/repo/*` bridge documentation. | **Medium** | Updated `shared/frontend_api_contract.json` to `1.1.0` adding `vite_repo_bridge`, `student4_*` paths, and `student4_plots`. |
| 3 | Fallback alerts in `ComparisonPage.tsx` and `MlEvaluationPage.tsx` still read as if Student 4 had not yet published/committed outputs (`"Student 4 will publish..."`, `"Student 4 has not yet committed..."`). | **Low** | Updated fallback messages to explain launching `npm run dev` for the Vite `/repo/` bridge if Student 4 outputs fail to fetch. |
| 4 | Controlled skip log anomaly (`mission4_skip_after_fix.json` reports `expected_last_first_sample: 159520`, `tail_shift_samples: -160` vs `last_5_first_samples[-1]: 159360`). | **Doc/Interpretation** (raw HW log preserved) | Confirmed `validate_dataset_and_packets.py` correctly computes `((160000 - 480) // 320) * 320 = 159360` (`0` sample misalignment after fix vs `960` samples before fix). Preserved raw JSON untouched. |
| 5 | Runtime note: Vite `/repo/` middleware is registered in `configureServer` (dev mode `npm run dev`); standalone `npm run preview` (`vite preview` tested on `127.0.0.1:4173`) did not serve the app/bridge in our check, and `dist/` alone cannot load Student 4 outputs over HTTP. | **Operational** | Documented canonical launch pair: `py student2_python/api/server.py --port 5000` + `npm run dev -- --port 5173` inside `student3_frontend/`. |

---

## 4. Tests Not Performed in Stage B & Remaining Submission Work

- **Physical ESP32-S3 Re-Run (`NOT RE-TESTED` in Stage B):** No ESP32-S3 board was connected during this Stage B session. Firmware compilation (`0` warnings) and hardware logs remain verified from Stage A (`student1_stage_A_review.md`). Flashing the patched firmware (`doorbell_board.ino`) and running a live packet smoke test remain optional if live board streaming is demonstrated.
- **Course Submission Packaging (Before Monday 30 Nov 2026):** Assemble final `team_01_module2/` technical report PDF (`<= 12` pages), Commitment Memo, and 5-minute presentation deck using the upgraded Stage B numbers and plots.

---

## 5. Stage B Integration Readiness Verdict

**READY FOR FINAL SUBMISSION & DEMO PREP.**  
All four student deliverables compile, pass all 18 automated unit and Stage B integration tests (`pytest`), build cleanly to TypeScript/Vite production assets (`npm run build`), and interoperate live over `/api/*` (Flask) + `/repo/*` (Vite) with the complete Mission 5 `8 kHz antialias=True` evaluation restored.

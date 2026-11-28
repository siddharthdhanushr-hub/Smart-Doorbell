# Stage B Master Integration Report — Smart Doorbell Edge AI (`Team 1 Paradise`)

**Repository:** `https://github.com/siddharthdhanushr-hub/Smart-Doorbell.git` (Branch reviewed: `stage-b-review` branched from `origin/main` @ `ded36aa`)  
**Team / Course:** Team 1 (`Paradise`) · AI255TBD Edge AI Module 2 (*"The Doorbell's Ears"*)  
**Date of Review:** 2026-11-28  
**Environment:** Windows 11 · Python `3.14.7` (`pytest 9.1.1`) · Node.js + Vite `v6.4.6` · `arduino-cli` (`esp32:esp32` core `3.3.12`) · Physical ESP32-S3-DevKitC-1 N16R8 connected on `COM11` (USB CDC) · Sibling `../edge_ai_assignment2/speech_pool.npz` present

---

## 1. Executive Summary

Stage B end-to-end integration testing across all four student modules (`student1_esp32/`, `student2_python/`, `student3_frontend/`, `student4_validation/`, plus `shared/` and `dataset/`) is **COMPLETE** and verified against both software test suites and a **live physical ESP32-S3-DevKitC-1 N16R8 connected on `COM11`**.

**Overall Stage B Verdict:** **PASS — READY FOR STAGE C (Submission Packaging & Live Demo Prep).**

Major Stage B findings and outcomes:
- **Firmware Build & Live Upload Verified:** `doorbell_board.ino` compiled with `--warnings all` (`0` warnings, `392,700 B` flash [2%], `33,728 B` global RAM [10%]) and flashed cleanly to physical ESP32-S3 (`MAC a4:cb:8f:d4:74:98`) on `COM11`. Post-flash `CRC flash` confirmed the `4,608,000 B` `/rec.bin` (`0x55c3d431`) LittleFS recording persisted intact across power-off and re-flash.
- **Live Hardware–Software Integration Verified on `COM11`:** Live streaming succeeded across `i16` (`16 kHz`, `speed=1.0`, `PSRAM` dump byte-identical), `f32` (`16 kHz`, `speed=1.0`), `i8` (`16 kHz S=0.25`, `speed=4.0`), achieving **`1.37e-06` to `1.67e-06 dB` MAE** vs Python `reference_logmel.py`. Controlled `skip=(0, 10, 11, 200)` and raw duplicate/corrupted CRC injection proved `seq=0` gap detection, zero-fill timeline alignment (`0` tail shift), `dup=1`, and `bad_crc=1` rejection on hardware.
- **Mission 5 `8 kHz` Aliasing Baseline Restored:** On `origin/main` (`ded36aa`), `mission5_feature_comparison.json` and `mission5_classifier_results.json` fell back to `8 kHz antialias=False` because `speech_pool.npz` was missing on teammates' laptops. Re-running Student 4's scripts with `speech_pool.npz` updated `8k_i16_S1.0_noaa` vs true `8 kHz antialias=True` (`MAE = 8.050974 dB`, `RMSE = 11.375017 dB`; classifier accuracy drops `75.00% → 25.00%`).
- **Bugs Discovered & Fixed (`BUG-01..BUG-04`):** Upgraded `8k_i16_S1.0_noaa` baseline + plots, synchronised `shared/frontend_api_contract.json` (`1.1.0`), clarified `ComparisonPage.tsx` `AA=False` vs `AA=True` table columns, updated stale awaiting text in `ComparisonPage.tsx` & `MlEvaluationPage.tsx`, and fixed `MockBoard.stream()` packet-0 skip detection in `serial_sender.py`.
- **Automated Verification After Final Edits:** `18 / 18 pytest` checks passing, `npm run build` (`tsc -b && vite build`) passing (`0` errors), and all live HTTP `/api/*` + `/repo/*` routes verified `HTTP 200` on both Vite `dev` and `preview` backed by Flask `:5000`.

---

## 2. Individual Student Review

| Student | Role | Stage B Verdict | Summary |
|---|---|---|---|
| **Student 1** | Embedded Systems & ESP32 (`student1_esp32/`) | **PASS** *(COM12 not re-plugged)* | Patched firmware compiles cleanly (`0` warnings) and flashes to `COM11`; live RT/PSRAM/Flash CRC/`f32`/`i16`/`i8`/`skip`/`bad_crc`/`dup` tests all pass; COM12 UART hardware benchmarks rely on Stage A logs (`COM12` not attached in Stage B). |
| **Student 2** | Python Backend & Audio (`student2_python/`) | **PASS** *(1 bug fixed in MockBoard)* | Pure-NumPy HTK log-mel matches ESP32 within `1.67e-06 dB` MAE live; Flask `/api/*` offline & clip routes pass; `MockBoard` initial-packet (`seq=0`) gap bug fixed and tested (`serial_sender.py`). |
| **Student 3** | Frontend Dashboard (`student3_frontend/`) | **PASS** *(headless Chrome DevTools blocked)* | `npm install` + `tsc -b && vite build` clean (`0` errors); `/api/*` + `/repo/*` return `HTTP 200` on `dev` & `preview`; fixed `ComparisonPage.tsx` baseline header clarity and outdated fallback strings. Live interactive DOM render in Chrome DevTools `NOT TESTED` (no active `DevToolsActivePort`). |
| **Student 4** | Validation & ML (`student4_validation/`) | **PASS** *(outputs upgraded in Stage B)* | All 3 pipelines + unit/contract tests pass (`7/7` in `student4_validation/tests`); `8k_i16_S1.0_noaa` upgraded to `8 kHz AA=True` reference; clip-level stratified 96/48 split prevents leakage cleanly. |

Detail reports: [student1_esp32_integration.md](student1_esp32_integration.md), [student2_python_integration.md](student2_python_integration.md), [student3_frontend_integration.md](student3_frontend_integration.md), [student4_validation_ml_integration.md](student4_validation_ml_integration.md).

---

## 3. Integration Test Results

| Test ID | Component | Test Objective | Procedure | Expected Result | Actual Result | Status | Evidence / Output File | Remarks |
|---|---|---|---|---|---|---|---|---|
| `IT-01` | Repo Inventory | Verify completeness of Students 1–4 files & configs | Recursive file listing & config inspection | All deliverables & `shared/*.json` present | 140+ tracked source/output/doc files indexed; `speech_pool.npz` via sibling dir | **PASS** | [repository_inventory.md](repository_inventory.md) | No missing code dependencies |
| `IT-02` | S1 Firmware | Compile firmware with strict warnings | `arduino-cli compile --fqbn esp32:esp32:esp32s3:... --warnings all` | 0 warnings, exit 0 | Exited 0; `392,700 B` flash (2%), `33,728 B` RAM (10%) | **PASS** | `student1_esp32/firmware/doorbell_board/` | Reproduced live |
| `IT-03` | S1 Hardware | Flash & verify post-power-cut persistence | `arduino-cli upload -p COM11`; `PING`, `INFO`, `CRC flash` | Flash succeeds & `/rec.bin` intact | Exited 0; `CRC flash`: `4,608,000 B`, `0x55c3d431` | **PASS** | Live terminal capture (`COM11`) | Bit-exact persistence preserved |
| `IT-04` | S1+S2 Live | Real-time 6-clip stream + PSRAM dump + log-mel parity | Stream 6 classes `16k i16 speed=1.0`, `DUMP psram`, compare `features` | 0 gaps, 0 bad CRC, exact PSRAM match, MAE <= 0.05 dB | `300` pkts, `299/299` feats, `MAE=1.67e-06 dB`, `683.75 us` mean, PSRAM exact | **PASS** | [hardware_software_integration.md](hardware_software_integration.md) | Live physical board |
| `IT-05` | S1+S2 Live | Multi-format codec parity (`f32` & `i8 S=0.25`) | Stream `f32 speed=1.0` & `i8 S=0.25 speed=4.0` on `COM11` | `99/99` frames, MAE <= 0.05 dB | `f32`: `MAE=1.59e-06 dB`; `i8 S=0.25`: `MAE=1.37e-06 dB`; `0` losses | **PASS** | [hardware_software_integration.md](hardware_software_integration.md) | `f32 @ speed=4.0` (`256 KB/s`) loses pkts (`75/99`), confirming USB cap |
| `IT-06` | S1+S2 Live | Controlled `skip=(0, 10, 11, 200)` & dup/bad-CRC | Send missing pkts incl. `seq=0`; send dup `seq=0` & bit-flipped CRC | `seq_gaps=4`, `last=95360`, `dup=1`, `bad_crc=1` | `seq_gaps=4`, `samples=96000`, `last=95360`; `dup=1`, `bad_crc=1` | **PASS** | [hardware_software_integration.md](hardware_software_integration.md) | Verified on patched firmware |
| `IT-07` | S1 UART | Live `COM12` UART baud/speed re-test | Test `BAUD 921600/2000000` on UART pin | Pass UART ramp | No `COM12` bridge attached in Stage B (`COM11` only) | **NOT TESTED** | `student1_esp32/logs/mission4_com_speed_ramp.json` | **HARDWARE REQUIRED (`COM12`)**; Stage A log valid |
| `IT-08` | S2+S4 Python | Combined unit, API, validation & contract tests | `py -m pytest -v student2_python/tests student4_validation/tests` | All tests pass | **`18 passed in 8.70s`** | **PASS** | `test_api_server.py`, `test_stage_b_integration.py`, etc. | Re-run after final edit |
| `IT-09` | S4 Pipeline | Regenerate Mission 4 & 5 metrics with `speech_pool.npz` | Run all 3 `student4_validation.src.*` modules | `8k_i16_S1.0_noaa` uses `8k AA=True` ref | `MAE=8.050974 dB`, `RMSE=11.375017 dB`; 8k clf acc=`0.2500` | **PASS** | `student4_validation/outputs/*.json`, `plots/*.png` | Resolves Stage A fallback |
| `IT-10` | S3 Build | TypeScript & Vite production build | `npm run build` in `student3_frontend/` | 0 TS/build errors | `✓ 1652 modules transformed`, built in `9.48s` | **PASS** | `student3_frontend/dist/` | Re-run after final edit |
| `IT-11` | S2+S3 Bridge | HTTP probe of Vite `dev`/`preview` + Flask `:5000` | Probe `/`, `/api/*`, `/repo/student4_validation/outputs/*`, PNGs | HTTP 200 with valid JSON/PNG MIME types | All 25 `dev` & 4 `preview` routes returned `HTTP 200` | **PASS** | [end_to_end_test_report.md](end_to_end_test_report.md) | `vite dev` & `vite preview` both work |
| `IT-12` | S3 Browser | Chrome DevTools interactive UI & responsive click-through | Launch `browser` subagent against `http://127.0.0.1:5174` | Zero console errors, 10 pages rendered | Chrome `DevToolsActivePort` missing (`ENOENT`) | **NOT TESTED** | — | Remote debugging inactive; HTTP + `tsc -b` + TSX audited |

---

## 4. Bugs and Fixes

| Bug ID | Severity | Affected Component | Root Cause | Fix Applied | Retest Result |
|---|---|---|---|---|---|
| `BUG-01` | **HIGH** | `student4_validation/outputs/mission5_*` | `speech_pool.npz` missing on Student 4 machine during Stage A → `8k_i16_S1.0_noaa` compared against `antialias=False` (`0.0028 dB`, `75%` acc). | Re-ran all 3 Student 4 scripts with `speech_pool.npz`; regenerated JSONs, CSVs, `.npz`, and 4 PNG plots. | **PASS** (`MAE=8.0510 dB`, acc=`25.0%`, `test_stage_b_integration.py` passes) |
| `BUG-02` | **MEDIUM** | `student3_frontend/src/pages/ComparisonPage.tsx` | Top parity table mixed `MAE vs Orig f32` (`0.002828 dB`, `AA=False`) beside Student 4's `RMSE` (`11.3750 dB`, `AA=True`) without distinguishing baselines. | Updated column headers to show `(vs 8k No-AA)` and `Student 4 MAE / RMSE (AA=True Ref)`. | **PASS** (`tsc -b && vite build` 0 errors) |
| `BUG-03` | **MEDIUM** | `shared/frontend_api_contract.json` & S3 fallback text | Contract (`1.0.0`) omitted Student 4 outputs/plots and `/repo/*` bridge; fallback alerts said outputs weren't committed. | Updated contract to `1.1.0` with `vite_repo_bridge` and `student4_*` paths; updated S3 fallback text. | **PASS** (`test_frontend_api_contract_all_paths_exist` passes) |
| `BUG-04` | **LOW** | `student2_python/transmission/serial_sender.py` | `MockBoard.stream()` checked `last_seq >= 0`, missing lost packet `seq=0` (`last_seq < 0 and rseq > 0`). | Added `if last_seq < 0 and rseq > 0: seq_gaps += rseq` matching `doorbell_board.ino`. | **PASS** (`test_frame_crc_and_mock_board_skip` passes with `skip=(0,)`) |
| `BUG-05` | **INFO / DOC** | `student1_esp32/logs/mission4_skip_after_fix.json` | Raw log recorded `expected_last_first_sample: 159520` (`160000 - 480`) rather than hop-aligned `159360`, causing `-160` reported shift. | Preserved raw hardware log untouched; `validate_dataset_and_packets.py` & report document true aligned index `159360` (`0` drift). | **DOCUMENTED** |
| `BUG-06` | **LOW (Known Limit)** | `student2_python/transmission/serial_sender.py` | `MockBoard.stream()` returns `np.zeros((0, dim))` features and does not zero-fill gap samples in `rx_buf` (`test_phase2_codec_and_protocol.py` asserts `320 * 8`). | Left intact to preserve existing unit contract; clearly flagged as simulation-only scope. | **DOCUMENTED** |

Full details: [bug_tracker.md](bug_tracker.md).

---

## 5. Hardware Limitations & Tests Not Run

1. **UART Bridge (`COM12`) Tests (`NOT TESTED – HARDWARE REQUIRED`):** Only native USB CDC (`COM11`) was plugged in during Stage B. `COM12` UART baud switching (`115.2k`, `921.6k`, `2M`), `BAUD` command, and `COM12` speed-ramp lag measurements rely on verified Stage A logs (`mission1_pipe_results.json`, `mission4_com_speed_ramp.json`).
2. **Flash Overwrite (`cmdSave()`) on `COM11`:** Preserved the existing 144-clip `/rec.bin` (`4,608,000 B`, `0x55c3d431`) untouched during live Stage B testing rather than overwriting flash with the 6-clip test; verified `CRC flash` both pre- and post-upload instead.
3. **USB CDC Throughput Ceiling:** Re-confirmed live during Stage B when `f32 @ speed=4.0` (`256 KB/s`) lost 24/99 frames on `COM11`, matching Mission 3's `192 KB/s` (`6×` i16) ceiling. Real-time streaming (`32 KB/s` `i16`, `64 KB/s` `f32`) had `0` loss.
4. **Live Chrome DevTools DOM Render (`NOT TESTED`):** Chrome remote debugging (`DevToolsActivePort`) was inactive, so interactive mouse clicks in Chrome were not executed (all HTTP responses, TypeScript compilation, Vite bundle, and component JSX bindings were verified cleanly).

---

## 6. Missing Deliverables

- **Code / Data / Configs / API / Validation / Dashboard:** None missing for Stage B code/data integration (every path in `shared/frontend_api_contract.json` exists).
- **Stage C Course Submission Package (Pending Before Final Deadline — Monday 30 Nov 2026):**
  - Final formatted Mission 1–5 PDF report (`<= 12` pages, 8 sections per mission) in `team_01_module2/`.
  - 1-page Team Contribution / Commitment Memo + LLM prediction reflection write-up.
  - 5-minute demonstration slide deck & rehearsal.

---

## 7. Integration Readiness

- **Python ↔ ESP32-S3 Serial Protocol:** Fully compatible (`0xA5 0x5A` / `0xB5 0x5B`, LE framing, CRC-32, verified live on `COM11`).
- **Audio & Log-Mel Configs (`shared/*.json`):** Consistent across firmware `features.h`, Python `reference_logmel.py`, dataset `.npz`/`.csv`, Flask `server.py`, and dashboard `ComparisonPage` / `LogMelPage`.
- **Flask `:5000` + Vite `:5173` (`/repo/*` + `/api/*`) ↔ Frontend:** Verified working together in both `dev` and `preview` modes.

---

## 8. Stage C Readiness

The project is **READY FOR STAGE C** once you run through [stage_C_readiness_checklist.md](stage_C_readiness_checklist.md): assemble the `team_01_module2/` PDF report + Commitment Memo using the **upgraded Stage B `8 kHz antialias=True` results**, optionally test live Chrome UI visually in your browser (`npm run dev` + `server.py`), and merge the approved PR after your explicit review.

# Repository Inventory — `Smart-Doorbell` (Stage B Audit)

**Generated:** 2026-11-28 · **Branch:** `stage-b-review` (based on `origin/main` @ `ded36aa`)

---

## 1. Root & Shared Files

| Path | Role | Status | Notes |
|---|---|---|---|
| `README.md` | Project quick start & role index | Present | Accurate commands (`py`, `pytest`, `server.py`) |
| `.gitignore` | Excludes `speech_pool.npz`, `node_modules`, `dist`, logs/cache | Present | Keeps `speech_pool.npz` (~13 MB) out of Git |
| `pytest.ini` | Pytest configuration (`72 B`) | Present | Configured for root test discovery |
| `pyrightconfig.json` | Type-checker config (`319 B`) | Present | Root Python typing rules |
| `student1_stage_A_review.md` | Student 1 Stage A audit | Present | `15,181 B` |
| `student2_stage_A_review.md` | Student 2 Stage A audit | Present | `18,297 B` |
| `student3_stage_A_review.md` | Student 3 Stage A audit | Present | `15,309 B` |
| `student4_stage_A_review.md` | Student 4 Stage A audit | Present | `10,918 B` |
| `stage_B_review.md` | Preliminary Stage B summary | Present | Replaced/superseded by `stage_B_review/` suite |
| `starter_files/README.md` | Unmodified faculty Mission 1–5 spec (`16,298 B`) | Present | Primary spec reference |
| `starter_files/board_link.py` | Unmodified faculty Python serial client (`10,914 B`) | Present | Used by Student 1 benchmarks |
| `starter_files/team_audio.py` | Unmodified faculty audio synthesizer (`6,079 B`) | Present | Reads `speech_pool.npz` |
| `starter_files/TEAMS.csv` | Course team room/audio config table (`2,010 B`) | Present | Team 1 (`Paradise`) row verified |
| `../edge_ai_assignment2/speech_pool.npz` | Faculty speech pool (~13 MB, outside Git) | Present (sibling dir) | Resolved cleanly by `student2_python/src/paths.py` |
| `shared/hardware_config.json` | ESP32-S3 N16R8, FQBN, USB/UART ports, memory stats | Present | Verified against `arduino-cli` & `INFO` |
| `shared/audio_config.json` | Class list, 144 clips, `f32`/`i16`/`i8` specs | Present | Verified |
| `shared/logmel_config.json` | `480/320/512/40` HTK log-mel + MFCC-13 specs | Present | Verified against `features.h` & Python |
| `shared/communication_protocol.json` | `0xA5 0x5A` / `0xB5 0x5B`, CRC-32, CLI commands | Present | Verified live on `COM11` |
| `shared/frontend_api_contract.json` | Cross-module API & file path contract (`v1.1.0`) | Updated in Stage B | Added `vite_repo_bridge` + Student 4 outputs/plots |

---

## 2. Dataset (`dataset/`)

| Path | Size | Role |
|---|---:|---|
| `dataset/data_card.md` | 2,614 B | Provenance, straddling-frame policy (`143` excluded), scope limits |
| `dataset/dataset_manifest.csv` | 17,912 B | 144 clips metadata (`clip_id`, `label`, `fs=16000`, `pool_index`, `peak_abs`, `rms`, `valid`) |
| `dataset/dataset_validation.json` | 610 B | `144/144` valid, `0` dups, Team 1 `whine=7347.98 Hz`, `hum=100 Hz`, `noise=0.007695` |
| `dataset/doorbell_team1_esp32_features.npz` | 997,477 B | Clean `7,056 x 40` `float32` ESP32 features + `clip_id`, `label`, `first_sample`, `compute_us` |
| `dataset/doorbell_team1_esp32_features.csv` | 3,249,011 B | CSV mirror of clean 7,056-frame dataset |
| `dataset/team_01_preview.wav` | 480,044 B | Team 1 preview audio (`480 KB`) |

---

## 3. Student 1 — Embedded Systems (`student1_esp32/`)

- **README / Docs (8 files):** `README.md`, `documentation/{setup_and_phase1,mission1_complete_report,mission1_predictions_and_llm_log,phase2_com12_report,mission2_complete_report,mission3_complete_report,phase5_final_handover_report}.md`
- **Firmware (5 files):**
  - Active Stage A/B build: `firmware/doorbell_board/{doorbell_board.ino, features.h, partitions.csv}`
  - Unmodified starter reference: `firmware/doorbell_board_starter/{doorbell_board_starter.ino, features.h}`
- **Benchmarks & Plots (9 files):** `benchmarks/{mission1_pipe_benchmark.py, mission1_throughput.csv, mission1_packet_size.png, mission1_speed_vs_baud.png, mission2_storage_test.py, mission3_feature_benchmark.py, mission3_suite.py, mission4_com_speed_ramp.py, mission4_packet_loss_test.py, phase5_full_pipeline.py}`
- **Hardware Feature Arrays (8 `.npz` files):**
  - `feature_arrays/esp32_raw_{16k_i16_S1.0_speed1,16k_i8_S1.0,16k_i8_S0.25,8k_i16_S1.0_noaa}.npz` (`(7199, 40)`)
  - `feature_arrays/esp32_clips_{16k_i16_S1.0_speed1,16k_i8_S1.0,16k_i8_S0.25,8k_i16_S1.0_noaa}.npz` (`(144, 49, 40)`)
- **Logs (11 JSON files):** `logs/{phase1_port_test,mission1_pipe_results,mission2_probe_baseline,mission2_save144_opi_16m,mission2_verify_opi_16m,mission3_starter_10s,mission3_optimized_results,mission4_skip_before_fix,mission4_skip_after_fix,mission4_com_speed_ramp,phase5_144clips_all_runs}.json`

---

## 4. Student 2 — Python Backend & Audio (`student2_python/`)

- **Package & Setup:** `README.md`, `requirements.txt` (includes `flask>=3.0`, `numpy`, `pyserial`, `matplotlib`, `scipy`, `pandas`, `scikit-learn`, `pytest`)
- **Source & Preprocessing:** `src/{paths.py, dataset_inspect.py, mission2_audio_analysis.py}`, `preprocessing/audio_codec.py`, `logmel/reference_logmel.py`, `transmission/{serial_sender.py, batch_pipeline.py}`
- **Backend API:** `api/server.py` (Flask `/api/health`, `/api/configs`, `/api/dataset`, `/api/clips/<id>`, `/api/benchmarks/mission1..4_5`)
- **Reference Feature Arrays (6 `.npz` files):**
  - `feature_arrays/python_ref_clips_{16k_i16_S1.0_speed1,16k_i8_S1.0,16k_i8_S0.25,8k_i16_S1.0_noaa}.npz` (`features_orig_f32`, `features_quantised`)
  - `feature_arrays/python_ref_team1_16000hz_{f32,i16}_S1.0_win480_hop320_mels40_mfcc0.npz`
- **Documentation / Plots (4 files):** `documentation/{mission2_audio_analysis.json, mission2_aliasing_spectra.png, mission2_sqnr_comparison.png, mission3_class_spectrograms.png}`
- **Tests (3 files):** `tests/{test_api_server.py, test_phase2_codec_and_protocol.py, test_phase4_reference_logmel.py}` (`11` test cases total)

---

## 5. Student 3 — Frontend Dashboard (`student3_frontend/`)

- **Docs & Config:** `README.md`, `IMPLEMENTATION_AND_INTEGRATION_GUIDE.md`, `package.json`, `package-lock.json`, `vite.config.ts`, `tsconfig.json`, `index.html`
- **Core App / Services / Types:** `src/{main.tsx, App.tsx, index.css}`, `src/types/dashboard.ts`, `src/services/api.ts`
- **Data Fallbacks:** `src/data/recorded/recordedSnapshot.ts`, `src/data/mock/mockGenerators.ts`
- **UI & Charts:** `src/components/layout/DashboardLayout.tsx`, `src/components/ui/{DataBadge,EmptyAwaitingCard,KpiCard,SectionCard}.tsx`, `src/components/charts/{BarChart,ConfusionMatrix,LineChart,SpectrogramCanvas,WaveformCanvas}.tsx`
- **Pages (10):** `src/pages/{OverviewPage,ArchitecturePage,AudioInputPage,CommunicationPage,PacketIntegrityPage,LogMelPage,HardwarePerformancePage,ComparisonPage,DatasetPage,MlEvaluationPage}.tsx`

---

## 6. Student 4 — Validation & ML (`student4_validation/`)

- **Docs:** `README.md`, `IMPLEMENTATION_AND_INTEGRATION_GUIDE.md`
- **Source (`src/`):** `validate_dataset_and_packets.py`, `compare_features.py`, `nearest_centroid_eval.py`
- **Outputs (`outputs/`):** `mission4_validation_summary.json`, `mission5_feature_comparison.{json,csv}`, `mission5_classifier_results.{json,csv}`, `nearest_centroid_model.npz`, plus 6 PNG plots in `outputs/plots/` (`mission4_port_speed_limits.png`, `mission4_skip_alignment.png`, `mission5_confusion_matrices.png`, `mission5_diff_heatmaps.png`, `mission5_per_band_mae.png`, `mission5_per_class_mae.png`)
- **Tests (`tests/`):** `test_metrics_and_split.py` (`5` tests) + `test_stage_b_integration.py` (`2` Stage B tests)

---

## 7. Inconsistencies & Duplicate Notes

- **NPZ Key Naming Convention Split:** `dataset/doorbell_team1_esp32_features.npz` uses singular keys (`clip_id`, `label`), while `student1_esp32/feature_arrays/esp32_clips_*.npz` and `student2_python/feature_arrays/*.npz` use plural keys (`clip_ids`, `labels`). Consumer code handles each correctly, verified by tests.
- **`starter_files/` Mirroring:** `starter_files/` holds exact copies of unmodified faculty files from `../edge_ai_assignment2/` (except `speech_pool.npz`, kept out of Git by `.gitignore`).
- **Missing External Assets on Teammate Machines:** Resolved here via sibling `../edge_ai_assignment2/speech_pool.npz`; teammates without it automatically trigger fallback behavior in `student4_validation` and `student3_frontend` `/api/clips/<id>`.

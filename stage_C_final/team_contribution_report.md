# Team Contribution Report (`Team 1 Paradise`)

**Course:** AI255TBD Edge AI Module 2 (*"The Doorbell's Ears"*)  
**Repository:** `https://github.com/siddharthdhanushr-hub/Smart-Doorbell.git`  
**Attribution Basis:** Direct Git commit/PR history (`git shortlog`, PRs #1–#10), Stage A review records, and Stage B/C integration execution logs.

---

## 1. Per-Student Recorded Contributions

### Student 1 — Embedded Systems & ESP32 (`student1_esp32/`, Hardware Runs)
- **Contributor Identity:** `Siddharthdhanush` / `Siddharth Dhanush R` (`24` commits/merges on GitHub).
- **Verified Contributions:**
  - ESP32-S3-DevKitC-1 N16R8 board setup, Arduino IDE / `arduino-cli` custom build config (`PSRAM=opi`, `FlashSize=16M`, `partitions.csv` `6.88 MiB` LittleFS).
  - Production firmware (`doorbell_board.ino`, `features.h`): LittleFS persistence (`SAVE`/`DUMP`/`CRC`), `HWCDC` 32 KB buffer + 256-B TX chunking, Mission 4 `seq=0` & mid-stream zero-fill alignment (`st.samples` / `skipToHop`), and iterative Cooley-Tukey radix-2 DIT FFT + twiddle/bitrev LUT + sparse HTK mel filterbank (`2,725×` speedup).
  - Executed all physical hardware benchmarks (`COM11` & `COM12`, Missions 1–4 + 4×144-clip Phase 5 extractions), consolidated repo structure, authored `student1_stage_A_review.md`, and drafted initial Student 3/4 implementation guides (`9fec295`).

### Student 2 — Python Backend & Audio Processing (`student2_python/`)
- **Contributor Identity:** `Rakshith Raghavendra` (`WhiteDevil-06`, commit `0e1df81`) working on top of the consolidated Phase 1–5 Python pipeline built with `Siddharth Dhanush R`.
- **Verified Contributions:**
  - `student2_python/src/{dataset_inspect.py,mission2_audio_analysis.py,paths.py}` — 144-clip dataset validation, aliasing/SQNR experiments, sibling asset resolution.
  - `student2_python/preprocessing/audio_codec.py` — `f32`/`i16`/`i8` codec matching Section 5 formulas.
  - `student2_python/logmel/reference_logmel.py` — Pure-NumPy HTK log-mel/MFCC baseline matching ESP32 within `<= 0.00014 dB`.
  - `student2_python/transmission/{serial_sender.py,batch_pipeline.py}` — `0xA5 0x5A` framing, `MockBoard`, `ClipLoader`, batch pipeline.
  - `student2_python/api/server.py` & Stage A hardening (`0e1df81`, PR #7) — Offline board-free Flask API, bit-length `nfft`, JSON `503` error handling, input guards, `requirements.txt` (`flask>=3.0`), and `student2_stage_A_review.md`.

### Student 3 — Frontend & Dashboard (`student3_frontend/`)
- **Contributor Identity:** `Monica` / `monicaguru10` (commits `75ba217`, `f5e7b54`; merged PRs #5, #6, #8, #10), with Stage A audit fixes & report (`d032b4d`) committed by `Saakshi-babu`.
- **Verified Contributions:**
  - Built 10-page React 19 + TypeScript + Vite 6 + Tailwind v4 engineering dashboard (`Overview`, `System Architecture`, `Audio Input`, `Communication & Throughput`, `Packet Integrity`, `Log-mel Features`, `Hardware Performance`, `Laptop vs ESP32 Comparison`, `Dataset Info`, `ML Evaluation`).
  - Custom SVG charts (`BarChart`, `LineChart`, `ConfusionMatrix`), HTML5 Canvas `WaveformCanvas` & interactive `SpectrogramCanvas`, Vite `/repo/*` + `/api/*` bridges (`vite.config.ts`), strict `DataBadge` (`Live API` vs `Recorded` vs `Mock` vs `Awaiting`) isolation, and offline `recordedSnapshot.ts` fallback.

### Student 4 — Validation & Machine Learning (`student4_validation/`)
- **Contributor Identity:** `Saakshi-babu` (commits `1b26dcd`, `cc92de3`, plus `d032b4d`).
- **Verified Contributions:**
  - `validate_dataset_and_packets.py` — 144-clip/7,056-frame integrity audit, controlled `skip=(10, 11, 200)` alignment plot (`159,360` verification), `COM11` vs `COM12` speed-ramp limits.
  - `compare_features.py` — Per-setting, per-band (40), per-class (6) `MAE`/`MSE`/`RMSE`/`MaxAbs` breakdown + difference heatmap PNGs, with automatic `8 kHz AA=True` synthesis when `speech_pool.npz` is present.
  - `nearest_centroid_eval.py` — Zero-leakage stratified clip-level split (`96` train / `48` test, `seed=42`), 80-dim `[mean, std]` Nearest-Centroid evaluation, confusion matrix generation, `test_metrics_and_split.py` (5 tests), and `student4_stage_A_review.md`.

---

## 2. Stage B & Stage C Independent Integration & Verification Attribution

- **Stage B & Stage C Integration Auditor:** **Siddharth Dhanush R** (assisted by AI engineering tooling on host laptop with physical ESP32-S3 connected on `COM11`).
- **Scope Executed in Stages B & C:** Cross-module repo audit, re-execution of Student 4 scripts with `speech_pool.npz` (`8k AA=True` fix), `shared/frontend_api_contract.json` (`v1.1.0`) sync, `ComparisonPage.tsx` & `MockBoard` bug fixes, live `COM11` firmware compile/upload/persistence/stream/E2E-ML tests, `pytest` (`18/18`), `npm run build` (`0` errors), Flask + Vite live HTTP verification, and authoring `stage_B_review/` and `stage_C_final/`.

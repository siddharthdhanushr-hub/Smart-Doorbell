# AI255TBD Edge AI — Module 2 Submission: Team 1 Paradise

**Submission Folder:** `team_01_module2/`  
**Team Name:** Team 1 (`Paradise`)  
**Target Board:** ESP32-S3-DevKitC-1 N16R8 (`16 MB` Flash, `8 MB` OPI PSRAM)  
**Submission Date:** 28 November 2026  
**Repository:** `https://github.com/siddharthdhanushr-hub/Smart-Doorbell.git`

---

## 1. Submission Contents

| # | Item Required by Faculty Rubric | Location in this Folder | Description |
|---|---|---|---|
| **1** | **Mission Records (Missions 1 to 5)** | [`team_01_module2_technical_report.pdf`](team_01_module2_technical_report.pdf) | Comprehensive PDF report featuring all **eight required headings** per mission: *1. Aim, 2. Background, 3. Prediction, 4. Method, 5. Observations, 6. Analysis, 7. What we learnt, 8. LLM log*. |
| **2** | **One-Page Commitment Memo** | [`team_01_commitment_memo.pdf`](team_01_commitment_memo.pdf) | Official 1-page client guarantee covering sampling rate, filter, format/scale auto-ranging, port/speed/headroom, storage size/room left, compute time vs budget, loss accounting, laptop-vs-board parity, and design vulnerabilities. |
| **3** | **Data Card** | [`data_card.md`](data_card.md) (and in PDF) | Official data card documenting 144 source clips, 7,056 clean frames, 143 straddling frames policy, loss proofs, and out-of-scope uses. |
| **4** | **Finished Board Sketch & Tools Settings** | [`firmware/doorbell_board/`](firmware/doorbell_board/) | Production firmware: `doorbell_board.ino`, `features.h` (radix-2 DIT FFT), `partitions.csv` (6.88 MiB LittleFS), and `tools_settings.txt`. |
| **5** | **Dataset Files** | [`dataset/`](dataset/) | Exported feature corpus: `doorbell_team1_esp32_features.npz` (7,056 × 40 float32), `doorbell_team1_esp32_features.csv`, `dataset_manifest.csv`, and `dataset_validation.json`. |
| **6** | **All Python Code** | [`python/`](python/) | Complete Python pipeline: `audio_codec.py`, `reference_logmel.py`, `serial_sender.py`, `batch_pipeline.py`, `validate_dataset_and_packets.py`, `compare_features.py`, `nearest_centroid_eval.py`, `server.py`, `test_stage_b_integration.py`. |
| **7** | **Visual Verification & Plots** | [`screenshots/`](screenshots/) | Dashboard overview screenshot (`01_dashboard_overview.png`) and all benchmark/evaluation plots. |

---

## 2. Arduino IDE Tools Settings (Exact FQBN)

To compile and flash the board sketch:
- **Board:** `ESP32S3 Dev Module`
- **USB CDC On Boot:** `Enabled`
- **Flash Size:** `16MB (128Mb)`
- **Partition Scheme:** `Custom` (`partitions.csv` located in sketch folder)
- **PSRAM:** `OPI PSRAM`
- **Core Debug Level:** `None` (or `Info` for verbose diagnostics)
- **FQBN:** `esp32:esp32:esp32s3:CDCOnBoot=cdc,FlashSize=16M,PartitionScheme=custom,PSRAM=opi`

---

## 3. Team Member Attributions

- **Student 1 — Siddharth Dhanush R:** Embedded Systems & Hardware Lead (ESP32-S3 firmware, LittleFS persistence, radix-2 FFT optimization, physical hardware execution on COM11/COM12).
- **Student 2 — Rakshith Raghavendra:** Python Backend & Audio Processing Lead (audio codec, framing protocol, NumPy reference DSP, Flask server).
- **Student 3 — Monica:** Frontend & Dashboard Developer (React 19 + Vite dashboard, Canvas spectrograms, telemetry visualization).
- **Student 4 — Saakshi Babu:** Validation & Machine Learning Engineer (loss accounting, feature comparison, Nearest-Centroid classifier, test suites).

# End-to-End Test Report (`Audio → Python → ESP32 → Validation → API → Dashboard`)

**Date:** 2026-11-28 · **Branch:** `stage-b-review`

---

## 1. End-to-End Stage Matrix

| Stage # | Data Flow Step | Input → Output Schema Verified | Status | Evidence |
|---|---|---|---|---|
| 1 | **Audio Dataset (`team_audio.py` + `dataset/`)** | 144 clips (`24`/class), `16,000 Hz`, mono, `float32`, `0` clipped, `0` dups → `dataset_manifest.csv`, `dataset_validation.json` | **PASS** | `dataset/dataset_validation.json`, `validate_dataset_and_packets.py` |
| 2 | **Python Codec (`audio_codec.py`)** | `pack()` / `unpack()` `<f4`, `<i2`, `int8` with scale `S` & SQNR (`74.21 dB` `i16`) | **PASS** | `test_phase2_codec_and_protocol.py` (`6/6`) |
| 3 | **Serial Framing (`board_link.py` / `serial_sender.py`)** | `0xA5 0x5A` + `<IH` + `payload` + IEEE `CRC-32`, `<= 4,096 B` | **PASS** | Live `COM11` Tests 1–4 + `test_phase2_codec_and_protocol.py` |
| 4 | **ESP32 Reception, PSRAM & LittleFS (`doorbell_board.ino`)** | `32 KB` ring buffer → OPI PSRAM (`192 KB` verified exact) + `/rec.bin` Flash (`4,608,000 B`, `0x55c3d431` post-flash) | **PASS** | Live `COM11` `INFO` / `DUMP psram` / `CRC flash` (`COM12` UART `NOT TESTED`) |
| 5 | **ESP32 Log-Mel (`features.h`) ↔ Downlink `0xB5 0x5B`** | `(n_frames, 40)` `float32`, `683.75 us` mean (`max 742 us`), `MAE = 1.67e-06 dB` (`i16`) | **PASS** | Live `COM11` Tests 1–2 |
| 6 | **Clean Frame Labelling (`phase5` → `dataset/*.npz/.csv`)** | `7,199` raw → `7,056` clean frames (`143` straddling excluded), `(7056, 40)` `float32` | **PASS** | `audit_dataset()`, `data_card.md` |
| 7 | **Student 4 Validation & ML (`student4_validation/`)** | `mission4_validation_summary.json`, `mission5_feature_comparison.json` (`8k AA=True` `8.051 dB` MAE), `mission5_classifier_results.json` (`16k=75%`, `8k=25%`) | **PASS** | `py -m student4_validation.tests` (`7/7`), generated JSONs/CSVs/PNGs |
| 8 | **Backend Flask API (`server.py` `:5000`)** | `/api/health`, `/api/configs`, `/api/dataset`, `/api/clips/<id>`, `/api/benchmarks/mission{1,2,3,4_5}` | **PASS** | `test_api_server.py` + live HTTP `200` probe |
| 9 | **Frontend Bridge & Build (`student3_frontend/`)** | Vite `/repo/*` + `/api/*` (`dev` & `preview`), `tsc -b && vite build` → `dist/` | **PASS** | `npm run build` (`9.48 s`), 25 HTTP `200` `dev` + 4 HTTP `200` `preview` probes (`Chrome DevTools` `NOT TESTED`) |

---

## 2. Final Re-Verification Commands & Outputs (Executed After Final Code Edit)

1. **`C:\WINDOWS\py.exe -m pytest -v student2_python/tests student4_validation/tests`**
   - Result: **`18 passed in 8.70s`** (0 failed, 0 skipped).
2. **`npm run build` (`tsc -b && vite build` inside `student3_frontend/`)**
   - Result: Exited `0` (`✓ 1652 modules transformed`, `built in 9.48s`).
3. **Vite Preview + Flask `:5000` Live Probe (`http://127.0.0.1:4173/`)**
   - `/`, `/api/health`, `/repo/student4_validation/outputs/mission5_feature_comparison.json`, `/repo/student4_validation/outputs/mission5_classifier_results.json` → all **`HTTP 200`**.
4. **Live Physical ESP32-S3 (`COM11`) Verification**
   - `arduino-cli compile --upload -p COM11 --warnings all` → `0` warnings (`392,700 B` flash / `33,728 B` RAM).
   - Post-flash `CRC flash` → `4,608,000 B`, `0x55c3d431`.
   - `TEST1` (`i16 speed=1.0`, PSRAM), `TEST2` (`f32 speed=1.0`, `i8 S=0.25 speed=4.0`), `TEST3` (`skip=(0, 10, 11, 200)`), `TEST4` (`dup=1`, `bad_crc=1`) → **all PASS**.

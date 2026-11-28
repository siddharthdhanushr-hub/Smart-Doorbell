# Smart Doorbell Edge AI ("The Doorbell's Ears") — Final Technical Report

**Team 1 (`Paradise`)** · **Course:** AI255TBD Edge AI (Module 2) · **Date:** 2026-11-28  
**Repository:** `https://github.com/siddharthdhanushr-hub/Smart-Doorbell.git` (`stage-b-review`)

---

## 1. Project Title
**Smart Doorbell Edge AI ("The Doorbell's Ears"): End-to-End Embedded Audio Acquisition, Persistent Flash Storage, Real-Time Radix-2 Log-Mel Extraction, Validation, and Full-Stack Diagnostics on ESP32-S3-DevKitC-1 N16R8**

---

## 2. Abstract
Deploying keyword spotting at the edge requires tight coordination across serial transport, memory tiers, fixed/floating-point digital signal processing (DSP), dataset hygiene, and numerical validation. This project implements a complete four-student Smart Doorbell audio pipeline centered on the `ESP32-S3-DevKitC-1 N16R8` (`240 MHz`, `16 MB` Flash, `8 MB` OPI PSRAM). Streaming 144 deterministic one-second clips (`6` classes: `on`, `off`, `stop`, `go`, `_unknown`, `_silence`) over CRC-32 framed USB CDC (`COM11`) and WCH UART (`COM12`), we resolve internal SRAM (`142,070 B`) bottlenecks using `8 MB` OPI PSRAM and a custom `6.88 MiB` LittleFS partition (`4,608,000 B` `/rec.bin`, bit-exact `CRC 0x55c3d431` surviving power cuts), optimize on-board `40`-band HTK log-mel computation from `1,863.4 ms` to **`683.7–685.2 us`** (`2,725×` speedup, `3.4%` CPU load) matching pure-NumPy within `0.000137 dB` max error (`1.45e-06–1.87e-06 dB` MAE live), validate `7,056` clean frames with a clip-split Nearest-Centroid accuracy of **`75.00%`** (`16 kHz i16`) vs **`25.00%`** under un-filtered `8 kHz` aliasing (`8.0510 dB` MAE), and expose all telemetry through Flask and a 10-page React dashboard.

---

## 3. Introduction
Smart doorbell voice front-ends operate under strict latency, memory, and communication budgets. Sending raw `16 kHz` PCM continuously to the cloud exhausts link bandwidth and raises privacy concerns, while naive embedded DSP implementations fail real-time frame deadlines or introduce subtle window/mel/filterbank mismatches relative to Python training code. Module 2 (*"The Doorbell's Ears"*) treats the ESP32-S3 as a deterministic acoustic accelerator paired with a Python host across five engineering missions and a full-stack diagnostic interface.

---

## 4. Problem Statement
Design, implement, benchmark, and validate a reproducible embedded audio + ML pipeline that:
1. Characterizes UART (`COM12`) vs native USB CDC (`COM11`) throughput, packet framing overhead, and RX buffer limits.
2. Quantifies aliasing and quantization distortion across sampling rates (`48k`, `16k`, `8k`) and data types (`f32`, `i16`, `i8`) and fits a complete 144-clip (`4.608 MB`) corpus persistently on device.
3. Achieves real-time (`<= 20 ms` hop) ESP32 log-mel feature extraction with `<= 0.05 dB` parity against a NumPy reference.
4. Recovers clean sample timestamps (`first_sample`) under packet loss (`skip`) and prevents inter-clip boundary leakage or train/test split leakage.
5. Quantifies how quantization and aliasing affect downstream classifier performance and presents verified data transparently on a dashboard.

---

## 5. Project Objectives
- Match Python pure-NumPy and ESP32 C++ HTK log-mel feature extraction within `0.05 dB`.
- Sustain zero-loss real-time `16 kHz i16` streaming (`32,000 B/s`) and survive power loss via LittleFS flash persistence.
- Deliver an audit-ready, balanced 144-clip / 7,056-frame dataset with complete packet accounting (`seq`, `CRC-32`, `dup`).
- Integrate all four students' codebases behind shared JSON contracts (`shared/`), offline Flask `/api/*`, Vite `/repo/*`, automated unit/integration tests, and live Stage B/C physical hardware verification.

---

## 6. System Architecture
Audio flows from deterministic synthesis (`team_audio.py`) → Python codec (`audio_codec.py`) → `0xA5 0x5A` CRC-32 frames (`board_link.py` / `serial_sender.py`) → `COM11`/`COM12` → ESP32-S3 `doorbell_board.ino` (32 KB RX ring buffer, zero-fill gap alignment, `8 MB` OPI PSRAM, `6.88 MiB` LittleFS `/rec.bin`) → `features.h` radix-2 FFT + sparse HTK mel filterbank → `0xB5 0x5B` `'F'`/`'S'` downlink → clean dataset export (`doorbell_team1_esp32_features.npz`) → Student 4 validation (`validate_dataset_and_packets.py`, `compare_features.py`, `nearest_centroid_eval.py`) → Flask API (`server.py`) & Vite static bridge (`/repo/*`) → 10-page React dashboard (`student3_frontend/`).

---

## 7. Hardware Requirements
- **MCU Board:** `ESP32-S3-DevKitC-1 N16R8` (Dual-core Xtensa LX7 @ `240 MHz`, `40 MHz` XTAL, `16 MB` Quad/Octal Flash, `8 MB` OPI PSRAM, `MAC a4:cb:8f:d4:74:98`).
- **Interfaces:** Native USB CDC port (`COM11`) and WCH USB-to-UART bridge (`COM12`, default `921,600` baud, tested `115.2k`–`2M`).
- **Build Target (Arduino Core `3.3.12`):** `esp32:esp32:esp32s3:CDCOnBoot=cdc,FlashSize=16M,PartitionScheme=custom,PSRAM=opi` with custom `partitions.csv` (`4.5 MB` APP ×2, `6.88 MiB` LittleFS).

---

## 8. Software Requirements
- **Embedded (`student1_esp32/`):** Arduino C++ (`doorbell_board.ino`, `features.h`, `<LittleFS.h>`, `esp_heap_caps.h`).
- **Python (`student2_python/` & `student4_validation/`):** `Python 3.14+` with `numpy>=1.24`, `pyserial>=3.5`, `matplotlib>=3.7`, `scipy>=1.10`, `pandas>=2.0`, `scikit-learn>=1.3`, `flask>=3.0`, `pytest>=7.4`.
- **Frontend (`student3_frontend/`):** Node.js + `npm`, `react@19`, `vite@6`, `tailwindcss@4`, `typescript`.

---

## 9. Dataset Description
Generated deterministically via `starter_files/team_audio.py` for Team 1 (`Paradise`) from `speech_pool.npz` (`780` word recordings @ `22,050 Hz` `int16`) mixed with Team 1 simulated room noise (`7,347.98 Hz` switching-regulator whine @ `0.0505` amplitude, `100.0 Hz` mains hum, `0.007695` Gaussian noise):
- **Clips:** `144` valid 1-s clips (`24` clips per class across `on`, `off`, `stop`, `go`, `_unknown`, `_silence`).
- **Integrity:** `0` invalid clips, `0` clipped clips (global peak abs = `0.67562`), `0` non-silence duplicates (`dataset/dataset_validation.json`).
- **Exported Clean Feature Corpus (`dataset/doorbell_team1_esp32_features.npz` & `.csv`):** `7,056 × 40` `float32` (`49` frames/clip × `144` = `1,176` frames/class), obtained after excluding `143` inter-clip boundary frames out of `7,199` streamed frames.

---

## 10. Audio Preprocessing
Downsampling from `48 kHz` (`team_audio.py`) applies a 255-tap Blackman windowed-sinc anti-aliasing filter when `antialias=True`. On silence clip `id=120`, Team 1's `7,348.0 Hz` tone (`-31.97 dB` at `48 kHz`) aliases cleanly to **`652.0 Hz` (`-31.94 dB`)** at `8 kHz` (`antialias=False`); enabling `antialias=True` suppresses that alias by **`51.82 dB`** down to **`-83.76 dB`**. Across 144 clips at `16 kHz antialias=True`, `audio_codec.py` yields **`74.21 dB`** mean SQNR (`min 61.84 dB`, `0%` clipping) for `i16 S=1.0` (`32,000 B/s`) vs `25.98 dB` (`i8 S=1.0`) and `16.25 dB` (`i8 S=0.25`, `1.694%` word clipping). Shipping configuration is **`fs=16000 Hz`, `antialias=True`, `fmt=i16`, `scale=1.0`**.

---

## 11. Serial Communication
Both host (`board_link.py`, `serial_sender.py`) and firmware use little-endian binary frames: `0xA5 0x5A | type(1B) | seq(u32) | len(u16) | payload(<=4096B) | crc32(u32)` uplink and `0xB5 0x5B` downlink (`CRC-32` IEEE `0xEDB88320` over `type + seq + len + payload`). `COM12` UART rates track the 10-bit wire clock cleanly (`11.4 kB/s` @ `115.2k`, `90.9 kB/s` @ `921.6k`, `194.7 kB/s` @ `2M`, `0` errors); `COM11` USB CDC ignores baud, peaks up to `~334–559 kB/s` in unthrottled bursts, and hits an RX overflow wall at **`>= 256 KB/s`** (`8×` `i16` / `4×` `f32`). At `speed=1.0`, both `COM11` and `COM12 >= 921.6k` deliver `0` gaps and `0` bad CRCs.

---

## 12. ESP32 Audio Reception and Storage
- **RX & Gap Recovery (`doorbell_board.ino`):** `32,768 B` RX/TX serial buffers (`Serial.setRxBufferSize` / `setTxBufferSize`) + 256-B chunked `writeAll()` eliminate USB TX drops during `DUMP flash`. Missing packets (including `seq=0`) insert zero bytes into `storeBuf`, increment `st.samples`, reset `fcount = 0`, and realign `skipToHop` so post-gap `'F'` frames keep exact `first_sample` alignment.
- **Storage Hierarchy:** Default internal SRAM capped contiguous allocation at `142,070 B` (`4.44 s`). Enabling `PSRAM=opi` unlocked `8,388,608 B` volatile PSRAM (`4,608,000 B` stored with `CRC` match), and `SAVE` wrote `/rec.bin` (`4,628,480 / 7,208,960 B` used) to LittleFS in `10.56 s`. Post-power-cut and post-firmware-flash checks verified flash `CRC 0x55c3d431` (`4,608,000 B`) intact while PSRAM reset to `0 B`.

---

## 13. Log-Mel Feature Extraction
`features.h` implements an iterative Cooley-Tukey radix-2 DIT FFT with precomputed bit-reversal and twiddle LUTs (`twRe`, `twIm`) plus sparse non-zero mel filter bounds `[melStart[m], melEnd[m])` (`53,636 B` dynamic heap). Matching `student2_python/logmel/reference_logmel.py`: symmetric Hann (`480`), `512`-pt FFT, unnormalized power `/512`, `40` HTK mel filters (`20 Hz..8,000 Hz`), `10*log10(max(m, 1e-10))`. Optimization reduced per-frame compute from `1,863,425.25 us` (starter DFT) to **`683.71–685.19 us`** (`2,725×` faster, `3.4%` of 20 ms hop); secondary `MFCC-13` (`win=400, hop=160`) runs in `714.22 us` (`7.1%` of 10 ms hop, `7,300 B/s` downlink).

---

## 14. Feature Comparison
Across all 4 committed hardware 144-clip arrays vs Python float32 references (`mission5_feature_comparison.json`):
- **`16k_i16_S1.0_speed1`:** `MAE = 0.003914 dB`, `RMSE = 0.006064 dB`, `max = 0.124218 dB` (`MAE vs quantised NumPy = 0.000002 dB`).
- **`16k_i8_S1.0`:** `MAE = 1.089735 dB`, `RMSE = 1.590833 dB`, `max = 16.425510 dB`.
- **`16k_i8_S0.25`:** `MAE = 0.821018 dB`, `RMSE = 2.551389 dB`, `max = 34.247005 dB` (clipping distortion on speech peaks).
- **`8k_i16_S1.0_noaa` vs `8 kHz AA=True` Ref:** **`MAE = 8.050974 dB`**, `MSE = 129.391002 dB²`, **`RMSE = 11.375017 dB`**, `max = 53.593886 dB` (bands 12–14 reach `27.24`, `31.08`, `20.79 dB` MAE from `7,348 Hz` alias).

---

## 15. Dataset Validation
`validate_dataset_and_packets.py` confirms `144/144` valid clips, `0` duplicates/metadata errors, `7,056` clean finite frames (`first_sample % 16000 <= 15360`), `7,200` uplink / `7,199` downlink frames with `0` gaps/CRCs/dups across all 4 hardware runs, and `0`-sample post-fix timeline shift (`159,360 == ((160000-480)//320)*320`) vs `-960` pre-fix (`158,400`) on `skip=(10, 11, 200)`.

---

## 16. Machine Learning Implementation
Using `nearest_centroid_eval.py` (stratified clip-level split: `96` train / `48` test clips, `seed=42`, `80`-dim `[mean, std]` standardized features):
- **`Laptop f32 (16k AA=True)` & `ESP32 16k i16 S=1.0`:** Identical confusion matrices — **`75.00%` Accuracy**, `0.7495` Precision, `0.7500` Recall, `0.7356` F1.
- **`ESP32 16k i8 S=1.0` / `S=0.25`:** `68.75%` (`0.6532` F1) and `66.67%` (`0.6289` F1).
- **`ESP32 8k i16 (No-AA vs 8k AA=True Ref)`:** Collapses to **`25.00%` Accuracy** (`0.1642` F1), proving anti-aliasing filter necessity.

---

## 17. Frontend and Dashboard
`student3_frontend/` implements a 10-page React 19 + TypeScript + Vite 6 + Tailwind v4 dashboard (`Overview`, `System Architecture`, `Audio Input`, `Communication`, `Packet Integrity`, `Log-Mel`, `Hardware Performance`, `Comparison`, `Dataset`, `ML Evaluation`) backed by Flask `:5000` (`/api/*`), Vite `/repo/*` static serving (`dev` and `preview`), `recordedSnapshot.ts` fallback, and explicitly badged `mockGenerators.ts`. Build (`tsc -b && vite build`) passes cleanly and all `/`, `/api/*`, `/repo/*` routes return `HTTP 200`.

---

## 18. Experimental Results
See [`stage_C_final/final_experimental_results.md`](final_experimental_results.md) for the consolidated 20-metric verification table covering every measured quantity, unit, source, and measurement method.

---

## 19. Performance Analysis
With `features.h` optimized to **`683.7–685.2 us/frame`** (`3.4%` CPU duty cycle on `20 ms` hops), feature computation has ~29× real-time headroom. Instead, **serial ingress (`32 KB` RX buffer ceiling at `>= 256 KB/s` on `COM11` USB CDC)** or **UART wire clock (`921.6k`/`2M` backpressure lag above `2.5×`/`6×`)** dictates maximum acceleration factor. Choosing `16 kHz i16 S=1.0` (`32 KB/s`) runs comfortably inside both `COM11` and `COM12 >= 921.6k` limits while matching laptop float32 ML accuracy (`75.00%`).

---

## 20. Testing and Verification
All Stage C checks executed on `2026-11-28`:
- **Python Unit & Integration Tests (`pytest`):** **`18 passed in 3.99s`**.
- **ESP32 Firmware Build (`arduino-cli --warnings all`):** `0` warnings (`392,700 B` flash / `33,728 B` RAM).
- **Live Physical Hardware (`COM11`, `task-934` & Stage B hardware suite):** `POST_FLASH_CRC_FLASH` (`0x55c3d431`), `f32`/`i16`/`i8` live parity (`1.37e-06`–`1.67e-06 dB`), `skip=(0, 10, 11, 200)`, `dup=1`/`bad_crc=1` injection, and **6/6 live held-out test-split end-to-end predictions** across all 6 classes (`heap_free` `295,828 → 295,504 B`).
- **Frontend Build & API/Repo Probe (`task-937`):** `npm run build` (`4.01 s`, 0 errors) and 10 HTTP `200` endpoint checks across `vite preview` `:4173` + Flask `:5000`.
- **Untested in Stage C:** `COM12` UART hardware (`NOT TESTED – HARDWARE REQUIRED`) and Chrome DevTools automated UI click-through (`DevToolsActivePort` missing).

---

## 21. Limitations
1. Synthesized audio streamed over USB serial (`team_audio.py`) rather than live I2S/PDM microphone capture.
2. Small 144-clip corpus (`48` test clips) with mean+std frame pooling restricts separability between short words like `go` and `on`.
3. `COM11` USB CDC drops burst traffic `>= 256 KB/s`.
4. `MockBoard` offline simulator tracks framing/CRC/sequence gaps (`skip=(0,)`) without running log-mel DSP.

---

## 22. Future Improvements
1. Port INT8 keyword-spotting CNN inference onto ESP32-S3 with ESP-NN + INMP441 I2S DMA mic capture.
2. Serve `dist/` & Student 4 JSON/PNG artifacts directly from `server.py` for single-command standalone UI hosting.
3. Add DMA queue separation on Core 0 to raise USB RX burst ceiling above `256 KB/s`.

---

## 23. Conclusion
Team 1 (`Paradise`) delivered a verified, reproducible, end-to-end Edge AI acoustic pipeline across Students 1–4. Live hardware tests on `ESP32-S3-DevKitC-1 N16R8` (`COM11`) confirm `~684 us` on-device HTK log-mel compute, `<= 1.87e-06 dB` MAE against Python on live streams, bit-exact `4.608 MB` LittleFS persistence across power loss and re-flash, exact `75.00%` classifier parity with laptop float32 (`16 kHz i16`), and full diagnostic visualization in the dashboard (`2. READY WITH MINOR ISSUES` pending final `team_01_module2/` PDF export and GitHub PR #11 merge approval).

---

## 24. References
1. Faculty Specification: `starter_files/README.md` (`AI255TBD Edge AI Module 2: The Doorbell's Ears`).
2. Shared Configs & API Contract: `shared/{hardware_config,audio_config,logmel_config,communication_protocol,frontend_api_contract}.json`.
3. Firmware & Benchmarks: `student1_esp32/firmware/doorbell_board/{doorbell_board.ino,features.h,partitions.csv}`, `student1_esp32/logs/*.json`.
4. Python Reference, Codec & Flask API: `student2_python/{preprocessing/audio_codec.py,logmel/reference_logmel.py,transmission/serial_sender.py,api/server.py}`.
5. Frontend Dashboard: `student3_frontend/src/` & `student3_frontend/vite.config.ts`.
6. Validation & ML Pipeline: `student4_validation/src/{validate_dataset_and_packets,compare_features,nearest_centroid_eval}.py` & `student4_validation/outputs/*.json`.
7. Stage A, B & C Audits: `student{1..4}_stage_A_review.md`, `stage_B_review/`, `stage_C_final/`.

# Final System Architecture — Smart Doorbell Edge AI (`Team 1 Paradise`)

**Target Hardware:** `ESP32-S3-DevKitC-1 N16R8` (Dual-core Xtensa LX7 @ `240 MHz`, `16 MB` Flash, `8 MB` OPI PSRAM, `MAC a4:cb:8f:d4:74:98`)  
**Software Stack:** Python `3.14.7` (NumPy/SciPy/PySerial/Flask) + Arduino C++ (`esp32:esp32` `3.3.12`) + React 19 / TypeScript / Vite 6

---

## 1. End-to-End Pipeline Architecture

```text
[1. Audio Dataset]          starter_files/team_audio.py + speech_pool.npz (144 clips, 6 classes, Team 1 noise)
        │
        ▼
[2. Python Preprocessing]   student2_python/preprocessing/audio_codec.py
        │                   fs=16,000 Hz, antialias=True (255-tap Blackman), f32 / i16 / i8 + scale S
        ▼
[3. Serial Transport]       board_link.py / serial_sender.py (0xA5 0x5A + type + u32 seq + u16 len + payload + CRC-32)
        │                   Links: COM11 (USB CDC, <=192 KB/s) | COM12 (WCH UART @ 921.6k / 2M baud)
        ▼
[4. ESP32 Reception & Mem]  student1_esp32/firmware/doorbell_board/doorbell_board.ino
        │                   32 KB RX Ring Buffer -> gap detection & zero-fill -> OPI PSRAM (8 MB) <-> LittleFS (/rec.bin, 6.88 MiB)
        ▼
[5. Embedded Feature DSP]   student1_esp32/firmware/doorbell_board/features.h
        │                   win=480 Hann -> zero-pad 512 -> Radix-2 DIT FFT (LUT) -> |X|^2/512 -> 40 HTK Mel (20..8kHz) -> 10*log10
        ▼
[6. Downlink & Parity]      0xB5 0x5B ('F' frames: first_sample + compute_us + float32[40]; 'S' summary stats)
        │                   student2_python/logmel/reference_logmel.py (exact pure-NumPy parity <= 0.00014 dB)
        ▼
[7. Clean Dataset & Audit]  dataset/doorbell_team1_esp32_features.{npz,csv} (7,056 clean frames; 143 straddling excluded)
        │                   student4_validation/src/validate_dataset_and_packets.py
        ▼
[8. Feature & ML Eval]      student4_validation/src/{compare_features,nearest_centroid_eval}.py
        │                   MAE/MSE/RMSE + stratified clip-split (96 train / 48 test) 80-dim Nearest Centroid
        ▼
[9. Backend API & UI]       student2_python/api/server.py (Flask /api/*) + Vite /repo/* <-> student3_frontend/ (10 React pages)
```

---

## 2. Partitioning & Memory Map (`partitions.csv`)

- **`nvs` (`0x9000`, `20 KB`):** Non-volatile Wi-Fi/system config
- **`otadata` (`0xe000`, `8 KB`) + `app0` (`0x10000`, `4.5 MB`) + `app1` (`0x490000`, `4.5 MB`):** Dual OTA app slots (current firmware `doorbell_board.ino` occupies **`392,700 B`**)
- **`spiffs` / LittleFS (`0x910000`, `0x6E0000` = `7,208,960 B` / `6.88 MiB`):** Stores persistent `/rec.bin` (`4,608,000 B` for all 144 clips)
- **OPI PSRAM (`8,388,608 B`):** Volatile runtime buffer (`store="psram"`) for full multi-minute audio capture without internal SRAM exhaustion
- **Internal SRAM (`320 KB` DRAM):** Firmware static `.bss`/`.data` (`33,728 B`) + dynamic FFT/Mel tables (`53,636 B` for `nfft=512, mels=40`)

---

## 3. Shared Cross-Module Contracts (`shared/`)

- `shared/hardware_config.json` — Board specs, Arduino IDE FQBN (`CDCOnBoot=cdc,FlashSize=16M,PartitionScheme=custom,PSRAM=opi`), COM ports.
- `shared/audio_config.json` — Class labels, 144-clip counts, quantisation formulas, native `48 kHz` → `16 kHz`/`8 kHz` modes.
- `shared/logmel_config.json` — Exact Section 5 recipe parameters (`win=480, hop=320, nfft=512, mels=40, mfcc=0`) + MFCC-13 (`win=400, hop=160, mfcc=13`).
- `shared/communication_protocol.json` — Frame binary layout, CRC-32 coverage, ASCII CLI commands (`PING`, `INFO`, `BAUD`, `STREAM`, `SAVE`, `DUMP`, `CRC`, `FREE`).
- `shared/frontend_api_contract.json` (`v1.1.0`) — All JSON/NPZ/CSV/PNG data paths, Flask `/api/*` endpoints, and Vite `/repo/*` bridge mounts.

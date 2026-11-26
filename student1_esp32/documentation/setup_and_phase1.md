# Student 1 — Setup & Phase 1 Guide & Results (ESP32-S3-DevKitC-1 N16R8)

**Team:** 1 (`Paradise`)  
**Board Operator (Student 1):** Siddharth Dhanush R  
**Primary Reference:** `edge_ai_assignment2/README.md`

---

## 1. Environment Status (Verified on Laptop)

- **Python:** `3.14.7` (run via `py` launcher; `python` in PATH hits a broken WindowsApps alias).
  - Installed: `numpy 2.5.3`, `pyserial 3.5`, `matplotlib 3.11.2`, `scipy 1.18.1`, `pandas 3.0.5`, `scikit-learn 1.9.1`, `pytest 9.1.1`.
  - Team 1 audio preview test: `py team_audio.py 1` succeeded (`team_01_preview.wav` generated in `edge_ai_assignment2/`).
- **Arduino IDE / CLI:** `C:\Program Files\Arduino IDE\Arduino IDE.exe` (`esp32:esp32` version `3.3.12`).

---

## 2. Arduino IDE / Build Settings (Phase 1 Initial Setup)

- **Board:** `ESP32S3 Dev Module` (`esp32:esp32:esp32s3:CDCOnBoot=cdc`)
- **USB CDC On Boot:** `Enabled`
- **Sketch:** `student1_esp32/firmware/doorbell_board_starter/doorbell_board_starter.ino`
- **Compiled Footprint:** `385,870` bytes flash (`29%`), `41,112` bytes dynamic RAM (`12%`).
- **Uploaded via:** `COM12` (`esptool v5.3.1`, chip `ESP32-S3 (QFN56) (revision v0.2)`, MAC `a4:cb:8f:d4:74:98`).

---

## 3. Physical Port Identification (Measured)

| Board Port | Windows COM | USB Hardware ID | Function | `PING` | `INFO` |
|---|---|---|---|---|---|
| **USB** (native CDC) | `COM11` | `USB\VID_303A&PID_1001&MI_00` | Built-in ESP32-S3 USB CDC (`Serial`) | `PONG` | Verified |
| **COM** (UART bridge) | `COM12` | `USB\VID_1A86&PID_55D3` (WCH USB-UART) | External UART bridge (`Serial0`, `921600` baud) | `PONG` | Verified |

### Measured `INFO` Output (Default Phase 1 Tools Settings)
- `cpu_mhz = 240`
- `heap_free = 256,208` bytes (`heap_largest = 204,788` bytes)
- `psram_size = 0` (expected with default Tools settings; OPI PSRAM to be enabled in Mission 2)
- `flash_chip = 16,777,216` bytes (`16 MB`)
- `fs_total = 1,441,792` bytes (`fs_used = 8,192` bytes)

---

## 4. Basic Data Transmission Test (Measured on `COM12`)

- Command: 1 s `int16` payload (`32,000` bytes, `50` data frames + `1` END frame) at `921600` baud (`feat=False`, `store="none"`, `speed=0`):
  - `packets_sent = 50`, `frames_ok = 51`
  - `bad_crc = 0`, `bad_len = 0`, `seq_gaps = 0`, `dup = 0`, `uart_errors = 0`
  - `samples = 16000`
  - `send_seconds = 0.3538 s`, board `ms = 353 ms`
- `COM11` basic stream test: Not yet tested (`COM11` was unplugged/absent after `COM12` test; will be tested in Phase 2 alongside USB vs COM benchmarks).

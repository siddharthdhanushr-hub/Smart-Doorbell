# Student 1 — Setup & Phase 1 Guide (ESP32-S3-DevKitC-1 N16R8)

**Team:** 1 (`Paradise`)  
**Board Operator (Student 1):** Siddharth Dhanush R  
**Primary Reference:** `edge_ai_assignment2/README.md`

---

## 1. Environment Status (Verified on Laptop)

- **Python:** `3.14.7` (run via `py` launcher; `python` in PATH hits a broken WindowsApps alias).
  - Installed: `numpy 2.5.3`, `pyserial 3.5`, `matplotlib 3.11.2`, `scipy 1.18.1`, `pandas 3.0.5`, `scikit-learn 1.9.1`, `pytest 9.1.1`.
  - Team 1 audio preview test: `py team_audio.py 1` succeeded (`team_01_preview.wav` generated in `edge_ai_assignment2/`).
- **Arduino IDE:** Installed at `C:\Program Files\Arduino IDE\Arduino IDE.exe`.
- **ESP32 Board Package:** `esp32:esp32` version `3.3.12` (satisfies `3.x` requirement).

---

## 2. Arduino IDE Settings (Phase 1 Initial Setup)

Open `edge_ai_assignment2/doorbell_board_starter/doorbell_board_starter.ino` (or the copy in `student1_esp32/firmware/doorbell_board_starter/`):

1. **Tools → Board:** `ESP32S3 Dev Module`
2. **Tools → USB CDC On Boot:** `Enabled`
3. Leave all other Tools settings at defaults for Phase 1 / Mission 1 (Mission 2 will intentionally uncover Flash Size, Partition Scheme, and OPI PSRAM settings).

---

## 3. Physical Board Connection & Port Identification

The **ESP32-S3-DevKitC-1 N16R8** has **two** USB-C ports:
- **COM / UART**: Goes through an external USB-to-UART bridge chip (`Serial0` in sketch when `USB CDC On Boot = Enabled`).
- **USB**: Native USB peripheral built into the ESP32-S3 (`Serial` in sketch).

### Commands to Run Once Both USB-C Cables Are Plugged In

```powershell
# 1. List serial ports before and after plugging in each cable
py "c:\Users\dhanu\OneDrive\Desktop\EDGE AI2\edge_ai_assignment2\board_link.py" ports

# 2. Test PING & INFO on each discovered port (replace COMx / COMy)
py "c:\Users\dhanu\OneDrive\Desktop\EDGE AI2\edge_ai_assignment2\board_link.py" --port COMx ping
py "c:\Users\dhanu\OneDrive\Desktop\EDGE AI2\edge_ai_assignment2\board_link.py" --port COMx info

py "c:\Users\dhanu\OneDrive\Desktop\EDGE AI2\edge_ai_assignment2\board_link.py" --port COMy ping
py "c:\Users\dhanu\OneDrive\Desktop\EDGE AI2\edge_ai_assignment2\board_link.py" --port COMy info
```

> **Note:** On `COM` (UART bridge), the default baud rate in `doorbell_board_starter.ino` and `board_link.py` is `921600`. On `USB` (native CDC), the baud rate setting is ignored by USB CDC. If upload says `Failed to connect`, hold **BOOT**, tap **RST** (or hold **BOOT** while IDE says `Connecting...`).

---

## 4. Phase 1 Test Results

- **USB Port (`USB` native CDC):** Not yet tested (board not plugged in yet)
- **COM Port (`UART` bridge):** Not yet tested (board not plugged in yet)
- **Pre-Mission 1 LLM Prediction Log:** To be recorded before running Mission 1 throughput tests.

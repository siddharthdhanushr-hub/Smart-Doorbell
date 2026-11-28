# Hardware–Software Integration Report (`Student 1 + Student 2`)

**Scope:** Python Host (`audio_codec.py`, `board_link.py`, `reference_logmel.py`, `serial_sender.py`) ↔ Physical `ESP32-S3-DevKitC-1 N16R8` (`doorbell_board.ino`, `features.h`) over `COM11` (USB CDC)  
**Test Execution Date:** 2026-11-28 (Post-Flash Live Hardware Run + Offline Protocol Verification)  
**Verdict:** **PASS (Physical `COM11` Verified Live; `COM12` UART Bridge Deferred / Not Attached)**

---

## 1. Protocol & Framing Alignment Audit

| Parameter | Python Side (`board_link.py` / `serial_sender.py`) | ESP32 Firmware (`doorbell_board.ino`) | Status |
|---|---|---|---|
| Uplink Magic | `0xA5 0x5A` (`b"\xA5\x5A"`) | `0xA5 0x5A` (byte state machine lines 182–187) | **Exact Match** |
| Downlink Magic | `0xB5 0x5B` (`b"\xB5\x5B"`) | `0xB5 0x5B` (`sendFrame()` lines 56–61) | **Exact Match** |
| Header & Endianness | `<IH` (`seq u32`, `len u16`), LE floats/ints | Little-endian Xtensa LX7 (`memcpy` u32/u16/f32) | **Exact Match** |
| CRC-32 Coverage | `zlib.crc32(type + seq + len + payload)` | IEEE `0xEDB88320` over `buf+2` for `7 + len` bytes | **Exact Match** |
| Payload Ceiling | `4,096 B` max check | `MAX_PAYLOAD = 4096` (`st.badLen++` on overflow) | **Exact Match** |
| Sample Quantisation | `f32` (`<f4`), `i16` (`q*scale/32767`), `i8` (`q*scale/127`) | Identical multipliers (`1.0`, `1/32767.0f`, `1/127.0f`) | **Exact Match** |
| Feature Config | `fs=16000, win=480, hop=320, nfft=512, mels=40` | `FeatCfg c;` (`fs=16000, win=480, hop=320, nfft=512, mels=40`) | **Exact Match** |

---

## 2. Live Physical Hardware Transmission Results (`COM11`)

All tests below were executed **live** against the ESP32-S3 (`MAC a4:cb:8f:d4:74:98`) immediately after compiling and flashing `student1_esp32/firmware/doorbell_board/` cleanly (`0` warnings):

### 2.1 Post-Flash Persistent Flash Integrity (`CRC flash`)
- **Result:** `INFO` (`cpu_mhz=240`, `heap_free=295828`, `psram_size=8388608`, `flash_chip=16777216`, `fs_total=7208960`, `fs_used=4628480`) and `CRC flash` returned **`n=4,608,000 B`**, **`crc=0x55c3d431` (`1438897201`)**.
- **Conclusion:** Persistent `/rec.bin` in LittleFS survived power-off AND firmware re-upload byte-for-byte.

### 2.2 Live Test 1 — Real-Time 6-Clip Stream + PSRAM Dump + Log-Mel Parity
- **Input:** Concatenation of 6 Team 1 clips (`id = 0, 24, 48, 72, 96, 120`, one per class), `16 kHz antialias=True`, `fmt=i16`, `S=1.0`, `speed=1.0`, `store="psram"`, `max=192000`, `samples_per_packet=320`.
- **Measured Output (`COM11`):**
  - `packets_sent = 300`, `frames_ok = 301` (`300` `'D'` + `1` `'E'`), `bad_crc = 0`, `bad_len = 0`, `seq_gaps = 0`, `dup = 0`, `uart_errors = 0`, `samples = 96,000`, `ms = 5,984`.
  - `expected_features = 299`, `received_features = 299`, `lost_features = 0`, `bad_crc_back = 0`.
  - `compute_us_mean = 683.75 us`, `compute_us_max = 742 us` (`3.4%` of `20,000 us` hop budget).
  - `psram_crc_match = True`, `psram_dump_exact_bytes = True` (`192,000 B` dumped from OPI PSRAM matched `payload_i16` identically).
  - `first_sample_match = True`.
  - **Numerical Parity vs Live `reference_logmel.py` (`x_hat`):** **`MAE = 1.67e-06 dB`**, **`max |diff| = 6.866e-05 dB`** (`< 0.05 dB` spec).

### 2.3 Live Test 2 — Wire Data Types & USB CDC Pipe Ceiling (`f32` & `i8`)
- **`f32 @ speed=4.0` (`256,000 B/s`):** Returned `75 / 99` feature frames on `COM11` — re-confirming native USB CDC's `>= 256 KB/s` RX buffer overflow limit discovered in Mission 3 (`192 KB/s` ceiling).
- **`f32 @ speed=1.0` (`64,000 B/s`, `spp=256`, 2 clips):** Returned **`99 / 99` frames** (`0` lost, `0` bad CRC, `0` gaps), **`MAE = 1.59e-06 dB`**, **`max = 3.815e-05 dB`**.
- **`i8 S=0.25 @ speed=4.0` (`64,000 B/s`, `spp=320`, 2 clips):** Returned **`99 / 99` frames** (`0` lost, `0` bad CRC, `0` gaps), **`MAE = 1.37e-06 dB`**, **`max = 1.144e-05 dB`**.

### 2.4 Live Test 3 — Controlled Packet Loss `skip=(0, 10, 11, 200)` (`COM11`)
- **Goal:** Verify patched firmware handles missing **`seq=0`** at stream start as well as multi-packet gap `(10, 11)` and single-packet gap `200`.
- **Measured Output:** `packets_sent = 296 / 300`, `seq_gaps = 4`, `samples = 96,000` (zeros inserted at all 4 gaps), `features = 293 / 299` (cleanly dropped 6 boundary-overlapping frames: 1 at start `[0]` + 3 across `(10, 11)` + 2 across `200`).
- **Alignment:** `first_sample_head = [320, 640, 960, 1280]`, `first_sample_tail = [94720, 95040, 95360] == expected_last_first_sample = 95360` (`0` tail misalignment).

### 2.5 Live Test 4 — Intentional Duplicate & Corrupted-CRC Frame Injection (`COM11`)
- **Sequence Injected:** Valid `D(seq=0)`, duplicate `D(seq=0)`, CRC-corrupted `D(seq=1)` (`XOR 0xFF` at byte 10), valid `D(seq=2)`, `E(seq=3)`.
- **Board Summary Frame `'S'` Observed:** `why=end frames_ok=3 bad_crc=1 bad_len=0 seq_gaps=1 dup=1 samples=960 stored=0 where=none`.
- **Conclusion:** Firmware cleanly isolated `bad_crc=1` and `dup=1`, accounted for lost `seq=1` (`seq_gaps=1`), and reconstructed `samples = 960`.

---

## 3. Offline Software Mock Verification (`MockBoard`)

- `MockBoard.stream()` (`student2_python/transmission/serial_sender.py`) is verified by `student2_python/tests/test_phase2_codec_and_protocol.py`.
- Fixed Stage B bug (`BUG-04`): `MockBoard` now counts missing initial packet `seq=0` (`last_seq < 0 and rseq > 0`), matching `doorbell_board.ino`.
- Explicitly distinguished from physical hardware runs via `"mock": True` and empty feature shape `(0, dim)`.

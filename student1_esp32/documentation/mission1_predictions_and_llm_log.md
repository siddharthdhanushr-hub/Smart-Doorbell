# Mission 1 — Pre-Experiment Predictions & LLM Log

**Mission:** Mission 1 — The Pipe (Data Rate, Port Comparison, Packet Overhead)  
**Team:** 1 (`Paradise`) · **Operator:** Siddharth Dhanush R  
**Primary Reference:** `edge_ai_assignment2/README.md` (Section 3, Mission 1)

---

## 1. Pre-Mission 1 Predictions (Calculated Before Measuring)

### Audio Stream Bitrates (Payload Only, 1 Channel)
| Sample Rate | Format | Bytes / Sample | Raw Payload Rate (B/s) | With 13 B Framing per 320 Samples (`+2.0%` at i16) |
|---|---|---|---|---|
| 16,000 Hz | `f32` | 4 | `64,000 B/s` | `64,650 B/s` (`50 pkt/s × 13 B = 650 B/s`) |
| 16,000 Hz | `i16` | 2 | `32,000 B/s` | `32,650 B/s` |
| 16,000 Hz | `i8`  | 1 | `16,000 B/s` | `16,650 B/s` |
| 8,000 Hz  | `i16` | 2 | `16,000 B/s` | `16,325 B/s` |
| 8,000 Hz  | `i8`  | 1 | `8,000 B/s`  | `8,325 B/s`  |

### UART (COM Port) Theoretical Maximum (8N1 = 10 bits/byte)
- `115,200 baud`: `11,520 B/s` raw wire limit → **cannot** sustain even `8 kHz i16` (`16,000 B/s`) or `16 kHz i8` (`16,000 B/s`), **can** sustain `8 kHz i8` (`8,325 B/s`).
- `921,600 baud`: `92,160 B/s` raw wire limit → **can** sustain all five configurations (`<= 64,650 B/s`), with `16 kHz f32` near ~70% link utilization.
- `2,000,000 baud`: `200,000 B/s` raw wire limit → comfortable headroom for all five, assuming the WCH USB-UART bridge and `Serial0` RX ring buffer keep up without `uart_errors`.

### Native USB CDC (USB Port) Prediction (Pre-Mission 1 LLM Question)
- ESP32-S3 has an internal Full-Speed USB 1.1 PHY (`12 Mbps` signaling = `1.5 MB/s` gross; after USB packet framing, bulk endpoints typically achieve ~`500–900 KB/s` in practice).
- Baud rate in `pyserial` / `BAUD` is ignored by USB CDC (`Serial`).
- Expected packet overhead effect (`samples_per_packet` with `i16` = 2 B/sample, 13 B header+CRC):
  - `8` samples (16 B payload): `16 / 29 = 55.2%` efficiency
  - `64` samples (128 B payload): `128 / 141 = 90.8%` efficiency
  - `320` samples (640 B payload): `640 / 653 = 98.0%` efficiency
  - `1024` samples (2048 B payload): `2048 / 2061 = 99.4%` efficiency

### Downlink Feature Bandwidth Prediction (Board → Laptop)
- With `fs = 16000`, `win = 480` (30 ms), `hop = 320` (20 ms), `mels = 40`:
  - Frame rate = `16000 / 320 = 50 frames/s` (49 frames in a 1.0 s clip because `1 + (16000 - 480) // 320 = 49`).
  - Each `'F'` frame payload = `8 B` (`first_sample`, `compute_us`) + `40 × 4 B` (`float32` features) = `168 B` payload + `13 B` frame header/CRC = `181 B/frame`.
  - Downlink bandwidth = `50 × 181 = 9,050 B/s` (`~9.05 KB/s`).
  - With `13 MFCCs` (`win=400, hop=160` -> `100 frames/s`): `(8 + 52 + 13) × 100 = 7,300 B/s`.

---

## 2. LLM Log (Pre-Mission 1)
- **Question asked:** How many bytes per second can be sent to an ESP32-S3 over its native USB CDC vs USB-UART bridge?
- **Answer summary:** Native ESP32-S3 USB is Full-Speed USB 1.1 (`12 Mbps` line rate, practical bulk CDC throughput typically `~500 KB/s–900 KB/s`, independent of baud rate), whereas the UART bridge uses 10 bits/byte (`baud / 10` B/s ceiling, e.g. `11,520 B/s` at 115,200 baud and `92,160 B/s` at 921,600 baud). Also `pyserial.write()` can return while OS/USB buffers are still draining, so board-side `ms` / `frames_ok` must be checked alongside laptop `send_seconds`.

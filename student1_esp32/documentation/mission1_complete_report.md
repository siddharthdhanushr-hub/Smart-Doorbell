# Phase 2 / Mission 1 Complete Report — COM (`COM12`) vs Native USB (`COM11`)

**Team:** 1 (`Paradise`) · **Operator:** Siddharth Dhanush R (Student 1)  
**Date:** 2026-11-26  
**Raw Data:** `student1_esp32/benchmarks/mission1_throughput.csv` (75 runs), `student1_esp32/logs/mission1_pipe_results.json`  
**Plots:** `student1_esp32/benchmarks/mission1_speed_vs_baud.png`, `student1_esp32/benchmarks/mission1_packet_size.png`

---

## 1. Speed=0 Throughput vs Configured Baud (16 kHz `i16`, `spp=320`, `64,000 B` payload, 3 repeats)

| Port | Baud | Mean Laptop Rate | Mean Board Rate | Bad CRC (avg) | Seq Gaps (total) | Explanation |
|---|---|---|---|---|---|---|
| **COM (`COM12`)** | `115,200` | `11,360.5 B/s` | `11,376.4 B/s` | `0` | `0` | UART 10-bit wire cap (`11,520 B/s`) minus 2% header/CRC overhead |
| **COM (`COM12`)** | `921,600` | `90,726.0 B/s` | `90,909.2 B/s` | `0` | `0` | UART 10-bit wire cap (`92,160 B/s`) |
| **COM (`COM12`)** | `2,000,000` | `194,535.1 B/s` | `194,726.9 B/s` | `0` | `0` | UART 10-bit wire cap (`200,000 B/s`); WCH bridge handles 2M baud cleanly |
| **USB (`COM11`)** | `115,200` | `501,455.3 B/s` | `332,181.9 B/s` | `13.0` | `0` | USB CDC ignores baud; `write()` returns before USB drains; 64 KB burst overflows 32 KB RX buffer |
| **USB (`COM11`)** | `921,600` | `508,498.1 B/s` | `334,509.0 B/s` | `13.7` | `0` | Same native USB CDC rate regardless of baud |
| **USB (`COM11`)** | `2,000,000` | `506,404.1 B/s` | `301,438.7 B/s` | `13.7` | `83` | Same native USB CDC rate; unthrottled 64 KB burst caused RX drops/timeouts |

---

## 2. Data-Type Comparison (`speed=0`, `921,600` baud, 16 kHz, 2.0 s payload, `spp=320`, 3 repeats)

| Format | Payload (2 s) | COM Board Rate | COM Samples/s | USB Board Rate | USB Samples/s | USB Errors |
|---|---|---|---|---|---|---|
| `f32` | `128,000 B` | `91,756.3 B/s` | `22,939` | `495,240.0 B/s` (rep 1: `367.8 kB/s`, rep 2–3: `559.0 kB/s`) | `123,810` | `23` bad CRC, `70` gaps in rep 1 (128 KB burst > 32 KB RX buffer) |
| `i16` | `64,000 B` | `90,823.1 B/s` | `45,412` | `332,763.7 B/s` | `166,382` | `13–14` bad CRC (64 KB burst > 32 KB RX buffer) |
| `i8` | `32,000 B` | `89,302.5 B/s` | `89,303` | `213,810.5 B/s` | `213,811` | **`0` bad CRC, `0` gaps** (32 KB fits within 32,768 B RX buffer) |

> **First-run observation:** On `USB f32`, Repeat 1 ran at `367,816 B/s` while Repeats 2 and 3 ran at `558,952 B/s`, confirming that initial USB/OS buffering makes the first run slower.

---

## 3. Real-Time Table (`speed=1.0`, 1.0 s clip, `spp=320`)

| Config | Payload | COM `115,200` | COM `921,600` | USB (`COM11`) |
|---|---|---|---|---|
| `16 kHz f32` | `64,000 B` | `5,570 ms` (**FAIL**) | `993 ms` (**PASS**) | `986 ms` (**PASS**, 0 err) |
| `16 kHz i16` | `32,000 B` | `2,809 ms` (**FAIL**) | `987 ms` (**PASS**) | `982 ms` (**PASS**, 0 err) |
| `16 kHz i8`  | `16,000 B` | `1,428 ms` (**FAIL**) | `983 ms` (**PASS**) | `981 ms` (**PASS**, 0 err) |
| `8 kHz i16`  | `16,000 B` | `1,400 ms` (**FAIL**) | `966 ms` (**PASS**) | `963 ms` (**PASS**, 0 err) |
| `8 kHz i8`   | `8,000 B`  | `980 ms` (**PASS**)   | `963 ms` (**PASS**) | `962 ms` (**PASS**, 0 err) |

---

## 4. Packet Size Effect (`samples_per_packet`, `16 kHz i16`, 1.0 s = `32,000 B`, `speed=0`, 3 repeats)

| `samples_per_packet` | Frames | COM Board Rate | COM Errors | USB Board Rate | USB Errors |
|---|---|---|---|---|---|
| `8` | `2,000` | `51,254.7 B/s` | `0` | `118,374.9 B/s` | `16–40` bad CRC, `0–97` gaps (`2,000` headers add `26,000 B`, total `58,000 B > 32 KB`!) |
| `64` | `250` | `84,359.0 B/s` | `0` | `200,838.6 B/s` | **`0`** (`35,250 B` total wire bytes) |
| `320` | `50` | `90,909.1 B/s` | `0` | `217,687.1 B/s` | **`0`** (`32,650 B` total wire bytes) |
| `1024` | `16` | `92,219.0 B/s` | `0` | `221,710.7 B/s` | **`0`** (`32,208 B` total wire bytes) |

---

## 5. Key Takeaways & Downlink Feature Bandwidth

1. **Why COM and USB behave differently:** `COM12` passes through a WCH USB-UART bridge whose baud clock throttles the physical wire (`11.4 kB/s` @ `115.2k`, `90.9 kB/s` @ `921.6k`, `194.7 kB/s` @ `2M`), preventing RX buffer overflow. `COM11` uses the ESP32-S3's internal Full-Speed USB CDC controller, ignores baud rate completely, writes at `~505 kB/s` from Python, and drops/corrupts packets if an unthrottled burst exceeds the `32,768 B` RX buffer faster than `runStream()` drains it. At `speed=1.0`, both `COM12 (>=921600)` and `COM11` have **zero errors**.
2. **Downlink feature bandwidth:** At `16 kHz`, `win=480` (30 ms), `hop=320` (20 ms), `mels=40`: `49` frames/clip (50 frames/s steady state) × (`8 B` metadata + `160 B` float32 + `13 B` frame) = `181 B/frame` → **`9,050 B/s`** steady-state (`8,869 B` for 1.0 s clip).

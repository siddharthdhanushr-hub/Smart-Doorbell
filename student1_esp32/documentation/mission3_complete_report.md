# Phase 4 / Mission 3 Complete Report — Python Reference & ESP32-S3 Log-Mel Optimization

**Team:** 1 (`Paradise`) · **Operator:** Siddharth Dhanush R (Student 1 & 2)  
**Date:** 2026-11-26  
**Source:** `student1_esp32/firmware/doorbell_board/features.h`, `student2_python/logmel/reference_logmel.py`, `shared/logmel_config.json`  
**Logs:** `student1_esp32/logs/mission3_starter_10s.json`, `student1_esp32/logs/mission3_optimized_results.json`  
**Plots:** `student2_python/documentation/mission3_class_spectrograms.png`

---

## 1. Pre-Mission 3 LLM Prediction Log
- **Question asked:** How long does a 512-point FFT take on an ESP32-S3 at 240 MHz?
- **Prediction:** Textbook $O(N^2)$ DFT calling `cosf`/`sinf` `257 × 480 × 2 = 246,720` times per frame would take **hundreds of milliseconds to ~1–2 seconds**, violating the `20 ms` hop budget; an iterative radix-2 FFT with precomputed twiddle factors (`2,304` butterflies, zero live trig) should take **under `1 ms` (`< 1,000 us`)**.

---

## 2. Starter vs Optimized ESP32-S3 Performance (`COM11`, 10 s @ `speed=1.0`, `16 kHz i16`)

| Implementation (`win=480, hop=320, nfft=512, mels=40`) | Expected Frames | Received Frames | Mean `compute_us` | Max `compute_us` | Mean `lag_s` | Max Diff vs NumPy |
|---|---|---|---|---|---|---|
| **Starter `dft()`** (`246,720` trig calls/frame) | `499` | `16` (`483` lost) | **`1,863,425 us`** (`1.86 s`) | `1,911,835 us` | `15.77 s` (up to `29.56 s`) | `0.000126 dB` |
| **Optimized Radix-2 FFT + Twiddle + Sparse Mel** | `499` | **`499` (`0` lost)** | **`683.71 us`** (`0.684 ms`) | `736 us` | **`0.0147 s`** | **`0.000072 dB`** |

- **Speedup:** **`2,725×`** faster per frame (`1,863.4 ms` → `0.684 ms`).
- **Real-time margin:** `0.684 ms` compute vs `20.0 ms` hop budget = **`3.4%` CPU duty cycle** (`~29×` real-time compute capacity).
- **Numerical accuracy:** `max_abs_diff_db = 0.000072 dB` (`mean = 0.000002 dB`, `RMSE = 0.000003 dB`) vs NumPy on identical quantised `i16` samples — well within the `0.05 dB` requirement.

---

## 3. Secondary Config (`win=400 / 25 ms, hop=160 / 10 ms, 13 MFCCs`)
- `expected = 998`, `received = 998` (`0` lost)
- `compute_us`: mean **`714.22 us`**, max **`764 us`** (vs `10,000 us` hop budget → `7.1%` CPU load)
- `lag_s`: mean `0.0149 s`, max `0.0203 s`
- `max_abs_diff_db`: **`0.000092 dB`**
- Downlink bandwidth: `100 frames/s × (13 header/CRC + 8 meta + 52 float32)` = **`7,300 B/s`** (vs `9,050 B/s` for 40 log-mel @ 20 ms hop).

---

## 4. Pipe vs Compute Bottleneck (`5 s` Speed Sweep on `COM11`, `16 kHz i16`)

| `speed` | Uplink Rate | `feat=False` (Lost / Seq Gaps / Bad CRC) | `feat=True` (Lost / Seq Gaps / Bad CRC) | Board `ms` (`feat=False` / `feat=True`) |
|---|---|---|---|---|
| `2×` | `64 KB/s` | `0 / 0 / 0` | `0 / 0 / 0` | `2,493 / 2,494 ms` |
| `4×` | `128 KB/s` | `0 / 0 / 0` | `0 / 0 / 0` | `1,249 / 1,248 ms` |
| `6×` | `192 KB/s` | `0 / 0 / 0` | `0 / 0 / 0` | `833 / 941 ms` |
| `8×` | `256 KB/s` | `26 gaps, 13 bad_crc` | `136 lost, 136 gaps, 68 bad_crc` | `724 / 729 ms` |
| `10×` | `320 KB/s` | `146 gaps, 73 bad_crc` | `170 lost, 170 gaps, 80 bad_crc` | `597 / 599 ms` |

**Conclusion:** Both `feat=False` and `feat=True` remain zero-loss up to **`6×` real-time (`192 KB/s`)** and fail at **`8×` (`256 KB/s`)**. Therefore **the USB CDC RX pipe/buffer drain rate—not feature compute—is the system bottleneck**.

---

## 5. Memory Usage (`nfft=512, win=480, mels=40, mfcc=0`)
- Global static sketch RAM: `33,432 B` (`10%` of 320 KB DRAM; down from `41,592 B` after removing `static float xr[2048]`).
- Dynamic feature pipeline allocations in `FeaturePipeline::begin()` + `runStream()`: `window` (`1,920 B`) + `re/im` (`4,096 B`) + `pw` (`1,028 B`) + `melw` (`41,120 B`) + `melv` (`160 B`) + `twRe/twIm` (`2,048 B`) + `bitrev` (`1,024 B`) + `melStart/melEnd` (`160 B`) + `fbuf/fout` (`2,080 B`) = **`53,636 B` (`~52.4 KiB`)** out of `287,976 B` free internal heap (`18.6%`).

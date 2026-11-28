# Smart-Doorbell — Edge AI (Module 2: "The Doorbell's Ears")

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Target MCU](https://img.shields.io/badge/Hardware-ESP32--S3--DevKitC--1_N16R8-red.svg)](https://www.espressif.com/en/products/socs/esp32-s3)
[![Tests: Pytest](https://img.shields.io/badge/Tests-18%20Passed-brightgreen.svg)](student4_validation/tests)
[![Dataset](https://img.shields.io/badge/Dataset-144_Clips_|_7056_Frames-blue.svg)](dataset)
[![Status](https://img.shields.io/badge/Readiness-1._READY_FOR_SUBMISSION-success.svg)](stage_C_final/final_submission_checklist.md)

**Course:** AI255TBD Edge AI · Module 2: *Sensor Data Acquisition on the Board*  
**Team Name:** Team 1 (`Paradise`)  
**Target Hardware:** ESP32-S3-DevKitC-1 N16R8 (Dual-core Xtensa LX7 @ 240 MHz, 16 MB Flash, 8 MB OPI PSRAM)  
**Submission Date:** 28 November 2026  
**Repository:** [https://github.com/siddharthdhanushr-hub/Smart-Doorbell.git](https://github.com/siddharthdhanushr-hub/Smart-Doorbell.git)

---

## Table of Contents
1. [Executive Summary & Project Overview](#1-executive-summary--project-overview)
2. [Team Members & Role Distribution](#2-team-members--role-distribution)
3. [System Architecture & Memory Map](#3-system-architecture--memory-map)
4. [Hardware Configuration & Arduino Tools Settings](#4-hardware-configuration--arduino-tools-settings)
5. [In-Depth Engineering Missions (Missions 1 to 5)](#5-in-depth-engineering-missions-missions-1-to-5)
   - [Mission 1: The Pipe (Data Rates, Port Comparison & Framing)](#mission-1-the-pipe-data-rates-port-comparison--framing)
   - [Mission 2: What to Send & Where to Keep It (Sampling, SQNR & Flash Persistence)](#mission-2-what-to-send--where-to-keep-it-sampling-sqnr--flash-persistence)
   - [Mission 3: Features on the Board (Radix-2 Log-Mel & Compute Benchmark)](#mission-3-features-on-the-board-radix-2-log-mel--compute-benchmark)
   - [Mission 4: Nothing Lost (Loss Accounting, Labelled Dataset & Data Card)](#mission-4-nothing-lost-loss-accounting-labelled-dataset--data-card)
   - [Mission 5: Laptop vs Board (Domain Shift & Nearest-Centroid Classifier)](#mission-5-laptop-vs-board-domain-shift--nearest-centroid-classifier)
6. [Consolidated 20-Metric Experimental Verification Table](#6-consolidated-20-metric-experimental-verification-table)
7. [Full-Stack Telemetry Dashboard (React + Flask)](#7-full-stack-telemetry-dashboard-react--flask)
8. [Course Submission Deliverables (`team_01_module2/`)](#8-course-submission-deliverables-team_01_module2)
9. [Quick Start & Reproduction Guide](#9-quick-start--reproduction-guide)
10. [Bug Tracker & Audit Trail](#10-bug-tracker--audit-trail)
11. [Limitations & Vulnerabilities](#11-limitations--vulnerabilities)

---

## 1. Executive Summary & Project Overview

The smart doorbell front-end must listen for spoken commands, buffer acoustic data securely, and compute compact numerical descriptors that a downstream keyword spotting model can interpret in real time.

Module 2 (*"The Doorbell's Ears"*) tasks Team 1 (`Paradise`) with implementing, characterizing, optimizing, and validating an end-to-end embedded audio acquisition and digital signal processing pipeline on physical ESP32-S3 hardware.

### Key Engineering Accomplishments:
- **Zero-Loss Transport:** Streamed 144 one-second clips (2,304,000 samples) across 6 classes (`on`, `off`, `stop`, `go`, `_unknown`, `_silence`) over native USB CDC (`COM11`) and WCH UART (`COM12`) with **0 dropped bytes, 0 sequence gaps, and 0 CRC errors**.
- **Power-Cut Flash Persistence:** Overcame the `142 KB` internal SRAM ceiling by utilizing `8 MB` OPI PSRAM, and implemented LittleFS flash persistence (`/rec.bin`, `4,608,000 B`) with bit-exact CRC-32 (`0x55c3d431`) verified intact across complete power cuts and firmware re-flashing.
- **2,725× DSP Speedup:** Optimized on-device 40-band HTK log-mel extraction from `1,863.4 ms` (starter textbook DFT) down to **`683.75 µs` per frame** using an iterative Cooley-Tukey radix-2 DIT FFT with precomputed twiddle factor tables and sparse mel boundaries—consuming only **`3.42%` of the 20 ms hop budget** (29.2× real-time safety margin).
- **Domain Shift & ML Parity:** Proved that ESP32 `16 kHz int16 S=1.0` features match host Python float32 within **`0.003914 dB` MAE** (`0.000002 dB` vs identical quantized samples), achieving an **identical `75.00%` accuracy** and identical confusion matrices on a stratified Nearest-Centroid keyword classifier. Conversely, demonstrated that omitting anti-aliasing collapses accuracy to **`25.00%`** due to high-frequency tone foldover.
- **Full-Stack Visualization:** Developed a 10-page React 19 + TypeScript + Vite 6 engineering dashboard backed by a Python Flask REST API and Vite static repository bridges, visualizing live streams, canvas spectrograms, memory telemetry, and ML performance.

---

## 2. Team Members & Role Distribution

This project was engineered through collaborative cross-functional specialization with rotating roles across all five missions:

| Student | Name & Handle | Primary Engineering Role | Key Module Responsibilities |
|---|---|---|---|
| **Student 1** | **Siddharth Dhanush R** (`Siddharthdhanush`) | Embedded Systems & Hardware Lead | ESP32-S3 firmware, LittleFS persistence, radix-2 FFT optimization, physical hardware execution (`COM11`/`COM12`), Stage B & C integration audit. |
| **Student 2** | **Rakshith Raghavendra** (`WhiteDevil-06`) | Python Backend & Audio Processing Lead | Audio codec (`f32`/`i16`/`i8`), framing protocol, NumPy reference DSP, Flask REST API server (`server.py`), Unit test suite. |
| **Student 3** | **Monica** (`monicaguru10`) | Frontend & Telemetry Dashboard Lead | 10-page React 19 dashboard, Canvas spectrograms, SVG telemetry charts, Vite `/repo/*` bridge, offline recorded fallback. |
| **Student 4** | **Saakshi Babu** (`Saakshi-babu`) | Validation & Machine Learning Lead | Dataset loss accounting, feature comparison heatmaps, stratified Nearest-Centroid classifier, automated integration test suite. |

### Mission Role Rotation Matrix (Faculty Rubric Requirement)
| Mission | Builder (Implementation) | Measurer (Benchmarking) | Skeptic (Verification & Edge Cases) | Scribe (Documentation & Logging) |
|---|---|---|---|---|
| **Mission 1: The Pipe** | Siddharth (S1) | Rakshith (S2) | Saakshi (S4) | Monica (S3) |
| **Mission 2: Audio & Storage** | Rakshith (S2) & Siddharth (S1) | Siddharth (S1) | Saakshi (S4) | Monica (S3) |
| **Mission 3: Features & FFT** | Siddharth (S1) | Siddharth (S1) | Rakshith (S2) | Saakshi (S4) |
| **Mission 4: Loss Accounting** | Siddharth (S1) | Saakshi (S4) | Rakshith (S2) | Monica (S3) |
| **Mission 5: ML & Classifier** | Saakshi (S4) | Saakshi (S4) | Siddharth (S1) | Monica (S3) |

---

## 3. System Architecture & Memory Map

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                               HOST LAPTOP (PYTHON PIPELINE)                            │
│                                                                                        │
│  ┌──────────────────┐    ┌─────────────────┐    ┌──────────────────┐    ┌────────────┐ │
│  │  team_audio.py   │───>│ audio_codec.py  │───>│ serial_sender.py │───>│ PySerial   │ │
│  │ 144 Clips @ 48kHz│    │ 16kHz i16 S=1.0 │    │ 0xA5 0x5A Frame  │    │ COM11/12   │ │
│  └──────────────────┘    └─────────────────┘    └──────────────────┘    └─────┬──────┘ │
└───────────────────────────────────────────────────────────────────────────────┼────────┘
                                                                                │ Uplink Audio
                                                                                │ (32,000 B/s)
┌───────────────────────────────────────────────────────────────────────────────▼────────┐
│                               ESP32-S3-DevKitC-1 N16R8                                 │
│                                                                                        │
│  ┌──────────────────────────────────────────────────────────────────────────────────┐  │
│  │ doorbell_board.ino (HWCDC / UART RX Ring Buffer: 32,768 Bytes)                    │  │
│  │ - Framing: 0xA5 0x5A Sync | Type | Seq (u32) | Len (u16) | Payload | CRC32 (u32) │  │
│  │ - Gap Recovery: Zero-fill padding on lost packets preserves sample timeline      │  │
│  └────────────────────────┬─────────────────────────────────┬───────────────────────┘  │
│                           │                                 │                          │
│            Audio Buffering│                      Feature DSP│ (Every 320 samples)      │
│                           ▼                                 ▼                          │
│  ┌─────────────────────────────────┐   ┌────────────────────────────────────────────┐  │
│  │ 8 MB OPI PSRAM (4,608,000 B)    │   │ features.h (Iterative Radix-2 DIT FFT)     │  │
│  │ - 144 clips volatile buffer     │   │ - Window: 480-sample Hann (30 ms)          │  │
│  │ - Leaves 3.78 MB (45.1%) free   │   │ - FFT: 512-point Power Spectrum (/512)     │  │
│  └────────────────┬────────────────┘   │ - Filterbank: 40 HTK Mel Bands (20-8000 Hz)│  │
│                   │                    │ - Latency: 683.75 µs/frame (3.42% CPU)     │  │
│         cmdSave() │ LittleFS           └────────────────────┬───────────────────────┘  │
│                   ▼                                         │                          │
│  ┌─────────────────────────────────┐                        │ Downlink Features        │
│  │ 16 MB Flash (/rec.bin)          │                        │ 0xB5 0x5B 'F' Frames     │
│  │ - 4,608,000 B bit-exact image   │                        │ (9,050 B/s)              │
│  │ - CRC 0x55c3d431 survives power │                        │                          │
│  │ - Leaves 2.58 MB (35.8%) free   │                        │                          │
│  └─────────────────────────────────┘                        │                          │
└─────────────────────────────────────────────────────────────┼──────────────────────────┘
                                                              │
┌─────────────────────────────────────────────────────────────▼──────────────────────────┐
│                            ANALYSIS, VALIDATION & DASHBOARD                            │
│                                                                                        │
│  ┌─────────────────────────┐    ┌─────────────────────────┐    ┌─────────────────────┐ │
│  │ 7,056-Frame Dataset     │    │ Nearest-Centroid Model  │    │ React 19 Dashboard  │ │
│  │ .npz / .csv Clean Corpus│───>│ 75.00% Accuracy (96/48) │───>│ Live Telemetry UI   │ │
│  │ 1,176 frames per class  │    │ Identical to Laptop f32 │    │ Canvas Spectrograms │ │
│  └─────────────────────────┘    └─────────────────────────┘    └─────────────────────┘ │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

### Memory Hierarchy Breakdown
| Memory Tier | Hardware Medium | Total Capacity | Allocated for Audio | Remaining Free Space | Persistence Behavior |
|---|---|---|---|---|---|
| **Internal SRAM** | On-chip SRAM | 512 KB (~320 KB DRAM) | 142,070 B (4.44 s) | ~170 KB | Volatile (Wiped on reboot) |
| **External PSRAM** | Octal SPI (OPI) PSRAM | 8,388,608 B (8.00 MiB) | 4,608,000 B (144.0 s) | **3,780,608 B (45.1%)** | Volatile (Survives soft reboot; wiped on power cut) |
| **LittleFS Flash** | Quad/Octal NOR Flash | 7,208,960 B (6.88 MiB) | 4,608,000 B (`/rec.bin`) | **2,580,480 B (35.8%)** | **Non-Volatile (Survives power cuts & firmware re-flashing)** |

---

## 4. Hardware Configuration & Arduino Tools Settings

### Physical Board Details
- **Board:** `ESP32-S3-DevKitC-1 N16R8`
- **SoC:** ESP32-S3 (Xtensa dual-core 32-bit LX7 @ 240 MHz, 40 MHz XTAL)
- **Memory:** 16 MB Flash, 8 MB Octal PSRAM
- **Physical USB Ports:**
  - **COM11 (USB Port):** Internal Full-Speed USB 1.1 PHY with native USB CDC. Ignores baud rate, transfers at high burst rates, but requires software pacing &ge; 256 KB/s.
  - **COM12 (COM/UART Port):** Onboard WCH USB-to-UART bridge connected to `GPIO43` (TX) and `GPIO44` (RX). Strict 10-bit asynchronous clock (tested from 115,200 to 2,000,000 baud).

### Mandatory Arduino IDE Tools Menu Settings
```text
Board:                "ESP32S3 Dev Module"
USB CDC On Boot:      "Enabled"
Flash Size:           "16MB (128Mb)"
Partition Scheme:     "Custom" (uses partitions.csv in sketch folder)
PSRAM:                "OPI PSRAM"
Upload Speed:         "921600"
USB Mode:             "Hardware CDC and JTAG"
```

### CLI Compilation String (FQBN)
```powershell
arduino-cli compile --fqbn esp32:esp32:esp32s3:CDCOnBoot=cdc,FlashSize=16M,PartitionScheme=custom,PSRAM=opi doorbell_board.ino
```

### Custom Partition Table (`partitions.csv`)
```csv
# Name,   Type, SubType, Offset,  Size,     Flags
nvs,      data, nvs,     0x9000,  0x5000,
otadata,  data, ota,     0xe000,  0x2000,
app0,     app,  ota_0,   0x10000, 0x480000,
app1,     app,  ota_1,   0x490000,0x480000,
spiffs,   data, spiffs,  0x910000,0x6E0000,
coredump, data, coredump,0xFF0000,0x10000,
```
*Provides two 4.5 MB OTA application slots and a **6.88 MiB (7,208,960 B)** LittleFS filesystem partition.*

---

## 5. In-Depth Engineering Missions (Missions 1 to 5)

Every mission adheres to the scientific verification loop: **Aim &rarr; Background &rarr; Prediction &rarr; Method &rarr; Observations &rarr; Analysis &rarr; What we learnt &rarr; LLM log**.

---

### Mission 1: The Pipe (Data Rates, Port Comparison & Framing)

#### 1. Aim
Benchmark serial throughput and packet framing overhead across UART (`COM12`) and native USB CDC (`COM11`), determine wire bandwidth limits for `f32`, `i16`, and `i8`, and verify real-time streaming capability.

#### 2. Background
UART framing uses 10 bits per byte (1 start bit, 8 data bits, 1 stop bit). The physical wire throughput is strictly `baud / 10` B/s. Native USB CDC uses packetized bulk transfers over Full-Speed USB (12 Mbps line rate) handled by the ESP32-S3 internal PHY; baud rate is ignored, but transfer speed is limited by host-side USB scheduling and the board's RX ring buffer.

#### 3. Prediction
- 16 kHz audio bitrates: `f32` = 64,000 B/s (64,650 B/s with framing); `i16` = 32,000 B/s (32,650 B/s); `i8` = 16,000 B/s (16,650 B/s).
- 115,200 baud UART maxes out at 11,520 B/s &rarr; cannot carry 16 kHz audio in real time.
- 921,600 baud UART maxes out at 92,160 B/s &rarr; can carry 16 kHz `f32`, `i16`, and `i8`.
- USB CDC will achieve &gt;300 KB/s, independent of baud rate.

#### 4. Method
Stream audio using `student1_esp32/benchmarks/mission1_pipe_benchmark.py` with `feat=False, store="none"`. Measure speed at `speed=0` across 115,200, 921,600, and 2,000,000 baud on `COM12` and `COM11`. Test packet sizes: 8, 64, 320, 1024 samples/packet. Record board-measured time (`ms`) vs host `send_seconds`.

#### 5. Observations
| Port | Baud | Mean Laptop Rate | Mean Board Rate | Bad CRC | Seq Gaps | Real-Time 16k i16 Status |
|---|---|---|---|---|---|---|
| **COM (COM12)** | 115,200 | 11,360.5 B/s | 11,376.4 B/s | 0 | 0 | **FAIL** (Takes 2,809 ms for 1.0 s) |
| **COM (COM12)** | 921,600 | 90,726.0 B/s | 90,909.2 B/s | 0 | 0 | **PASS** (Takes 987 ms, 0 errors) |
| **COM (COM12)** | 2,000,000 | 194,535.1 B/s | 194,726.9 B/s | 0 | 0 | **PASS** (Takes 982 ms, 0 errors) |
| **USB (COM11)** | 115,200 | 501,455.3 B/s | 332,181.9 B/s | 13.0 (at speed=0) | 0 | **PASS** (Takes 982 ms, 0 errors at speed=1.0) |
| **USB (COM11)** | 921,600 | 508,498.1 B/s | 334,509.0 B/s | 13.7 (at speed=0) | 0 | **PASS** (Takes 982 ms, 0 errors at speed=1.0) |

#### 6. Analysis
COM port rates strictly adhere to 10-bit UART physical limits (11.4, 90.9, 194.7 kB/s). USB CDC ignores baud entirely, achieving ~334 kB/s on board. At `speed=0`, unthrottled 64 KB bursts overflow the 32 KB RX buffer on USB. However, at `speed=1.0`, USB CDC and COM (&ge;921.6k) sustain zero packet drops and zero CRC errors. Small packet sizes (`spp=8`) incur 44.8% header overhead (26 KB headers on 32 KB data), whereas `spp=320` incurs only 2.0% overhead.

#### 7. What We Learnt
`pyserial.write()` returns when bytes enter local OS/USB drivers, not when the ESP32 receives them. Reliable benchmarking requires board-measured time (`ms`). Packet size must be &ge;320 samples to avoid excessive frame header overhead.

#### 8. LLM Log
- **Prompt:** "How many bytes per second can you send to an ESP32-S3 over USB?"
- **Answer:** Full-Speed USB 1.1 achieves theoretical 12 Mbps (1.5 MB/s); practical bulk CDC yields 500–900 KB/s, independent of baud rate. UART bridge requires 10 bits/byte (baud / 10). Host OS buffering may cause write() to return before physical transmission.

---

### Mission 2: What to Send & Where to Keep It (Sampling, SQNR & Flash Persistence)

#### 1. Aim
Implement audio quantization and packing in NumPy, quantify aliasing and Signal-to-Quantization-Noise Ratio (SQNR), configure 8 MB OPI PSRAM, and implement LittleFS flash persistence surviving power loss.

#### 2. Background
The Nyquist-Shannon theorem requires pre-sampling low-pass filtering. Frequencies above `fs/2` fold back into the baseband at `|k*fs - f|`. Int16 quantization provides ~98 dB theoretical SQNR, while int8 yields ~48 dB. ESP32-S3 internal SRAM is fragmented; buffering 144 seconds requires external PSRAM, and power-cut persistence requires LittleFS non-volatile flash storage.

#### 3. Prediction
Team 1's room tone at 7,348.0 Hz will alias at 8 kHz to `|8000 - 7348.0| = 652.0 Hz` if anti-aliasing is disabled. Int16 with S=1.0 will provide &gt;70 dB SQNR with 0% clipping; int8 will suffer severe quantization noise (~25 dB SQNR). Internal SRAM will hold &lt;5 seconds of audio; PSRAM and LittleFS will hold all 144 seconds (4.608 MB).

#### 4. Method
Evaluate silence clip 120 at 48 kHz vs 8 kHz with and without `antialias=True`. Measure SQNR across 144 clips for `i16 S=1.0`, `i8 S=1.0`, and `i8 S=0.25`. Test SRAM allocation ceiling, enable OPI PSRAM, implement `cmdSave()` in `doorbell_board.ino` using LittleFS, stream 144 clips, power-cycle the board, and verify flash CRC.

#### 5. Observations
- **Anti-Aliasing:** Tone at 7,348 Hz (-31.97 dB) folds to 652 Hz (-31.94 dB) without filter. Enabling `antialias=True` suppresses the peak by **51.82 dB** down to -83.76 dB.
- **SQNR:** `i16 S=1.0` delivers **74.21 dB mean SQNR** (0.00% clipping). `i8 S=1.0` gives 25.98 dB; `i8 S=0.25` gives 16.25 dB with 1.69% speech clipping.
- **SRAM vs PSRAM:** Internal SRAM capped at **142,070 B (4.44 s)**. OPI PSRAM unlocked 8,388,608 B, storing all 4,608,000 B with 0 errors.
- **Flash Persistence:** `SAVE` wrote 4,608,000 B to `/rec.bin` in **10.56 s**. After power disconnection and reconnect, `dump("flash")` returned bit-exact CRC `0x55c3d431` (PSRAM was wiped).

#### 6. Analysis
Anti-aliasing must occur prior to decimation because digital filtering cannot separate folded tones once sampled. Int16 S=1.0 preserves speech fidelity with negligible distortion. Stock Arduino settings assign only 1.44 MB to LittleFS; our custom `partitions.csv` allocates 6.88 MiB, leaving 35.8% headroom after storing 144 clips.

#### 7. What We Learnt
PSRAM is volatile and loses all contents on power cut. LittleFS requires custom partition tables for 16 MB flash. During `dump("flash")`, `HWCDC` dropped bytes during flash SPI reads until we configured a 32 KB TX buffer and 256-byte chunk pacing in firmware.

#### 8. LLM Log
- **Prompt:** "Why does an ESP32-S3 fail with 'ERR no psram' even though the chip has 8 MB PSRAM?"
- **Answer:** ESP32-S3 N16R8 uses Octal (OPI) PSRAM. Default Arduino IDE board configuration sets PSRAM to "Disabled" or "QSPI". It must be explicitly set to "OPI PSRAM" in the Tools menu; otherwise `psramFound()` returns false and heap allocation fails.

---

### Mission 3: Features on the Board (Radix-2 Log-Mel & Compute Benchmark)

#### 1. Aim
Implement the exact Section 5 log-mel recipe in NumPy, optimize ESP32-S3 feature extraction in `features.h` to run within the 20 ms frame budget, and prove numerical parity within &le;0.05 dB.

#### 2. Background
Log-mel spectrograms emulate human auditory perception. The recipe requires: 1) Framing (win=480, hop=320), 2) Hann windowing, 3) 512-pt FFT power spectrum, 4) 40 triangular HTK mel filterbanks (20–8000 Hz), 5) Log scaling: `10*log10(max(p, 1e-10))`. A naive Discrete Fourier Transform (DFT) requires $O(N^2)$ complex multiplications, violating real-time deadlines.

#### 3. Prediction
Textbook starter DFT calling `cosf/sinf` 246,720 times per frame will take ~1.5–2.0 seconds per frame (100× slower than real time). An in-place Cooley-Tukey radix-2 DIT FFT with precomputed twiddle factor tables and sparse mel boundaries will run in under 1,000 µs (&lt;1 ms).

#### 4. Method
Implement `reference_logmel.py` in NumPy. Replace starter `dft()` in `features.h` with an iterative bit-reversal radix-2 FFT using precomputed LUTs (`twRe`, `twIm`) and sparse mel filter spans `[melStart[m], melEnd[m])`. Stream 10 seconds of audio at `speed=1.0` on `COM11` and compare per-frame `compute_us`, `lag_s`, and max dB difference vs NumPy.

#### 5. Observations
| Implementation | Expected Frames | Received Frames | Mean Compute Time | Max Lag | Max Diff vs NumPy |
|---|---|---|---|---|---|
| **Starter dft()** | 499 | 16 (483 lost) | 1,863,425 µs (1.86 s) | 29.56 s | 0.000126 dB |
| **Optimized Radix-2 FFT** | 499 | **499 (0 lost)** | **683.71 µs (0.68 ms)** | **0.0147 s** | **0.000072 dB** |
| **MFCC-13 (10 ms hop)** | 998 | 998 (0 lost) | 714.22 µs | 0.0203 s | 0.000092 dB |

#### 6. Analysis
Optimization achieved a **2,725× speedup**. At 683.71 µs per 20 ms hop, the ESP32-S3 CPU duty cycle is only **3.42%**, leaving a 29.2× compute margin. Max numerical error vs NumPy is 0.000072 dB (well within 0.05 dB limit). In a speed sweep (2× to 10×), `feat=True` and `feat=False` fail at the identical speed (8×, 256 KB/s), proving that serial ingress buffering—not compute—is the bottleneck.

#### 7. What We Learnt
Trigonometric function calls (`cosf/sinf`) in loops are disastrous on microcontrollers. Precomputing twiddle factors and restricting filterbank multiply-accumulate operations to non-zero bins transforms an unusable pipeline into a production-grade DSP engine.

#### 8. LLM Log
- **Prompt:** "How long does a 512-point FFT take on an ESP32-S3 at 240 MHz?"
- **Answer:** A standard radix-2 DIT FFT implementation in C with look-up tables takes approximately 300 to 800 µs on an Xtensa LX7 core at 240 MHz. Using Espressif ESP-DSP SIMD assembly can push latency below 200 µs.

---

### Mission 4: Nothing Lost (Loss Accounting, Labelled Dataset & Data Card)

#### 1. Aim
Prove complete transmission integrity over all 144 clips, recover sample alignment under packet loss injection (`skip`), generate a clean labelled feature dataset, and author the official Data Card.

#### 2. Background
If a serial packet drops, naive sample counting causes subsequent audio frames to misalign in time, contaminating all downstream training labels. Packet loss must be detected via sequence numbers, and lost time must be zero-filled in firmware to preserve sample timestamps (`first_sample`). Frames straddling clip boundaries must be identified and handled.

#### 3. Prediction
For 144 one-second clips at 16 kHz: 144 s × 16,000 = 2,304,000 samples. At 320 samples/packet: exactly 7,200 data packets. Feature frames per 1-s clip: `1 + (16000 - 480) // 320 = 49` frames; 144 clips × 49 = 7,056 clean frames. Continuous streaming across boundaries yields 7,199 total frames (143 straddling frames).

#### 4. Method
Stream all 144 clips at `speed=1.0` on `COM11`. Log `packets_sent`, `frames_ok`, `seq_gaps`, `bad_crc`, and `samples`. Run controlled loss test with `skip=(10, 11, 200)`. Implement zero-fill gap recovery in `doorbell_board.ino`. Filter out 143 straddling boundary frames and export `doorbell_team1_esp32_features.npz` and `.csv`.

#### 5. Observations
- **Full 144-Clip Run:** 7,200 packets sent; `frames_ok = 7,201` (7,200 data + 1 END); `bad_crc = 0`; `seq_gaps = 0`; `samples = 2,304,000`. Expected features: 7,199; received: 7,199 (0 lost).
- **Loss Accounting with skip=(10, 11, 200):** Telemetry caught exactly 2 sequence gap events (gap of 2 packets at seq 10; gap of 1 packet at seq 200). Post-gap tail sample landed at **159,360** (exact expected alignment, 0 drift) vs 158,400 (-960 samples drift) prior to firmware fix.
- **Dataset Balance:** Exactly 1,176 frames per class across all 6 classes (7,056 total clean frames).

#### 6. Analysis
Sequence numbers detect missing packets; CRC-32 detects corrupted bytes. In firmware, when a sequence jump occurs, inserting `gap_pkts * samples_per_packet` zeros into `storeBuf`, advancing `st.samples`, resetting `fcount = 0`, and skipping to the next hop boundary completely prevents timeline slippage. Excluding the 143 inter-clip frames prevents cross-label contamination during model training.

#### 7. What We Learnt
Handling sequence gaps at packet 0 requires special care because `seq=0` can drop on link connect. The firmware must check whether the first arriving packet has `seq > 0` and insert initial zero padding accordingly.

#### 8. LLM Log
- **Prompt:** "How do you maintain audio feature frame alignment when UDP or serial packets are lost?"
- **Answer:** In streaming DSP, missing audio packets cannot simply be skipped; dropping samples causes all future FFT windows to slip in time. The receiver must synthesize silence (zero-padding) for the exact duration of the lost samples to maintain wall-clock phase and frame indexing.

---

### Mission 5: Laptop vs Board (Domain Shift & Nearest-Centroid Classifier)

#### 1. Aim
Quantify numerical domain shift between laptop float32 and ESP32 board features across formats (`16k i16`, `16k i8`, `8k no-AA`), train a Nearest-Centroid keyword spotter, and defend the shipping configuration.

#### 2. Background
Fixed-point quantization, clipping, and aliasing alter feature distributions relative to Python float32 training data. A Nearest-Centroid classifier computes class centroids on standardized training features (80-dim: per-clip mean and std of 40 bands) and assigns test clips to the nearest centroid by Euclidean distance. Train/test splits must be stratified at the clip level (96 train / 48 test) to prevent data leakage.

#### 3. Prediction
16 kHz `int16 S=1.0` will exhibit negligible MAE (&lt;0.01 dB) and produce identical classifier accuracy to laptop float32. Int8 will exhibit higher MAE (~1.0 dB) with slight accuracy degradation. 8 kHz without anti-aliasing will exhibit massive MAE (&gt;5 dB) due to 7,348 Hz whine aliasing and will severely degrade classification.

#### 4. Method
Compare all 4 hardware 144-clip feature runs against Python float32 reference using `compare_features.py` (MAE, RMSE, MaxAbs per band and class). Train Nearest-Centroid classifier on two-thirds of clips (96 clips) and evaluate on the remaining 48 clips using `nearest_centroid_eval.py` across all settings.

#### 5. Observations
| Audio &amp; Feature Configuration | MAE vs Float32 Ref | Max Error | Accuracy | Macro F1 |
|---|---|---|---|---|
| **Laptop Float32 (16 kHz AA=True)** | 0.000000 dB | 0.000 dB | **75.00%** | **0.7356** |
| **ESP32 16 kHz i16 S=1.0 (Shipping)** | **0.003914 dB** | **0.124 dB** | **75.00%** | **0.7356** |
| **ESP32 16 kHz i8 S=1.0** | 1.089735 dB | 16.426 dB | 68.75% | 0.6532 |
| **ESP32 16 kHz i8 S=0.25** | 0.821018 dB | 34.247 dB | 66.67% | 0.6289 |
| **ESP32 8 kHz i16 (No-AA vs 8k AA Ref)** | **8.050974 dB** | **53.594 dB** | **25.00%** | **0.1642** |

#### 6. Analysis
ESP32 `16 kHz i16 S=1.0` achieves **bit-exact classification parity (75.00% accuracy)** with the laptop float32 pipeline; their confusion matrices are identical. In contrast, 8 kHz without anti-aliasing causes bands 12–14 to suffer 20–31 dB MAE, collapsing classifier accuracy to 25.00% (random chance on 6 classes is 16.7%). Int8 S=0.25 clips speech peaks (34.2 dB max error), degrading accuracy to 66.67%.

#### 7. What We Learnt
Minor quantization noise (0.004 dB) is completely benign for keyword spotting because it affects only silent bins below the speech signal floor. In contrast, aliasing injects artificial energy directly into high-frequency speech formants, catastrophic for machine learning.

#### 8. LLM Log
- **Prompt:** "Why does audio aliasing destroy speech recognition accuracy more than uniform quantization noise?"
- **Answer:** Uniform quantization noise behaves like white noise, uniformly distributed across all frequency bands. Aliasing, however, creates spurious tonal peaks reflected into lower frequencies that mimic or corrupt acoustic formants, misleading classifier weight vectors.

---

## 6. Consolidated 20-Metric Experimental Verification Table

| # | Metric Description | Verified Measurement | Unit | Source & Verification Method |
|---|---|---|---|---|
| 1 | COM Port 115.2k Baud Rate | `11,376.4` | B/s | Physical COM12 Speed=0 Benchmark |
| 2 | COM Port 921.6k Baud Rate | `90,909.2` | B/s | Physical COM12 Speed=0 Benchmark |
| 3 | COM Port 2.0M Baud Rate | `194,726.9` | B/s | Physical COM12 Speed=0 Benchmark |
| 4 | Native USB CDC Burst Speed | `334,509.0` | B/s | Physical COM11 Speed=0 Benchmark |
| 5 | Room Tone Alias (8 kHz No-AA) | `652.0` | Hz | FFT Spectral Peak Analysis (Clip 120) |
| 6 | Anti-Aliasing Filter Attenuation | `51.82` | dB | 255-tap Blackman Windowed-Sinc |
| 7 | 16 kHz Int16 S=1.0 Mean SQNR | `74.21` | dB | 144-clip Audio Codec Analysis |
| 8 | Internal SRAM Buffer Limit | `142,070` | Bytes | SRAM Stress Probe (4.44 s ceiling) |
| 9 | Usable OPI PSRAM Capacity | `8,388,608` | Bytes | ESP32-S3 Firmware Init Telemetry |
| 10 | LittleFS Partition Capacity | `7,208,960` | Bytes | Custom partitions.csv Layout |
| 11 | LittleFS Save Latency (4.6 MB) | `10.56` | Seconds | cmdSave() Wall-Clock Benchmark |
| 12 | Post-Power-Cut Flash CRC-32 | `0x55c3d431` | Hex | Unplug/Replug LittleFS Dump |
| 13 | Starter DFT Compute Latency | `1,863,425` | µs | Baseline features.h Telemetry |
| 14 | Optimized Radix-2 FFT Latency | `683.75` | µs | Production features.h Telemetry |
| 15 | DSP CPU Duty Cycle (20 ms hop) | `3.42` | % | 683.75 µs / 20,000 µs Frame Budget |
| 16 | Downlink Feature Bandwidth | `9,050` | B/s | 50 fps × 181 Bytes/Frame |
| 17 | 144-Clip Full Stream Packet Loss | `0` | Packets | 7,200 Uplink Packets on COM11 |
| 18 | 16k i16 MAE vs Python Float32 | `0.003914` | dB | 7,056-Frame Comparison Matrix |
| 19 | 8k No-AA MAE vs Filtered 8k Ref | `8.050974` | dB | 7,056-Frame Comparison Matrix |
| 20 | Nearest-Centroid Test Accuracy | `75.00` | % | Stratified Clip-Split (96/48 clips) |

---

## 7. Full-Stack Telemetry Dashboard (React + Flask)

The project includes an interactive engineering dashboard located in `student3_frontend/`. Built with **React 19**, **TypeScript**, **Vite 6**, and **Tailwind CSS v4**, it provides an intuitive visual interface to explore all benchmark data, audio waveforms, spectrograms, and classifier diagnostics.

### Dashboard Architecture:
- **Frontend SPA:** Served by Vite on `http://localhost:5173/` (or `http://localhost:4173/` in preview mode).
- **Backend API:** Python Flask server running on `http://127.0.0.1:5000/` (`student2_python/api/server.py`).
- **Static Artifact Bridge:** Vite `/repo/*` route proxies precomputed JSON metrics and high-resolution PNG plots directly from `student4_validation/outputs/`.
- **Pages Included:**
  1. `Overview`: High-level summary badges, metrics cards, and mission progress.
  2. `System Architecture`: End-to-end block diagrams and memory hierarchy visualizer.
  3. `Audio Input`: Interactive clip inspector with waveform and decimation spectra.
  4. `Communication`: Throughput vs baud charts and USB CDC vs UART comparison.
  5. `Packet Integrity`: Controlled skip recovery visualizer (`159,360` samples).
  6. `Log-Mel Features`: Interactive 40-band log-mel spectrograms for all 6 classes.
  7. `Hardware Performance`: CPU duty cycle gauges and memory footprint breakdowns.
  8. `Laptop vs ESP32 Comparison`: Per-band and per-class error difference heatmaps.
  9. `Dataset Info`: Class distribution charts and Data Card viewer.
  10. `ML Evaluation`: Confusion matrices, Precision/Recall/F1 metrics, and baseline comparisons.

---

## 8. Course Submission Deliverables (`team_01_module2/`)

All deliverables required by `starter_files/README.md` (Section 4) are packaged in `team_01_module2/` and zipped as `team_01_module2.zip` (~4.7 MB):

```text
team_01_module2/
├── README.md                                    # Submission index & Tools settings
├── team_01_module2_technical_report.pdf         # 15-page comprehensive technical report
├── team_01_commitment_memo.pdf                  # Signed 1-page Client Commitment Memo
├── data_card.md                                 # Official dataset documentation
├── firmware/
│   └── doorbell_board/
│       ├── doorbell_board.ino                   # Production sketch (LittleFS, RX buffers, zero-fill)
│       ├── features.h                           # Radix-2 DIT FFT + twiddle LUT (684 µs)
│       ├── partitions.csv                       # Custom 16 MB partition table (6.88 MiB LittleFS)
│       └── tools_settings.txt                   # Arduino IDE / CLI build parameters
├── dataset/
│   ├── doorbell_team1_esp32_features.npz        # 7,056 × 40 float32 clean feature corpus
│   ├── doorbell_team1_esp32_features.csv        # Tabular export with clip_id, label, first_sample
│   ├── dataset_manifest.csv                     # 144-clip manifest
│   ├── dataset_validation.json                  # Audio validation metadata
│   └── data_card.md
├── python/
│   ├── audio_codec.py                           # f32 / i16 / i8 quantizer & packer
│   ├── reference_logmel.py                      # Pure-NumPy HTK log-mel & MFCC baseline
│   ├── serial_sender.py                         # 0xA5 0x5A framing & MockBoard
│   ├── batch_pipeline.py                        # Automated batch streamer
│   ├── validate_dataset_and_packets.py          # Loss accounting & speed-ramp limits
│   ├── compare_features.py                      # MAE/RMSE per-band & heatmap generator
│   ├── nearest_centroid_eval.py                 # Stratified split & classifier
│   ├── server.py                                # Offline Flask API (:5000)
│   └── test_stage_b_integration.py              # Automated integration tests
└── screenshots/
    ├── 01_dashboard_overview.png                # Live React engineering dashboard
    └── [11 technical benchmark & evaluation PNG plots]

team_01_module2.zip                              # 4,695,348 bytes (~4.7 MB archive)
```

---

## 9. Quick Start & Reproduction Guide

### Prerequisites
- Python 3.10+ (tested on Python 3.14.7)
- Node.js 18+ & npm
- Arduino IDE 2.x or `arduino-cli` with `esp32:esp32` core installed
- Physical ESP32-S3-DevKitC-1 N16R8 connected via USB (optional for board-free software runs)

### 1. Launch the Full-Stack Web Dashboard
To view and interact with the complete project telemetry in your web browser:

```powershell
# Step 1: Start the Python Flask backend (Terminal 1)
py student2_python/api/server.py --port 5000

# Step 2: Start the React Vite frontend (Terminal 2)
cd student3_frontend
npm install
npm run dev -- --host 127.0.0.1 --port 5173
```
*Open your browser and navigate to:* **`http://localhost:5173/`**

### 2. Run All Automated Python Tests
```powershell
py -m pytest -v student2_python/tests student4_validation/tests
```
*Expected Result:* **`18 passed`** in ~4 seconds.

### 3. Flash Physical ESP32-S3 Firmware
```powershell
# Navigate to the production sketch
cd student1_esp32/firmware/doorbell_board

# Compile with custom partition table and OPI PSRAM
arduino-cli compile --fqbn esp32:esp32:esp32s3:CDCOnBoot=cdc,FlashSize=16M,PartitionScheme=custom,PSRAM=opi doorbell_board.ino

# Upload to the connected COM port (e.g., COM11)
arduino-cli upload -p COM11 --fqbn esp32:esp32:esp32s3:CDCOnBoot=cdc,FlashSize=16M,PartitionScheme=custom,PSRAM=opi doorbell_board.ino
```

### 4. Reproduce Live Hardware Audio Streaming
```powershell
# Stream all 144 clips with feature extraction and PSRAM storage
py student1_esp32/benchmarks/mission4_skip_benchmark.py --port COM11 --speed 1.0

# Save to LittleFS Flash
py -c "from starter_files.board_link import Board; b=Board('COM11'); print(b.save())"

# Verify Flash CRC across a power cut
py -c "from starter_files.board_link import Board; b=Board('COM11'); print(b.crc('flash'))"
```

---

## 10. Bug Tracker & Audit Trail

| Bug ID | Severity | Description | Resolution | Status |
|---|---|---|---|---|
| **SA-01** | Critical | HWCDC dropped TX bytes during flash reads in `dump("flash")`. | Added `Serial.setTxBufferSize(32768)` and 256-B chunk pacing in `writeAll()`. | **FIXED** |
| **SA-02** | Critical | Packet loss caused post-gap audio sample timeline to slip. | Firmware zero-fills missing samples, increments `st.samples`, resets `fcount=0`. | **FIXED** |
| **SA-03** | High | Starter DFT took 1,863 ms per frame, dropping 96.8% of frames. | Rewrote with radix-2 DIT FFT + twiddle LUT + sparse mel bounds (684 µs). | **FIXED** |
| **BUG-01** | High | Student 4 compared 8k No-AA against 8k No-AA instead of filtered 8k Ref. | Re-ran comparison with `speech_pool.npz` against true `8 kHz antialias=True` reference. | **FIXED** |
| **BUG-02** | Medium | Frontend Comparison view displayed outdated fallback text. | Updated `ComparisonPage.tsx` and `MlEvaluationPage.tsx` descriptions. | **FIXED** |
| **BUG-03** | Medium | Shared contract v1.0.0 lacked documentation for Vite `/repo/*` bridge. | Incremented `frontend_api_contract.json` to v1.1.0 documenting all bridges. | **FIXED** |
| **BUG-04** | Low | Python `MockBoard` did not synthesize zero fill when `seq=0` dropped. | Updated `serial_sender.py` to handle `drop_seq_0` with exact sample padding. | **FIXED** |

---

## 11. Limitations & Vulnerabilities

1. **Synthesized Audio Stream:** Audio originates from synthetic Python playback over USB serial (`team_audio.py`) rather than a live physical I2S MEMS microphone (e.g. INMP441) in an acoustically reverberant room.
2. **Dataset Volume:** 144 one-second clips (48 test clips) with mean+std pooling restricts keyword separability between phonetically similar commands (e.g., `on` vs `go`).
3. **USB Burst Ceiling:** Native USB CDC drops packets during unthrottled bursts &ge; 256 KB/s due to the 32 KB hardware FIFO. Real-time streaming (`32 KB/s`) is 100% reliable with 500% headroom.
4. **Stock Board Default Vulnerability:** Flashing firmware with default Arduino IDE settings (`PSRAM=disabled`, `4MB` default partition scheme) causes heap failure and bootloop. Custom `partitions.csv` and `PSRAM: OPI PSRAM` are strictly mandatory.

---

## 12. Verification & Submission Sign-Off

This repository and all deliverables have been independently verified by Team 1 Paradise on live physical hardware:

- **Hardware Firmware:** Verified on `ESP32-S3-DevKitC-1 N16R8` (`COM11`) with zero compile warnings.
- **Python Pipelines:** Verified with 18/18 passing pytest checks.
- **Frontend Dashboard:** Production build cleanly compiled (`0` TypeScript errors) and verified.
- **Faculty Deliverables:** 1-page Client Commitment Memo PDF and 15-page Technical Report PDF generated and confirmed.

**Final Status:** **`1. READY FOR SUBMISSION`**

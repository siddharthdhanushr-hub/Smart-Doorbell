# Phase 3 / Mission 2 Complete Report — Sampling, Quantisation, PSRAM & Flash Persistence

**Team:** 1 (`Paradise`) · **Operator:** Siddharth Dhanush R (Student 1 & 2)  
**Date:** 2026-11-26  
**Firmware:** `student1_esp32/firmware/doorbell_board/doorbell_board.ino` + `partitions.csv`  
**FQBN:** `esp32:esp32:esp32s3:CDCOnBoot=cdc,FlashSize=16M,PartitionScheme=custom,PSRAM=opi`  
**Logs & Plots:** `mission2_probe_baseline.json`, `mission2_save144_opi_16m.json`, `mission2_verify_opi_16m.json`, `mission2_audio_analysis.json`, `mission2_aliasing_spectra.png`, `mission2_sqnr_comparison.png`

---

## 1. Sampling Rate & Anti-Aliasing Experiment (Silence Clip `id=120`)
- At `48 kHz`, Team 1's room has a switching-regulator whine at **`7348.0 Hz` (`-31.97 dB`)**.
- Sampling at `8 kHz` with `antialias=False` folds that tone to `|1 × 8000 - 7348.0|` = **`652.0 Hz` (`-31.94 dB`)** right inside the speech band.
- Sampling at `8 kHz` with `antialias=True` (255-tap Blackman windowed-sinc low-pass applied *before* decimation) attenuates the aliased peak by **`51.82 dB`** down to **`-83.76 dB`**.

## 2. Quantisation SQNR Comparison (`16 kHz`, `antialias=True`)
| Format | Scale `S` | Word (`id=0`) SQNR | Word Clipped | Silence (`id=120`) SQNR | All-144 Mean SQNR |
|---|---|---|---|---|---|
| `i16` | `1.0`   | `77.12 dB` | `0.000%` | `61.90 dB` | **`74.21 dB`** (`min 61.84`) |
| `i8`  | `1.0`   | `28.95 dB` | `0.000%` | `13.66 dB` | `25.98 dB` |
| `i8`  | `0.5`   | `34.93 dB` | `0.000%` | `19.65 dB` | `29.53 dB` |
| `i8`  | `0.25`  | `15.39 dB` | `1.694%` | `25.72 dB` | `16.25 dB` |
| `i8`  | `0.125` | `6.81 dB`  | `6.450%` | `31.70 dB` | — |

**Chosen Shipping Audio Config:** `fs = 16000 Hz`, `antialias = True`, `fmt = "i16"`, `scale = 1.0`. Dataset global peak is `0.67562 < 1.0` (`0%` clipping), `32,000 B/s` streams real-time with 3×–10× headroom on both `COM 921600` and `USB`, and all 144 clips total **`4,608,000 B` (~`4.39 MiB`)**.

## 3. SRAM vs OPI PSRAM & LittleFS Flash Persistence (Physically Measured)
- **SRAM limit (baseline):** Maximum contiguous `store="sram"` allocation verified end-to-end was **`142,070 B` (`4.44 s` of `16 kHz i16`)**; `store="psram"` failed with `ERR no psram (Tools > PSRAM)`.
- **OPI PSRAM + 16 MB Flash (`esp32s3` N16R8):** Enabling `PSRAM=opi`, `FlashSize=16M`, and custom `partitions.csv` (`6.88 MiB` LittleFS, since default 4 MB gave `1.44 MB` and default 16 MB `default_16MB.csv` gave only `3.38 MB` SPIFFS) unlocked **`8,388,608 B` PSRAM** and **`7,208,960 B` LittleFS**.
- **Full 144-Clip Store & Save:** Streamed `4,608,000 B` (`2,304,000` samples, `7,201` frames, `0` errors) into PSRAM (`psram_exact_match = true`), then `SAVE` wrote `/rec.bin` to LittleFS in **`10.56 s`** (`4,628,480 / 7,208,960 B` used, `64.2%`).
- **Power-Cut Persistence Test (Unplug + Replug):**
  - **PSRAM after power cut:** `n = 0`, `crc = 00000000` (volatile — **wiped**).
  - **Flash (`/rec.bin`) after power cut:** `dump("flash")` returned all **`4,608,000` bytes**, `flash_crc = 55c3d431` == `host_crc = 55c3d431`, **`flash_exact_byte_match = true`** (survived power cut intact!).
  - *Firmware fix discovered during `dump("flash")`:* Added `Serial.setTxBufferSize(32768)` and `256`-byte TX chunk pacing in `writeAll()` so `HWCDC` never drops TX bytes during interleaved Flash SPI reads.

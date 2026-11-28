# Final Hardware Testing Report (`ESP32-S3-DevKitC-1 N16R8`)

**Date of Final Hardware Execution:** 2026-11-28 (Stage B & Stage C live sessions on `COM11`)  
**Hardware Under Test:** `ESP32-S3 (QFN56) rev v0.2`, Dual Core LX7 @ `240 MHz`, `40 MHz` XTAL, `16 MB` Flash, `8 MB` OPI PSRAM, `MAC a4:cb:8f:d4:74:98`

---

## 1. Board Identification, Build & Port Status

- **FQBN Compiled (`arduino-cli --warnings all`):** `esp32:esp32:esp32s3:CDCOnBoot=cdc,FlashSize=16M,PartitionScheme=custom,PSRAM=opi`
  - Compiler output: **0 warnings**, **`392,700 B`** flash (`2%` of 16 MB), **`33,728 B`** global RAM (`10%` of 320 KB).
- **Detected Port (Live Stage C):** **`COM11`** (`USB Serial Device`, `ESP32 Family Device`).
- **UART Adapter (`COM12`):** `NOT TESTED – HARDWARE REQUIRED` during Stage B/C (USB-to-UART bridge was unplugged; historical Stage A `COM12` runs in `mission1_pipe_results.json` and `mission4_com_speed_ramp.json`).

---

## 2. Live Hardware Test Log Summary (`COM11`)

### 2.1 Flash Persistence Across Unplug/Replug + Firmware Re-Flash
- **Pre-flash & Post-flash `INFO`:** `cpu_mhz=240`, `heap_free=295828`, `psram_size=8388608`, `flash_chip=16777216`, `fs_total=7208960`, `fs_used=4628480`.
- **Post-flash `CRC flash`:** Returned `n = 4,608,000 B`, **`crc = 0x55c3d431` (`1438897201`)**, confirming the 144-clip LittleFS `/rec.bin` recording survived both power removal and OTA app re-flash unchanged.

### 2.2 Stage B Live Stream, Format & Protocol Error Tests (`COM11`)
| Test | Audio Config | Link & Storage | Measured Hardware Result | Verdict |
|---|---|---|---|---|
| **6-Clip RT Stream** | `16 kHz i16 S=1.0`, `speed=1.0`, `spp=320` | `COM11`, `store=psram` (`192,000 B`) | `300` pkts sent, `0` gaps, `0` bad CRC, `299/299` features, `compute_us` `683.75` avg / `742` max, PSRAM CRC & byte-dump **100% exact**, `MAE=1.67e-06 dB` | **PASS** |
| **Float32 Safe Rate** | `16 kHz f32 S=1.0`, `speed=1.0`, `spp=256` | `COM11` (`64 KB/s`), `store=none` | `99/99` features, `0` gaps, `0` bad CRC, `MAE=1.59e-06 dB`, `max=3.815e-05 dB` | **PASS** |
| **Float32 Burst Cap** | `16 kHz f32 S=1.0`, `speed=4.0`, `spp=256` | `COM11` (`256 KB/s`) | `75/99` features (24 lost) — confirms `COM11` `>= 256 KB/s` RX buffer limit | **EXPECTED CAP** |
| **Int8 Quantisation** | `16 kHz i8 S=0.25`, `speed=4.0`, `spp=320` | `COM11` (`64 KB/s`), `store=none` | `99/99` features, `0` gaps, `0` bad CRC, `MAE=1.37e-06 dB`, `max=1.144e-05 dB` | **PASS** |
| **Skip `(0,10,11,200)`** | `16 kHz i16 S=1.0`, `speed=4.0` | `COM11`, patched firmware | `296/300` pkts sent, `seq_gaps=4`, `samples=96000`, `features=293`, tail `95360 == expected` (`0` drift) | **PASS** |
| **Dup & Corrupted CRC** | Raw `D(0)`, dup `D(0)`, corrupt `D(1)`, `D(2)`, `E(3)` | `COM11`, `feat=0` | `why=end frames_ok=3 bad_crc=1 bad_len=0 seq_gaps=1 dup=1 samples=960` | **PASS** |

### 2.3 Stage C Repeated-Operation Stability & Live ML Inference Trace (`COM11`)
6 consecutive held-out test-split runs (`clip_id = 0, 25, 48, 73, 105, 126`, covering all 6 classes, `16 kHz i16`, `speed=2.0`, `store=psram`, `CRC psram`, `FREE`):
- **All 6 consecutive runs:** `0` lost features, `0` bad CRCs, `psram_crc_match=true` across every clip.
- **Per-frame compute time:** `682.69–685.16 us` mean across clips (`~3.4%` of `20,000 us` hop).
- **MAE / RMSE vs Python `reference_logmel.py`:** `1.45e-06–1.87e-06 dB` MAE / `2.36e-06–4.08e-06 dB` RMSE.
- **SRAM Stability:** `heap_free` before `6` consecutive cycles = `295,828 B`; after `6` cycles = `295,504 B` (no progressive leak).

---

## 3. Physical Tests Not Re-Run in Stage C

- `COM12` WCH UART bridge baud (`115.2k`, `921.6k`, `2M`) and `COM12` speed ramp (`1×..8×`) → **`NOT TESTED – HARDWARE REQUIRED`** (`COM12` adapter unplugged; verified in Stage A logs).
- Re-running `SAVE` on 144 clips (`cmdSave()`, ~10.56 s Flash write) → **`NOT RE-RUN`** in Stage C to avoid overwriting the verified `0x55c3d431` `/rec.bin` image; post-flash `CRC flash` confirmed Flash contents intact.

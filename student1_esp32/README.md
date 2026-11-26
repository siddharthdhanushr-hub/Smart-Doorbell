# Student 1 — Embedded Systems & Hardware (ESP32-S3-DevKitC-1 N16R8)

**Team:** 1 (`Paradise`) · **Operator:** Siddharth Dhanush R  
**Primary Specification:** `../edge_ai_assignment2/README.md`

## Firmware Layout
- `firmware/doorbell_board_starter/` — Unmodified faculty starter baseline.
- `firmware/doorbell_board/` — Finished Mission 2–4 firmware:
  - `doorbell_board.ino`: LittleFS `cmdSave()` (`/rec.bin`), `Serial.setTxBufferSize(32768)` + `256`-byte TX pacing for reliable 4.6 MB `DUMP flash`, and Mission 4 packet-gap `st.samples` + `fcount` timeline alignment.
  - `features.h`: Iterative radix-2 DIT FFT with precomputed twiddle/bit-reversal tables and sparse HTK mel filterbank bounds (`2,725×` speedup over starter `dft()`, `<= 0.0001 dB` difference vs NumPy).
  - `partitions.csv`: Custom 16 MB partition table (`4.5 MB` APP ×2 + `6.88 MiB` LittleFS).

## Arduino IDE / CLI Build Settings (Verified)
- **Board:** `ESP32S3 Dev Module`
- **USB CDC On Boot:** `Enabled`
- **Flash Size:** `16MB (128Mb)`
- **Partition Scheme:** `Custom` (`partitions.csv` in sketch folder)
- **PSRAM:** `OPI PSRAM`
- **FQBN:** `esp32:esp32:esp32s3:CDCOnBoot=cdc,FlashSize=16M,PartitionScheme=custom,PSRAM=opi`

## Reproducing Hardware Benchmarks (Student 1 Only)
```powershell
# Mission 1: COM vs USB throughput, data types, real-time, packet size
py student1_esp32/benchmarks/mission1_pipe_benchmark.py --com-port COM12 --usb-port COM11 --repeats 3

# Mission 2: SRAM probe, 144-clip PSRAM + SAVE, and post-power-cut verify
py student1_esp32/benchmarks/mission2_storage_test.py --port COM11 --phase save144 --tag opi_16m --speed 4.0
# (unplug and replug board)
py student1_esp32/benchmarks/mission2_storage_test.py --port COM11 --phase verify --tag opi_16m

# Mission 3: Optimized FFT benchmark + speed sweep
py student1_esp32/benchmarks/mission3_suite.py

# Mission 4: Controlled skip=(10, 11, 200) alignment check
py student1_esp32/benchmarks/mission4_packet_loss_test.py --port COM11 --tag after_fix

# Phase 5: Full 144-clip speed=1.0 extraction + SAVE + Mission 5 settings
py student1_esp32/benchmarks/phase5_full_pipeline.py --port COM11 --realtime-speed 1.0
```

# Phase 5 Final Handover Report — Student 1 & Student 2

**Team:** 1 (`Paradise`) · **Operator:** Siddharth Dhanush R (covering Student 1 & Student 2)  
**Date:** 2026-11-26  
**Board:** ESP32-S3-DevKitC-1 N16R8 (`240 MHz`, `16 MB` Flash, `8 MB` OPI PSRAM, MAC `a4:cb:8f:d4:74:98`)  
**Firmware:** `student1_esp32/firmware/doorbell_board/` (`doorbell_board.ino`, `features.h`, `partitions.csv`)

---

## 1. Completed Hardware & Python Deliverables Summary

| Phase / Mission | Status | Key Verified Evidence |
|---|---|---|
| **Phase 1 (Setup & Ports)** | **Complete** | Flashed ESP32-S3; identified `COM11` (native USB CDC) & `COM12` (WCH UART bridge); verified `PING`/`INFO`/stream |
| **Phase 2 / Mission 1 (Pipe)** | **Complete** | 75 benchmark runs (`mission1_throughput.csv`): COM `11.4 / 90.9 / 194.7 kB/s` @ `115.2k / 921.6k / 2M` baud; USB `~334 kB/s` (`i16`) ignoring baud; all 5 RT configs pass on `COM >= 921.6k` & `USB` |
| **Phase 3 / Mission 2 (Audio & Storage)** | **Complete** | `7348 Hz` whine aliasing (`652 Hz` @ `8 kHz`) suppressed `51.8 dB`; `16 kHz i16 S=1.0` (`74.21 dB` mean SQNR); SRAM max `142,070 B` (`4.44 s`); OPI PSRAM (`8 MB`) + LittleFS (`6.88 MiB`) stored all 144 clips (`4,608,000 B`) and survived unplug/replug byte-for-byte (`CRC 55c3d431`) |
| **Phase 4 / Mission 3 (Features)** | **Complete** | Optimized `features.h` (radix-2 FFT + twiddle table + sparse mel) cut `compute_us` from `1,863,425 us` to **`685 us`** (`2,725×` speedup, `0.000137 dB` max diff vs quantised NumPy); pipe (`6×` max zero-loss) is bottleneck, not compute (`3.4%` CPU) |
| **Phase 5 / Mission 4 (Loss & Dataset)** | **Complete** | Demonstrated `-960` sample shift before fix vs **`0` shift** after gap-alignment fix on `skip=(10, 11, 200)`; COM12 speed ramp (`mission4_com_speed_ramp.json`: `2.5×` max lag-free @ `921.6k`, `6.0×` @ `2M`, backpressure avoids drops vs USB `COM11` `8×` RX overflow); streamed all 144 clips at `speed=1.0` (`7,200` data pkts, `0` gaps, `0` CRC errors, `7,199/7,199` features, `SAVE` CRC `55c3d431`); exported `7,056`-frame dataset + `dataset/data_card.md` |
| **Phase 5 / Mission 5 Board Runs** | **Complete** | Exported 144-clip ESP32 & matching Python reference arrays for `16k i16 S=1.0`, `16k i8 S=1.0`, `16k i8 S=0.25`, and `8k i16 unfiltered` (`0` lost features on all 4 runs) |

---

## 2. All-144-Clip Hardware Extraction Results (`phase5_144clips_all_runs.json`)

| Config Tag | `fs` / `fmt` / `S` | `speed` | Sent / Recv Features | Board `avg_us` / `max_us` | MAE vs Quantised NumPy | MAE vs Orig `f32` NumPy |
|---|---|---|---|---|---|---|
| `16k_i16_S1.0_speed1` | `16k / i16 / 1.0` | `1.0×` | `7,199 / 7,199` (`0` lost) | `685 / 742 us` | **`0.000002 dB`** | **`0.003914 dB`** |
| `16k_i8_S1.0` | `16k / i8 / 1.0` | `4.0×` | `7,199 / 7,199` (`0` lost) | — | `0.000002 dB` | `1.089735 dB` |
| `16k_i8_S0.25` | `16k / i8 / 0.25` | `4.0×` | `7,199 / 7,199` (`0` lost) | — | `0.000001 dB` | `0.821018 dB` |
| `8k_i16_S1.0_noaa` | `8k / i16 / 1.0` (no AA) | `4.0×` | `7,199 / 7,199` (`0` lost) | — | `0.000002 dB` | `0.002828 dB` (vs 8k no-AA) |

---

## 3. Handover Packages Ready for Students 3 & 4

- **To Student 4 (Validation & ML, Missions 4 & 5):**
  - ESP32 & Python aligned feature arrays (`.npz` pairs listed in `shared/frontend_api_contract.json`)
  - Labelled clean dataset: `dataset/doorbell_team1_esp32_features.npz` & `.csv` (`7,056` frames)
  - Packet/loss logs: `mission4_skip_before_fix.json`, `mission4_skip_after_fix.json`, `phase5_144clips_all_runs.json`
  - Dataset manifest & data card: `dataset/dataset_manifest.csv`, `dataset/dataset_validation.json`, `dataset/data_card.md`
  - *Remaining for Student 4:* Compute full MAE/MSE/RMSE breakdown per band & per class, compare `8k_i16_S1.0_noaa` vs `8k (antialias=True)` reference, generate difference heatmaps, and train/evaluate the clip-split nearest-centroid classifier.
- **To Student 3 (Frontend / Dashboard):**
  - Data file index & contract: `shared/frontend_api_contract.json`
  - Hardware, audio, log-mel, and protocol configs in `shared/`
  - Benchmark CSV/JSONs and PNG plots in `student1_esp32/benchmarks/`, `student1_esp32/logs/`, and `student2_python/documentation/`.
- **Team Final Submission Items (Shared):**
  - Write final Mission 1–5 PDF records (8 headings each) + 1-page Commitment Memo + LLM reflection in `team_01_module2/` before Monday, 30 November 2026.

## 4. Hardware Constraints & Limitations Observed
- Native USB CDC (`COM11`) drops/corrupts packets if unthrottled bursts (`speed=0` or `>=8×` real-time) exceed the `32,768 B` RX buffer (`>= 256 KB/s`).
- `COM12` (UART bridge) is naturally wire-paced (`<= 194.7 kB/s` at `2M` baud) with `0` errors across all baud tests, while `115,200` baud cannot carry `16 kHz` audio in real time.
- Default Arduino IDE ESP32-S3 Tools settings disable PSRAM (`psram_size=0`) and give `1.44 MB` LittleFS; `PSRAM=opi`, `FlashSize=16M`, and `partitions.csv` (`6.88 MiB` LittleFS) are required for all 144 clips.

# Student 3 — Detailed Implementation & Integration Guide
## Frontend & Dashboard Developer

**Team:** 1 (`Paradise`) · **Primary Specs:** Project Master Plan (Section 9) & `../edge_ai_assignment2/README.md`  
**Board Access Required:** **None.** Never require a connected ESP32-S3 to run or demo the dashboard.

---

## 1. Git & Setup

```powershell
# 1. Pull latest verified deliverables from Students 1 & 2
git fetch origin
git checkout -b student3 origin/siddharth

# 2. Optional: start the board-free Student 2 backend API server on port 5000
py student2_python/api/server.py --port 5000
```

> **Ownership boundary:** Put all frontend code inside `student3_frontend/`. Do **not** modify `student1_esp32/`, `student2_python/`, `student4_validation/`, or `edge_ai_assignment2/`.

---

## 2. Backend & Data Integration Options

You have **two clean ways** to load data (you can use either, or both):

### Option A — Live HTTP JSON API (Provided by Student 2)
Run `py student2_python/api/server.py --port 5000` (if serving your frontend on another port, add `flask-cors` or proxy `/api` in Vite/React, or serve static HTML/JS straight from Flask/same origin).

| Endpoint | Returns |
|---|---|
| `GET /api/health` | `status`, `team=1`, `team_name="Paradise"`, `live_board_required: false`, `data_mode: "recorded_hardware_and_python_reference"` |
| `GET /api/configs` | `hardware`, `audio`, `logmel`, `protocol`, `contract` JSONs from `shared/` |
| `GET /api/dataset` | `validation` (`144/144`), `manifest` (`144` rows), `data_card_md` |
| `GET /api/clips/<clip_id>?fs=16000&antialias=true` | `clip_id`, `label`, `waveform` (`16000` floats), `first_sample`, `python_logmel` (`49×40`), `esp32_logmel` (`49×40`, recorded from `16k_i16_S1.0_speed1`) |
| `GET /api/benchmarks/mission1` | `csv_rows` (`75` runs across `COM12` & `COM11`) + `results` JSON |
| `GET /api/benchmarks/mission2` | `probe_baseline` (`SRAM` max), `save144`, `verify_power_cut`, `python_audio_analysis` (aliasing & SQNR) |
| `GET /api/benchmarks/mission3` | `starter_10s` (`1,863,425 us`) + `optimized` (`683.71 us`, `13 MFCC`, `speed` sweep) |
| `GET /api/benchmarks/mission4_5` | `skip_before_fix`, `skip_after_fix`, `com_speed_ramp`, `all_144_runs` |

### Option B — Direct Static File Loading (Zero Backend Server Required)
All file paths are listed in `shared/frontend_api_contract.json`. A pure React/Vite, Next.js, or Streamlit/HTML+Chart.js app can import/fetch those JSON/CSV/PNG assets directly.

### Integrating Student 4's Outputs (Graceful Empty/Loading States)
Student 4 will publish 3 files into `student4_validation/outputs/`:
- `mission4_validation_summary.json`
- `mission5_feature_comparison.json`
- `mission5_classifier_results.json`

**Critical UI Rule:** Until Student 4 merges those 3 files, display a clear **`Awaiting Student 4 Analysis`** badge/empty state on the Classifier & Full MAE/MSE/RMSE sections — **never fabricate metrics or substitute zeros (`0`) for missing values**.

---

## 3. Recommended Dashboard Stack

Pick any stack you are comfortable with that builds cleanly and runs in one documented command, e.g.:
- **Option 1 (Fastest & cleanest with existing Python API):** React + Vite + Tailwind + Recharts/Plotly (fetching `/api/*` via Vite proxy), **or**
- **Option 2 (Zero Node build needed):** Clean multi-page HTML/Tailwind/Chart.js or Plotly.js served directly (or via `student2_python/api/server.py` / `python -m http.server`).

---

## 4. Page-by-Page Specification & Exact Data Mapping

### Page 1 — Overview & System Architecture
- **Project summary:** Smart Doorbell Edge AI (`Team 1 — Paradise`, ESP32-S3-DevKitC-1 N16R8, 144 clips, 6 command classes).
- **Status Banner (Honesty Rule):** Clearly badge `"Data Source: Recorded Physical ESP32-S3 Runs (COM11 / COM12) & Python Reference"` — never claim a live board is streaming when displaying saved runs.
- **Architecture Diagram:** Laptop (`team_audio.py` → `audio_codec.py` → PySerial `A5 5A`) → ESP32-S3 (`PSRAM 8 MB` + `LittleFS 6.88 MiB` + Radix-2 FFT `features.h`) → Downlink (`B5 5B` `'F'`/`'S'`) → Offline Validation & ML (`Student 4`) → Dashboard (`Student 3`).
- **KPI Cards (from verified logs):**
  - Dataset: `144 / 144` clips (`7,056` clean frames)
  - Shipping Config: `16 kHz · int16 · S=1.0`
  - ESP32 Compute Time: `685.19 us / frame` (`2,725×` faster than starter `1,863,425 us`)
  - End-to-End 144-Clip Delivery: `0` lost packets, `0` bad CRCs, Flash CRC `55c3d431` verified after power cut.

### Page 2 — Audio Input & Feature Visualisation
- **Controls:** Clip selector (`clip_id 0..143`, filter by class `on / off / stop / go / _unknown / _silence`) + sample rate toggle (`16 kHz` / `8 kHz` / `antialias`).
- **Visuals (from `/api/clips/<id>`):**
  - Waveform plot (time `0..1.0 s` vs amplitude `-1..+1`).
  - Side-by-side Log-Mel Spectrogram heatmaps (`49 frames × 40 mel bands`, colorscale in `dB`): **Python Reference** vs **ESP32-S3 Board** (for `16 kHz` AA) + clip metadata (`peak_abs`, `rms`, `pool_word`, `pool_voice` from `dataset_manifest.csv`).

### Page 3 — Communication & Pipe Benchmarks (Mission 1)
- **Port Cards:** `COM11` (Native USB CDC, `VID_303A&PID_1001`, ignores baud) vs `COM12` (WCH UART bridge, `VID_1A86&PID_55D3`, `115.2k / 921.6k / 2M` baud).
- **Charts (from `/api/benchmarks/mission1`):**
  1. **Throughput (`kB/s`) vs Baud Rate** (`COM12` scales linearly `11.4 → 90.9 → 194.7 kB/s`; `COM11` stays flat `~332 kB/s` board-side / `~505 kB/s` laptop-side).
  2. **Data-Type Comparison** (`f32`, `i16`, `i8` throughput in `B/s` and `samples/s`).
  3. **Real-Time Matrix (`speed=1.0`):** `16 kHz f32/i16/i8`, `8 kHz i16/i8` pass/fail badges across `COM 115.2k` (only `8 kHz i8` passes), `COM 921.6k` (all 5 pass), and `USB` (all 5 pass).
  4. **Packet Size Overhead (`samples_per_packet = 8, 64, 320, 1024`)**: `51.3 → 84.4 → 90.9 → 92.2 kB/s` on `COM12`.

### Page 4 — Packet Integrity & Controlled Loss (Mission 4)
- **Full 144-Clip Stream Accounting (from `phase5_144clips_all_runs.json`):** `7,200` data packets sent, `7,201` `frames_ok`, `0` `seq_gaps`, `0` `bad_crc`, `7,199 / 7,199` features returned.
- **Controlled `skip=(10, 11, 200)` Before vs After Fix:** Show `before_fix` (`tail_shift = -960` samples, labels shifted) vs `after_fix` (`tail_shift = 0` samples, exact `first_sample` timeline preserved).
- **Speed Ramp Comparison (`COM11` USB vs `COM12` UART):** Plot `lost_features` & `lag_s_max` vs `speed` (`COM11` zero-loss to `6×`, drops at `8×`; `COM12` lag-free to `2.5× @ 921.6k` and `6× @ 2M`, zero byte drops due to UART backpressure).

### Page 5 — Hardware Performance, Sampling & Storage (Missions 2 & 3)
- **Sampling & SQNR (Mission 2):** Display `mission2_aliasing_spectra.png` (or interactive chart of `7348 Hz → 652 Hz` alias & `51.8 dB` anti-alias suppression) + SQNR bar chart (`i16 S=1.0: 74.21 dB` vs `i8 S=1.0: 25.98 dB` / `S=0.5: 29.53 dB` / `S=0.25: 16.25 dB` clipping).
- **Storage & Persistence Table:**
  - `SRAM`: max `142,070 B` (`4.44 s`) — cannot hold 144 clips (`4,608,000 B`).
  - `OPI PSRAM`: `8,388,608 B` (`8 MiB`) — holds all 144 clips (`psram_exact_match = true`), wiped (`0 B`) on power cut.
  - `LittleFS Flash`: `7,208,960 B` (`6.88 MiB`) — `/rec.bin` (`4,608,000 B`, `SAVE` in `10.56 s`), **`flash_exact_byte_match = true` (`CRC 55c3d431`) after unplug/replug**.
- **FFT Optimization & Bottleneck (Mission 3):**
  - Starter `dft()` (`1,863,425 us`, `483/499` frames lost) vs Radix-2 FFT (`683.71 us`, `0/499` lost, `0.000072 dB` diff).
  - Memory footprint (`53,636 B` / `~52.4 KiB` dynamic feature heap, `18.6%` of free internal SRAM) and `3.4%` CPU duty cycle (`20 ms` budget).

### Page 6 — Laptop vs Board & Classifier (Mission 5 — Integrated with Student 4)
- **Feature Comparison Table & Heatmaps:** Consume Student 4's `mission5_feature_comparison.json` + difference heatmaps for all 4 settings (`16k i16`, `16k i8 S=1.0`, `16k i8 S=0.25`, `8k i16 no-AA`).
  - *(Already verified in `phase5_144clips_all_runs.json`: `16k i16` achieves `0.000002 dB` MAE vs quantised NumPy and `0.003914 dB` MAE vs original `float32`.)*
- **Nearest-Centroid Classifier:** Consume Student 4's `mission5_classifier_results.json` (`accuracy`, `precision`, `recall`, `F1`, and interactive `6×6` confusion matrix).

### Page 7 — Dataset & Data Card
- Class bar chart (`24` clips / `1,176` clean frames per class across 6 classes), manifest table (searchable/filterable), and rendered `dataset/data_card.md` (including the `143` excluded straddling frames explanation and `clip_id`-level ML split constraint).

### Page 8 — Methodology, Tools Settings & Limitations
- Render exact Arduino IDE / FQBN settings (`ESP32S3 Dev Module`, `CDCOnBoot=cdc`, `FlashSize=16M`, `PartitionScheme=custom`, `PSRAM=opi`), metric definitions (`SQNR`, `MAE`, `MSE`, `RMSE`), and hardware limitations (USB `32 KB` RX overflow >= `8×`, synthetic `team_audio.py` room simulation).

---

## 5. UI Integrity Checklist (Strict Rules)
- [ ] Every chart/metric displays explicit **units** (`B/s`, `kB/s`, `us`, `ms`, `dB`, `bytes`, `frames`).
- [ ] Mock/placeholder states for Student 4's pending ML outputs are clearly labelled **`Awaiting Student 4 Results`** (never `0` or fabricated numbers).
- [ ] Dashboard runs completely offline from the board (`live_board_required: false`).
- [ ] Include a `student3_frontend/README.md` with exact start/build commands and a 2-minute live demo walkthrough.

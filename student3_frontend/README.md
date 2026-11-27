# Smart Doorbell — Edge AI Frontend Dashboard (Student 3)

**Team:** 1 (`Paradise`) · **Hardware Target:** `ESP32-S3-DevKitC-1 N16R8`  
**Board Access Required:** **None** (`live_board_required: false`). Runs cleanly offline using recorded hardware/Python logs, Student 2's Flask API, and clearly badged mock previews for pending/offline components.

---

## 1. Tech Stack & Architecture

- **Framework:** React 19 + TypeScript + Vite 6 + Tailwind CSS v4
- **Visualizations:** Custom responsive SVG Bar/Line charts, Confusion Matrix heatmap, and HTML5 Canvas time-domain Waveform & `49 × 40` Log-Mel Spectrogram plots with explicit engineering units (`dB`, `kB/s`, `us`, `ms`, `Hz`, `bytes`, `frames`).
- **Data Modes (Strictly Separated):**
  1. **Student 2 Flask API (`/api/*`)** — Proxied automatically by Vite to `http://127.0.0.1:5000`.
  2. **Repo Static Bridge (`/repo/*`)** — Serves committed JSON/CSV/MD files from `shared/`, `dataset/`, `student1_esp32/`, `student2_python/`, and `student4_validation/outputs/`.
  3. **Embedded Recorded Snapshot** — Fallback verified hardware snapshot if neither server bridge is available.
  4. **Mock / Simulated Layer (`src/data/mock/mockGenerators.ts`)** — Strictly isolated and labeled **`Mock / Simulated Data`** when `/api/clips/<id>` is offline or when previewing pending Student 4 ML outputs.

---

## 2. Setup & Execution

### Install dependencies
```powershell
cd student3_frontend
npm install
```

### Run Development Server (Board-Free)
```powershell
cd student3_frontend
npm run dev
```
Open `http://localhost:5173` in your browser.

### Optional: Start Student 2's Flask API (for live `/api/clips/<id>` waveform & spectrogram computation)
In a separate terminal at the repository root (requires `starter_files/speech_pool.npz` and Python dependencies):
```powershell
py -m pip install -r student2_python/requirements.txt
py student2_python/api/server.py --port 5000
```
Vite automatically proxies `/api/*` requests to `http://127.0.0.1:5000`.

### Production Type-Check & Build
```powershell
cd student3_frontend
npm run build
npm run preview
```

---

## 3. Dashboard Sections (10 Pages)

1. **Overview** — Project summary, workflow, team roles, tech stack, mission progress, and verified KPIs.
2. **System Architecture** — End-to-end pipeline SVG, `0xA5 0x5A` / `0xB5 0x5B` serial framing, FQBN settings, and hardware limitations.
3. **Audio Input** — Clip selector (`0..143`, class filter), `16 kHz / 8 kHz` & antialias toggles, metadata, and time-domain waveform.
4. **Communication & Throughput** — `COM11` (USB CDC) vs `COM12` (UART) comparison, throughput vs baud, data-type comparison, packet-size overhead, and real-time pass/fail matrix.
5. **Packet Integrity** — 144-clip accounting (`7,200` pkts, `0` gaps, `0` bad CRC), controlled `skip=(10, 11, 200)` before vs after gap-alignment fix, and speed-ramp loss/lag curves.
6. **Log-mel Feature Visualisation** — `49 × 40` HTK log-mel spectrogram heatmap (`dB` colorbar + cell hover), extraction config, and Python vs ESP32 comparison.
7. **Hardware Performance** — Aliasing & SQNR (`74.21 dB` `i16 S=1.0`), `SRAM` vs `OPI PSRAM` vs `LittleFS Flash` power-cut persistence (`CRC 55c3d431`), `2,725×` Radix-2 FFT speedup (`683.71 us`), and memory footprint.
8. **Laptop vs ESP32 Comparison** — `MAE`, `MSE`, `RMSE`, max diff across all 4 hardware runs + Student 4 `mission5_feature_comparison.json` integration.
9. **Dataset Information** — `144` clips (`24`/class, `7,056` clean frames), validation audit, searchable manifest table, and `dataset/data_card.md`.
10. **ML Evaluation** — Classifier accuracy, precision, recall, F1, and `6 × 6` confusion matrix wired to `student4_validation/outputs/mission5_classifier_results.json` (defaults to **`Awaiting Student 4 Results`** until merged, with an optional Mock Preview toggle).

---

## 4. Two-Minute Live Demo Walkthrough

1. **Overview (`0:00–0:20`):** Highlight `144/144` valid clips, `685.19 us` compute latency (`2,725×` speedup), `0` lost packets, and the board-free honesty badge.
2. **System Architecture (`0:20–0:35`):** Walk through Laptop Python → `0xA5 0x5A` → ESP32-S3 (`PSRAM` + `LittleFS` + `features.h`) → `0xB5 0x5B` → Validation/Dashboard.
3. **Audio Input & Log-Mel (`0:35–1:00`):** Pick a word clip (e.g. `#0 on`) and a `_silence` clip (`#120`), toggle `8 kHz` + `Antialias` to inspect waveform & `49 × 40` spectrogram behavior.
4. **Communication & Packet Integrity (`1:00–1:25`):** Compare `COM11` vs `COM12` throughput, show the `skip=(10, 11, 200)` before/after alignment fix, and contrast USB `8×` RX overflow with UART backpressure.
5. **Hardware & Comparison (`1:25–1:45`):** Show `LittleFS` `55c3d431` persistence after power cut, `74.21 dB` SQNR, and `0.003914 dB` MAE for `16k i16`.
6. **Dataset & ML Evaluation (`1:45–2:00`):** Show `data_card.md` (`143` straddling frames excluded) and demonstrate the `Awaiting Student 4 Results` state + Mock Preview confusion matrix.

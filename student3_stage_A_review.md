# Student 3 — Stage A Frontend & Dashboard Review Report

**Project:** Smart Doorbell — Edge AI (`Team 1: Paradise`)  
**Scope:** Stage A Review, Verification, Bug Fixing, and Stabilization of `student3_frontend/`  
**Review Date:** 2026-11-28  
**Branch Reviewed:** `student4` (base includes merged `student3` PR `d060b20`, local commit `f5e7b54`, and Student 4 outputs `1b26dcd`)

---

## 1. Pages and Components Reviewed

### Pages (`student3_frontend/src/pages/`)
1. `OverviewPage.tsx` — Project summary, data integrity banner, KPIs, 6-stage workflow, team roles, tech stack, mission progress tracker.
2. `ArchitecturePage.tsx` — SVG hardware/software pipeline (`0xA5 0x5A` / `0xB5 0x5B`), protocol frame layout, Arduino FQBN settings, hardware constraints.
3. `AudioInputPage.tsx` — Clip selector (`0..143`), class filter, sample-rate & anti-aliasing toggles, metadata KPIs, time-domain waveform canvas.
4. `CommunicationPage.tsx` — Board connection/stream status, `COM11` vs `COM12` cards, throughput vs baud chart, data-type sample-rate chart, packet-size overhead line chart, real-time capability matrix.
5. `PacketIntegrityPage.tsx` — 144-clip delivery KPIs (`packets_sent`, `frames_ok`, `seq_gaps`, `dup`, `bad_crc`), controlled `skip=(10, 11, 200)` before vs after firmware fix, `COM11` vs `COM12` speed-ramp loss/lag line charts.
6. `LogMelPage.tsx` — `49 × 40` HTK log-mel spectrogram inspector (Python reference vs recorded ESP32), extraction config KPIs, hover cell dB readout.
7. `HardwarePerformancePage.tsx` — Radix-2 FFT speedup & CPU duty cycle KPIs, SQNR bar chart (`i16` vs `i8`), processing-time bar chart, SRAM/PSRAM/LittleFS persistence table, aliasing summary, memory/storage chart.
8. `ComparisonPage.tsx` — Recorded 144-clip parity table (`MAE vs Quantised NumPy`, `MAE vs Orig float32`), bar chart, and Student 4 full `MAE`/`MSE`/`RMSE`/per-class/per-band comparison section.
9. `DatasetPage.tsx` — Dataset audit KPIs, class distribution bar chart, `data_card.md` viewer, searchable/filterable 144-clip manifest table.
10. `MlEvaluationPage.tsx` — Stratified clip-split Nearest-Centroid classifier KPIs (`Accuracy`, `Macro Precision`, `Macro Recall`, `Macro F1`), cross-setting bar chart, interactive `6 × 6` confusion matrix.

### Shared Components, Services & Config (`student3_frontend/`)
* Layout & UI: `DashboardLayout.tsx`, `DataBadge.tsx`, `KpiCard.tsx`, `SectionCard.tsx`, `EmptyAwaitingCard.tsx`
* Charts: `BarChart.tsx`, `LineChart.tsx`, `WaveformCanvas.tsx`, `SpectrogramCanvas.tsx`, `ConfusionMatrix.tsx`
* Services & Types: `src/services/api.ts`, `src/types/dashboard.ts`, `src/App.tsx`, `src/main.tsx`, `src/index.css`
* Data Layers: `src/data/recorded/recordedSnapshot.ts`, `src/data/mock/mockGenerators.ts`
* Tooling & Docs: `package.json`, `tsconfig.json`, `vite.config.ts`, `index.html`, `README.md`, `IMPLEMENTATION_AND_INTEGRATION_GUIDE.md`

---

## 2. Tests Performed

1. **TypeScript & Production Bundle Build:** Executed `npm run build` (`tsc -b && vite build`) inside `student3_frontend/` after final edits.
2. **Repository File & Contract Verification:** Executed Python validation script verifying all 23 referenced repo paths across `shared/`, `dataset/`, `student1_esp32/`, `student2_python/`, and `student4_validation/outputs/` exist and parse as valid JSON/CSV/Markdown.
3. **Numerical Cross-Check Against Source Logs:** Verified displayed metrics in `OverviewPage`, `CommunicationPage`, `HardwarePerformancePage`, `PacketIntegrityPage`, `DatasetPage`, `ComparisonPage`, and `MlEvaluationPage` against `mission1_pipe_results.json`, `mission2_*.json`, `mission3_*.json`, `mission4_*.json`, `phase5_144clips_all_runs.json`, `dataset_manifest.csv`, `dataset_validation.json`, and `student4_validation/outputs/*.json`.
4. **Vite Preview Server Local Probe:** Attempted launching `node ./node_modules/vite/bin/vite.js preview --host 127.0.0.1 --port 4173` and probing `/`, `/repo/*`, and `/api/health` inside the sandbox.
5. **Code & Accessibility Audit:** Inspected all charts, inputs, labels, keyboard handlers, missing-value paths, and mock-data separation rules.

---

## 3. Passed Tests

* **`tsc -b && vite build`:** Passed with exit code `0` after all Stage A bug fixes (`1652` modules transformed, built `dist/index.html`, `dist/assets/index-Dzpu_Ow6.css`, `dist/assets/index-rAfHXJ-b.js` in `4.29 s`).
* **Repo Data Contract Integrity (`23/23` files):** All 23 JSON, CSV, and Markdown files loaded by `src/services/api.ts` exist and parse without error.
* **Source Metric Verification:**
  * Mission 1 throughput means verified: `COM12` (`11.38 / 90.91 / 194.73 kB/s`), `COM11` (`332.18 / 334.51 / 301.44 kB/s` board-side), packet sizes (`8/64/320/1024`), data types (`f32/i16/i8`).
  * Mission 2/3 hardware values verified: `74.21 dB` `i16` mean SQNR, `51.82 dB` AA attenuation, Flash `CRC 55c3d431` (`4,608,000 B`), `683.71 us` (`mel40_10s_realtime`), `53,636 B` dynamic feature heap (`18.6%` of `287,976 B` free heap).
  * Dataset & Student 4 alignment verified: `144/144` valid clips, `7,056` clean frames (`143` straddling excluded), `16k_i16_S1.0_speed1` `MAE = 0.003914 dB` / `RMSE = 0.006064 dB`, Nearest-Centroid `75.00%` accuracy (`73.56%` macro F1) for both Laptop `float32` and ESP32 `16k int16`.

---

## 4. Failed Tests

* **Sandboxed `vite preview` HTTP Probe (`task-323`):** Failed with `Invoke-WebRequest : Unable to connect to the remote server` (`http://127.0.0.1:4173/`) because the Windows execution sandbox restricts local TCP port binding. *(The `npm run build` step inside the same run succeeded before the probe.)*

---

## 5. Bugs Discovered

1. **Missing-Data Zero Substitution (`CommunicationPage.tsx`):** `avg(nums)` returned `0` for empty arrays, which would display `0.0 kB/s` instead of `N/A` if a benchmark group were missing.
2. **Missing-Data Zero Substitution (`DatasetPage.tsx`):** `Number(r.peak_abs).toFixed(4)` and `Number(r.rms).toFixed(4)` converted empty/missing CSV cells into `0.0000` instead of `N/A`.
3. **Hardcoded Sample Rates (`AudioInputPage.tsx`):** Sample-rate `<select>` only listed `[16000, 8000, 48000, 24000, 12000]`, omitting `6000 Hz` and `4000 Hz` from `shared/audio_config.json` (`allowed_fs_hz`).
4. **Misleading `Mock` Origin Badge on `N/A` Metric (`LogMelPage.tsx`):** `Selected Clip Diff (MAE)` displayed a `Mock / Simulated Data` badge even when `esp32_logmel` was `null` (e.g., at `8 kHz` or `antialias=false`) and the value was `N/A`.
5. **Overlapping 40-Bar Chart & Partial Settings (`ComparisonPage.tsx`):** Per-band MAE used `BarChart` with 40 crowded `B0..B39` labels and filtered to only 2 of the 4 settings; also omitted Student 4's `reference_baseline` string (which notes when `speech_pool.npz` is absent for `8k_i16_S1.0_noaa`).
6. **Chart Tick/Label Overlap & Empty-State Guards (`BarChart.tsx`, `LineChart.tsx`):** Long category labels (`MlEvaluationPage`) and dense X-ticks (`LineChart` with 40 bands) overlapped, and empty series lacked an explicit empty-state guard.
7. **Missing Memory/Storage Chart (`HardwarePerformancePage.tsx`):** Memory & storage usage (`SRAM`, `OPI PSRAM`, `LittleFS`) was presented only in text/table form without a visual chart.
8. **Hardcoded Summary Strings (`OverviewPage.tsx`, `DatasetPage.tsx`):** Clean frame count (`7,056`), excluded frame count (`143`), invalid count (`0`), packet count (`7,200`), and CPU duty cycle (`3.4%`) were hardcoded instead of bound to `bundle` fields.
9. **Accessibility Gaps (`DashboardLayout.tsx`, `AudioInputPage.tsx`, `LogMelPage.tsx`, `DatasetPage.tsx`, `MlEvaluationPage.tsx`, `BarChart.tsx`, `LineChart.tsx`):** Missing `htmlFor`/`id` and `aria-label` bindings on form controls, missing `aria-current="page"` on active nav items, missing `Escape` handler on mobile drawer, and missing `role="img"`/`aria-label` on chart SVGs.

---

## 6. Bugs Fixed

| File | Fix Applied |
|---|---|
| `src/types/dashboard.ts` | Added optional `reference_baseline?: string` to `FeatureSettingMetrics`. |
| `src/pages/CommunicationPage.tsx` | Replaced `avg()` with `avgNullable()` returning `null` on empty arrays; added null-safe `N/A` rendering on throughput KPI cards. |
| `src/pages/DatasetPage.tsx` | Added `formatNumOrNA()` so missing `peak_abs`/`rms` never render as `0`; bound clean/excluded frames to `student4.validationSummary` and invalid count to `val.invalid_clip_ids.length`; added `aria-label` to filter/search inputs. |
| `src/pages/AudioInputPage.tsx` | Populated sample-rate options dynamically from `bundle.configs.audio.allowed_fs_hz`; connected `htmlFor`/`id` labels and `aria-pressed` on the antialias toggle. |
| `src/pages/LogMelPage.tsx` | Fixed `Selected Clip Diff (MAE)` `origin` badge to `'awaiting'` when `diffStats` is `null`; added `htmlFor`/`id` on clip selector. |
| `src/pages/ComparisonPage.tsx` | Replaced 40-bar per-band `BarChart` with `LineChart` across all 4 settings; added `Reference Baseline` column to Student 4's feature comparison table. |
| `src/pages/HardwarePerformancePage.tsx` | Added `BarChart` visualizing ESP32-S3 Memory & Storage Footprint (`SRAM Feature Heap`, `OPI PSRAM`, `LittleFS`) in `KiB` (`Used / Required` vs `Total Available`). |
| `src/pages/OverviewPage.tsx` | Bound `cleanFrames`, `excludedFrames`, `dutyCyclePct`, `packets_sent`, `bad_crc`, and `mean_sqnr_db` dynamically to `bundle`. |
| `src/pages/MlEvaluationPage.tsx` | Added `aria-label` to the classifier setting `<select>`. |
| `src/components/charts/BarChart.tsx` | Added empty-data guard, angled/truncated labels when `categories` are long or `> 6`, and `role="img"`/`aria-label`. |
| `src/components/charts/LineChart.tsx` | Added empty-data guard, automatic X-tick thinning (`<= 9` ticks) so 40-band charts stay legible, and `role="img"`/`aria-label`. |
| `src/components/layout/DashboardLayout.tsx` | Added `aria-current={active ? 'page' : undefined}` to nav buttons and `Escape` key closing for mobile drawer. |

---

## 7. Mock Data Still Present

* **`src/data/mock/mockGenerators.ts`:**
  * `generateMockClipDetail(...)`: Retained **strictly as an offline/missing-`speech_pool.npz` fallback** for `AudioInputPage` and `LogMelPage`, always explicitly badged **`Mock / Simulated Data`**. Whenever Student 2's Flask API returns real `/api/clips/<id>` data (with `speech_pool.npz` present), real audio/spectrograms replace the mock generator automatically.
  * `MOCK_STUDENT4_FEATURE_COMPARISON` & `MOCK_STUDENT4_CLASSIFIER_RESULTS`: Retained only for the manual "Preview Mock" fallback when `student4_validation/outputs/*.json` is absent. Because Student 4's real JSON outputs now exist in `student4_validation/outputs/`, `ComparisonPage` and `MlEvaluationPage` render **real Student 4 outputs** (`Recorded Hardware / Python Run` badge) and hide the mock preview button.
* **`src/data/recorded/recordedSnapshot.ts`:** Contains verified recorded hardware values (not fabricated mock data) used only when both Flask `/api/*` and Vite `/repo/*` are unavailable (e.g., static hosting of `dist/`).

---

## 8. Tests Not Performed

1. **Interactive Headless Browser / Visual DOM Test:** Live browser click-through across all 10 routes and mobile viewport (`375px`) was not automated in this review session (`vite preview` TCP port binding is blocked inside the sandbox).
2. **Live `/api/clips/<id>` End-to-End Test with `speech_pool.npz`:** `starter_files/speech_pool.npz` (~13 MB, git-ignored) is not present on this machine, so live Flask waveform/log-mel generation could not be exercised end-to-end.

---

## 9. Remaining Issues

1. **`starter_files/speech_pool.npz` Missing Locally:** Without `speech_pool.npz`, `/api/clips/<id>` returns `500` (`FileNotFoundError`) and `AudioInputPage` / `LogMelPage` fall back to `Mock / Simulated Preview`. Placing `speech_pool.npz` in `starter_files/` enables live Python reference clips immediately.
2. **Git Branch Synchronization:** The Stage A fixes in `student3_frontend/` and this report (`student3_stage_A_review.md`) currently sit uncommitted on branch `student4`. Commit and merge them (along with local `main` commit `f5e7b54`) into `origin/main` before Stage B.

---

## 10. Readiness for Stage B Integration

**Status: READY FOR STAGE B** (pending Git commit/merge of these Stage A fixes and optional placement of `speech_pool.npz` for live clip inspection).  
All 10 required sections, responsive layout, chart units, error/empty/missing-data guards, Student 1 & 2 recorded benchmarks, and Student 4's Mission 4/5 validation & ML outputs are cleanly integrated and pass `tsc -b && vite build`.

---

## Verified Frontend Files Inventory (`student3_frontend/`)

* `student3_frontend/index.html`
* `student3_frontend/package.json`
* `student3_frontend/package-lock.json`
* `student3_frontend/tsconfig.json`
* `student3_frontend/vite.config.ts`
* `student3_frontend/.gitignore`
* `student3_frontend/README.md`
* `student3_frontend/IMPLEMENTATION_AND_INTEGRATION_GUIDE.md`
* `student3_frontend/src/main.tsx`
* `student3_frontend/src/App.tsx`
* `student3_frontend/src/index.css`
* `student3_frontend/src/types/dashboard.ts`
* `student3_frontend/src/services/api.ts`
* `student3_frontend/src/data/mock/mockGenerators.ts`
* `student3_frontend/src/data/recorded/recordedSnapshot.ts`
* `student3_frontend/src/components/layout/DashboardLayout.tsx`
* `student3_frontend/src/components/ui/DataBadge.tsx`
* `student3_frontend/src/components/ui/EmptyAwaitingCard.tsx`
* `student3_frontend/src/components/ui/KpiCard.tsx`
* `student3_frontend/src/components/ui/SectionCard.tsx`
* `student3_frontend/src/components/charts/BarChart.tsx`
* `student3_frontend/src/components/charts/ConfusionMatrix.tsx`
* `student3_frontend/src/components/charts/LineChart.tsx`
* `student3_frontend/src/components/charts/SpectrogramCanvas.tsx`
* `student3_frontend/src/components/charts/WaveformCanvas.tsx`
* `student3_frontend/src/pages/OverviewPage.tsx`
* `student3_frontend/src/pages/ArchitecturePage.tsx`
* `student3_frontend/src/pages/AudioInputPage.tsx`
* `student3_frontend/src/pages/CommunicationPage.tsx`
* `student3_frontend/src/pages/PacketIntegrityPage.tsx`
* `student3_frontend/src/pages/LogMelPage.tsx`
* `student3_frontend/src/pages/HardwarePerformancePage.tsx`
* `student3_frontend/src/pages/ComparisonPage.tsx`
* `student3_frontend/src/pages/DatasetPage.tsx`
* `student3_frontend/src/pages/MlEvaluationPage.tsx`

---

## Instructions to Run the Dashboard

### Board-Free Standalone Mode (Recommended)
```powershell
cd "c:\Users\monic\OneDrive\Desktop\edge ai2\student3_frontend"
npm install
npm run dev
```
Open `http://localhost:5173/` in your browser.

### With Student 2's Flask Backend (Optional, for live `/api/clips/<id>`)
In a separate terminal from the repository root (place `speech_pool.npz` in `starter_files/` first):
```powershell
cd "c:\Users\monic\OneDrive\Desktop\edge ai2"
py -m pip install -r student2_python/requirements.txt
py student2_python/api/server.py --port 5000
```

### Production Type-Check & Build
```powershell
cd "c:\Users\monic\OneDrive\Desktop\edge ai2\student3_frontend"
npm run build
npm run preview
```

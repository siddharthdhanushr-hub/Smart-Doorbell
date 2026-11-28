# Student 3 Integration Review — React Dashboard & Backend Connectivity

**Component:** `student3_frontend/` · **Stack:** React 19, TypeScript, Vite 6.4.6, Tailwind CSS v4  
**Stage B Status:** **PASS** *(Production build + live Flask `/api/*` + Vite `/repo/*` HTTP routes verified in both `dev` and `preview`; Chrome DevTools click-through `NOT TESTED` — inactive `DevToolsActivePort`)*

---

## 1. Build, Type-Checking & Runtime Bridges

- **Dependencies:** Clean `npm install` (`84` packages, `0` vulnerabilities).
- **Type-Check & Production Bundle (`npm run build`):** `tsc -b && vite build` passed cleanly after all edits (`✓ 1652 modules transformed`, `dist/assets/index-C5KoY2x_.js` `347.44 kB` + CSS `31.53 kB`, built in `9.48 s`).
- **Vite Bridge (`vite.config.ts`):** Registers BOTH `configureServer` (`npm run dev`) AND `configurePreviewServer` (`npm run preview`) with:
  - `/repo/*` static bridge (restricted whitelist: `shared/`, `dataset/`, `student1_esp32/{benchmarks,logs}/`, `student2_python/documentation/`, `student4_validation/outputs/`).
  - `/api/*` proxy to `http://127.0.0.1:5000` returning clean JSON `503` if Flask is offline.

---

## 2. Backend Connectivity & Integrity Architecture (`services/api.ts`)

- **3-Tier Data Loading Verified:**
  1. **Flask `/api/*` + Vite `/repo/*`:** Fetches live configs, dataset, mission benchmarks, live `/api/clips/<id>` waveforms/log-mels, and Student 4 `outputs/*.json`.
  2. **Recorded Fallback (`recordedSnapshot.ts`):** Supplies committed Stage A/B hardware measurements if Flask/Repo bridge is offline.
  3. **Strict Mock Isolation (`mockGenerators.ts`):** Only triggered for `/api/clips/<id>` when Flask/`speech_pool.npz` is unreachable OR when the user explicitly toggles Mock Preview on Student 4 sections — always badged **`Mock / Simulated Data`** (`DataBadge.tsx`).
- **Honesty Rules Compliance:** Missing metrics are rendered as `N/A` or `EmptyAwaitingCard` (never displayed as `0`). Note: standalone `dist/index.html` without Vite dev/preview server cannot access `/repo/student4_validation/outputs/*.json` and therefore falls back cleanly to `recordedSnapshot.ts` + `Awaiting` state for Student 4.

---

## 3. Page-by-Page Code & Route Audit (10 Pages)

| Page (`PageId`) | Data Sources Consumed | Interactive Features / Visuals | Audit Verdict |
|---|---|---|---|
| `overview` | `configs`, `dataset`, `mission1..45`, `student4` | Navigation cards, Mission checklist, 4 KPI cards | **PASS** (Static + API parity verified) |
| `architecture` | `configs.hardware`, `configs.protocol` | End-to-end SVG pipeline diagram, FQBN & limitations | **PASS** |
| `audio` | `dataset.manifest`, `/api/clips/<id>` | Class filter, Clip ID `0..143`, `16k/8k` & `Antialias` toggles, `WaveformCanvas` | **PASS** (`/api/clips/0` & `/api/clips/120` 8k AA/No-AA HTTP 200 verified) |
| `communication` | `mission1.results.runs`, `mission45`, `configs` | Baud BarChart, Data-type comparison, Packet-size LineChart, RT pass/fail table | **PASS** |
| `packets` | `mission45.{all_144_runs,skip_before_fix,skip_after_fix,com_speed_ramp}`, `mission3` | 144-clip loss KPIs, skip before/after cards, USB vs COM loss & lag LineCharts | **PASS** |
| `logmel` | `configs.logmel`, `clipDetail.{python_logmel,esp32_logmel}` | Dual `SpectrogramCanvas` (`49x40`, hover values), live MAE/RMSE/Max diff card | **PASS** |
| `hardware` | `mission2`, `mission3`, `configs.hardware` | FFT `2,725×` KPI, SQNR BarChart, PSRAM/Flash table, SRAM/PSRAM footprint chart | **PASS** |
| `comparison` | `mission45.all_144_runs`, `student4.featureComparison` | Parity table + S4 MSE/RMSE + Per-Class BarChart + Per-Band LineChart | **PASS after `BUG-02` fix** |
| `dataset` | `dataset.{validation,manifest,data_card_md}`, `student4.validationSummary` | Balance KPIs, Class BarChart, searchable/filterable manifest table, `data_card.md` | **PASS** |
| `ml` | `student4.classifierResults` | Split metadata, setting dropdown (`8k` `25.0%` vs `16k` `75.0%`), 6×6 `ConfusionMatrix` | **PASS after `BUG-03` fix** |

---

## 4. Bugs Fixed in `student3_frontend/`

- **`BUG-02` (`ComparisonPage.tsx`):** Updated top parity table column headers and `8k_i16_S1.0_noaa` label to clearly show `Recorded MAE (Matched f32)` (`0.002828 dB (vs 8k No-AA)`) separately from `Student 4 MAE / RMSE (AA=True Ref)` (`8.0510 / 11.3750 dB`).
- **`BUG-03` (`ComparisonPage.tsx`, `MlEvaluationPage.tsx`):** Replaced outdated `"has not yet committed"` / `"will publish"` fallback copy with accurate `/repo/` bridge startup guidance (`npm run dev` or `npm run preview`).

---

## 5. Browser Verification Note (`NOT TESTED`)

Automated headless Chrome DevTools inspection via `browser` subagent could not attach (`DevToolsActivePort` `ENOENT`). Interactive DOM state and responsive layout breakpoints were audited by inspecting component TSX/CSS and verifying all 25 Vite `dev` + 4 Vite `preview` HTTP responses cleanly with real payloads. Recommend manual click-through in a desktop browser before Stage C demo.

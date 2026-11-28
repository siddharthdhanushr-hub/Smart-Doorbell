# Stage B Bug Tracker

Tracked bugs and cross-module discrepancies found during Stage B Master Integration Review.

---

## BUG-01 — Stale `8 kHz antialias=False` Baseline in Committed Student 4 Outputs
- **Severity:** **HIGH**
- **Affected Component:** `student4_validation/outputs/mission5_{feature_comparison,classifier_results}.{json,csv}`, `nearest_centroid_model.npz`, `plots/mission5_*.png`
- **Root Cause:** Teammates did not have `speech_pool.npz` (~13 MB) locally during Stage A, so `compare_features.py` and `nearest_centroid_eval.py` triggered their `speech_pool.npz absent` fallback (`8 kHz unfiltered (antialias=False)`), showing `0.002828 dB` MAE and `75.0%` classifier accuracy instead of demonstrating Mission 5's `8 kHz` aliasing collapse.
- **Fix Applied:** Re-executed `validate_dataset_and_packets`, `compare_features`, and `nearest_centroid_eval` in this workspace with sibling `../edge_ai_assignment2/speech_pool.npz` present; regenerated all JSONs, CSVs, model `.npz`, and 4 `mission5_*.png` plots.
- **Retest Result:** **PASS** — `8k_i16_S1.0_noaa` now compares against `"8 kHz filtered (antialias=True) Python float32 reference"` (`MAE = 8.050974 dB`, `RMSE = 11.375017 dB`, `8k` classifier accuracy = `25.00%`); enforced in `test_stage_b_integration.py`.

---

## BUG-02 — Ambiguous Side-by-Side Baselines in `ComparisonPage.tsx` Top Parity Table
- **Severity:** **MEDIUM**
- **Affected Component:** `student3_frontend/src/pages/ComparisonPage.tsx` (lines 33–57)
- **Root Cause:** Column 3 (`r.mae_vs_orig_f32_numpy_db` from `phase5_144clips_all_runs.json`, `0.002828 dB` vs `8k AA=False`) appeared beside Column 5 (`s4Row.rmse_db` from Student 4, `11.3750 dB` vs `8k AA=True`) without labeling the differing filter baselines or displaying Student 4's `8.0510 dB` MAE.
- **Fix Applied:** Updated table headers (`Recorded MAE (Matched f32)` and `Student 4 MAE / RMSE (AA=True Ref)`), added `(vs 8k No-AA)` inline tag on the `8k_i16_S1.0_noaa` row, and rendered `${s4Row.mae_db.toFixed(4)} / ${s4Row.rmse_db.toFixed(4)} dB`.
- **Retest Result:** **PASS** — `npm run build` (`tsc -b && vite build`) exited `0`.

---

## BUG-03 — Outdated `shared/frontend_api_contract.json` (`1.0.0`) & Student 4 Fallback Wording
- **Severity:** **MEDIUM**
- **Affected Component:** `shared/frontend_api_contract.json`, `student3_frontend/src/pages/ComparisonPage.tsx`, `student3_frontend/src/pages/MlEvaluationPage.tsx`
- **Root Cause:** Shared API contract pre-dated Student 4's outputs and Vite `/repo/*` bridge documentation; frontend empty-state alerts still stated `"Student 4 has not yet committed..."` / `"Student 4 will publish..."`.
- **Fix Applied:** Upgraded `shared/frontend_api_contract.json` to `1.1.0` adding `vite_repo_bridge`, `student4_*` paths, and `student4_plots`; updated fallback strings in both TSX pages. Added `test_frontend_api_contract_all_paths_exist` in `student4_validation/tests/test_stage_b_integration.py`.
- **Retest Result:** **PASS** — `pytest` (`18/18`) and `npm run build` pass.

---

## BUG-04 — `MockBoard.stream()` Missed Packet-0 Sequence Gap (`skip=(0,)`)
- **Severity:** **LOW**
- **Affected Component:** `student2_python/transmission/serial_sender.py` (line 138)
- **Root Cause:** Loop `if last_seq >= 0 and rseq != last_seq + 1:` only checked mid-stream gaps, missing `last_seq == -1 and rseq > 0`, whereas `doorbell_board.ino` line 200 explicitly catches missing `seq=0`.
- **Fix Applied:** Added `if last_seq < 0 and rseq > 0: seq_gaps += rseq` and regression assertion `skip=(0,)` in `student2_python/tests/test_phase2_codec_and_protocol.py`.
- **Retest Result:** **PASS** — Verified live firmware behavior (`TEST3_SKIP_0_10_11_200` on `COM11`: `seq_gaps=4`) matches updated `MockBoard` behavior (`test_frame_crc_and_mock_board_skip` passes).

---

## BUG-05 — Off-by-160 `expected_last_first_sample` Field in Historical `mission4_skip_after_fix.json`
- **Severity:** **INFO / DOC** (Preserved raw measured log)
- **Affected Component:** `student1_esp32/logs/mission4_skip_after_fix.json`
- **Root Cause:** Historical Stage A test computed `expected_last_first_sample` as `159520` instead of hop-aligned `((160000 - 480) // 320) * 320 = 159360`, yielding `tail_shift_samples: -160` even though `last_5_first_samples[-1]` (`159360`) was exact.
- **Status / Mitigation:** Preserved original measured JSON untouched per review integrity rules; `validate_dataset_and_packets.py` (`aligned_last_first_sample = 159360`) and `TEST3` on live `COM11` (`expected_last_first_sample = 95360`) both confirm exact `0`-sample drift.

---

## BUG-06 — `MockBoard.stream()` Does Not Zero-Fill Gap Samples or Extract Features
- **Severity:** **LOW** (Known simulation boundary)
- **Affected Component:** `student2_python/transmission/serial_sender.py` (lines 145–160)
- **Root Cause:** Existing `test_phase2_codec_and_protocol.py` line 77 asserts `res["board"]["samples"] == 320 * 8` when skipping 2 of 10 packets (`skip=(2, 5)`), and `MockBoard` returns `np.zeros((0, dim))` features.
- **Status:** Intentionally preserved to avoid breaking existing Student 2 unit assertions; clearly documented as framing/accounting simulation (`"mock": True`) while live hardware (`TEST3`) validates full zero-fill and real feature extraction.

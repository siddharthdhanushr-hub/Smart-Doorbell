# Final Consolidated Bug Tracker (Stages A, B & C)

All issues discovered across Students 1–4 during Stages A, B, and C, ordered from **CRITICAL → HIGH → MEDIUM → LOW**. Zero unresolved CRITICAL or HIGH bugs remain.

---

## Stage A Resolved Issues (Verified Retained in Stage C)

| ID | Severity | Affected File(s) | Root Cause & Fix Summary | Stage C Status |
|---|---|---|---|---|
| `SA-01` | **HIGH** | `student1_esp32/firmware/doorbell_board/doorbell_board.ino` | Interleaved Flash read/`DUMP flash` overflowed `HWCDC` TX FIFO + `freeStreamBufs()` leak on failed alloc. Fixed with `Serial.setTxBufferSize(32768)`, `writeAll()` 256-B pacing, and `freeStreamBufs()`. | **VERIFIED** (`0` warnings compile; live `COM11` stable across 6 runs) |
| `SA-02` | **MEDIUM** | `student2_python/api/server.py`, `requirements.txt` | Missing `flask>=3.0`, naive `nfft = win*2`, uncaught 500 if `speech_pool.npz` absent. Fixed bit-length power-of-2 `nfft` + JSON `503`. | **VERIFIED** (`test_api_server.py` passes; HTTP `200` on `:4173`) |
| `SA-03` | **LOW** | `student2_python/{reference_logmel.py,batch_pipeline.py,serial_sender.py}` | Missing input validation guards (`nfft < win`, empty `clip_ids`, odd payload length). Added explicit `ValueError` checks. | **VERIFIED** (`pytest` `18/18` passes) |

---

## Stage B & C Issues Tracked

| ID | Severity | Affected File(s) | Root Cause | Correction Applied | Retest Result |
|---|---|---|---|---|---|
| `BUG-01` | **HIGH** | `student4_validation/outputs/mission5_*` | `speech_pool.npz` absent during teammate Stage A runs caused `8k_i16_S1.0_noaa` to compare against `AA=False` (`0.0028 dB`, `75%` acc). | Re-ran all 3 Student 4 pipelines with `speech_pool.npz` present; regenerated JSONs, CSVs, `.npz`, and 4 `mission5_*.png` plots. | **CLOSED / PASS** (`8.0510 dB` MAE, `25.00%` acc; enforced in `test_stage_b_integration.py`) |
| `BUG-02` | **MEDIUM** | `student3_frontend/src/pages/ComparisonPage.tsx` | Top parity table showed `0.002828 dB` MAE (`AA=False`) next to Student 4 `11.3750 dB` RMSE (`AA=True`) without labeling differing references. | Clarified column headers (`Recorded MAE (Matched f32)` vs `Student 4 MAE / RMSE (AA=True Ref)`) and added `(vs 8k No-AA)` inline tag. | **CLOSED / PASS** (`npm run build` 0 errors) |
| `BUG-03` | **MEDIUM** | `shared/frontend_api_contract.json`, `ComparisonPage.tsx`, `MlEvaluationPage.tsx` | API contract (`1.0.0`) omitted Student 4 outputs and `/repo/*` bridge; TSX fallback alerts still read `"not yet committed"`. | Upgraded contract to `1.1.0` with `vite_repo_bridge` and `student4_*` paths; updated TSX fallback text + added contract test. | **CLOSED / PASS** (`pytest` + `npm run build` pass) |
| `BUG-04` | **LOW** | `student2_python/transmission/serial_sender.py` | `MockBoard.stream()` ignored initial skipped packet `seq=0` (`last_seq < 0 and rseq > 0`), unlike `doorbell_board.ino`. | Added `if last_seq < 0 and rseq > 0: seq_gaps += rseq` + `skip=(0,)` regression check in `test_phase2_codec_and_protocol.py`. | **CLOSED / PASS** (`18/18` pytest pass) |
| `BUG-05` | **LOW / DOC** | `student2_python/documentation/mission2_audio_analysis.json`, `student1_esp32/logs/mission4_skip_after_fix.json` | Minor static text anomalies: rationale string mentions `0.6705` while measured `dataset_global_peak_abs` is `0.67562`; historical `mission4_skip_after_fix.json` logged `159520` vs aligned `159360`. | Preserved raw logs untouched per audit rules; `validate_dataset_and_packets.py` uses exact `159360`, and Stage C reports cite `0.67562`. | **DOCUMENTED** |
| `BUG-06` | **LOW** | `student2_python/transmission/serial_sender.py` | `MockBoard.stream()` counts received samples without zero-fill and returns empty features `(0, dim)` (preserving `test_phase2_codec_and_protocol.py` line 77). | Kept backward-compatible; explicitly documented as protocol/framing simulation only while physical hardware runs test full DSP + zero-fill. | **DOCUMENTED** |

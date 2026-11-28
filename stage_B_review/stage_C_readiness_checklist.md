# Stage C Readiness Checklist (`Team 1 Paradise`)

**Deadline:** Monday, 30 November 2026  
**Prerequisite:** Stage B Master Integration Review (`PASS`)

---

## 1. Completed in Stage B (Ready for Submission Package)
- [x] Firmware (`student1_esp32/firmware/doorbell_board/`) compiles cleanly (`0` warnings, `392,700 B` flash, `33,728 B` RAM) and verified live on `COM11`.
- [x] Persistent LittleFS `/rec.bin` (`4,608,000 B`, `CRC 0x55c3d431`) re-verified intact post-flash on `2026-11-28`.
- [x] Real-time `16k i16`, `f32`, `i8 S=0.25`, `skip=(0, 10, 11, 200)`, and `dup`/`bad_crc` protocol error handling verified live on `COM11` (`MAE <= 1.67e-06 dB` vs Python).
- [x] Upgraded Student 4 Mission 5 `8 kHz antialias=True` comparison (`8.050974 dB` MAE, classifier accuracy `75.00% → 25.00%`) and regenerated all plots.
- [x] Updated `shared/frontend_api_contract.json` (`v1.1.0`), `ComparisonPage.tsx`, `MlEvaluationPage.tsx`, `serial_sender.py`, and `test_stage_b_integration.py`.
- [x] `py -m pytest -v student2_python/tests student4_validation/tests` → **18 passed**.
- [x] `npm run build` (`student3_frontend/`) → **0 errors**; Vite `dev` & `preview` + Flask `:5000` endpoints verified `HTTP 200`.

---

## 2. Remaining Stage C Action Items (User Sign-Off & Submission)

### A. Git / Branch Decision (Waiting for User Permission)
- [ ] Review all Stage B diffs (`git status`, `git diff`) locally.
- [ ] Commit `stage_B_review/` and final bug fixes (`BUG-02`, `BUG-04`, test updates) to branch `stage-b-review`.
- [ ] Explicitly authorize push to `origin/stage-b-review` and merge PR #11 into `main` *(held per Stage B instruction: no push/merge without permission)*.

### B. Optional Pre-Demo Live Checks
- [ ] *(Optional UI Visual Walkthrough)* Start `py student2_python/api/server.py --port 5000` and `npm run dev` inside `student3_frontend/` and click through all 10 tabs in Chrome (`http://localhost:5173`) since DevTools remote debugging was unavailable to automation.
- [ ] *(Optional UART Re-Verify)* Only needed if live UART (`COM12`) demo is planned; hardware already verified on `COM11` USB CDC and Stage A `COM12` logs are complete.

### C. Course Deliverables Packaging (`team_01_module2/`)
- [ ] Assemble `team_01_module2/` technical PDF report (`<= 12` pages, covering Missions 1–5 with the 8 required subsections using upgraded Stage B numbers & `student4_validation/outputs/plots/` figures).
- [ ] Complete 1-page Team Commitment / Contribution Memo & LLM prediction reflection (`mission1_predictions_and_llm_log.md`).
- [ ] Prepare and rehearse 5-minute demonstration (live dashboard + optional ESP32 `COM11` `PING`/`INFO`/`CRC flash` or short stream).

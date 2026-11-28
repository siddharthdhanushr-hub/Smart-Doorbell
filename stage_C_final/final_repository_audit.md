# Final Repository Audit — `Smart-Doorbell` (Stage C)

**Repository:** `https://github.com/siddharthdhanushr-hub/Smart-Doorbell.git`  
**Active Branch Audited:** `stage-b-review` (`6de581f`, ahead of `origin/main` @ `ded36aa`)  
**Audit Date:** 2026-11-28 · **Team:** 1 (`Paradise`) · **Course:** AI255TBD Edge AI Module 2

---

## 1. Phase 1 Audit Checklist (15 Required Criteria)

| # | Audit Item | Status | Evidence Verified in Stage C |
|---:|---|---|---|
| 1 | All four students' contributions present | **COMPLETE** | `student1_esp32/`, `student2_python/`, `student3_frontend/`, `student4_validation/` |
| 2 | Stage A review reports available | **COMPLETE** | `student1_stage_A_review.md`, `student2_stage_A_review.md`, `student3_stage_A_review.md`, `student4_stage_A_review.md` |
| 3 | Stage B integration review reports available | **COMPLETE** | `stage_B_review/` (`10` `.md` reports) + `stage_B_review.md` |
| 4 | All identified critical bugs resolved/documented | **COMPLETE** | `0` open CRITICAL/HIGH bugs; Stage A & B fixes re-verified (`final_bug_tracker.md`) |
| 5 | ESP32 firmware available | **COMPLETE** | `student1_esp32/firmware/doorbell_board/{doorbell_board.ino,features.h,partitions.csv}` + unmodified `doorbell_board_starter/` |
| 6 | Python backend & audio-processing code available | **COMPLETE** | `student2_python/{src,preprocessing,transmission,logmel,api,tests}/` |
| 7 | Dataset and manifest available | **COMPLETE** | `dataset/{dataset_manifest.csv,dataset_validation.json,doorbell_team1_esp32_features.{npz,csv},data_card.md,team_01_preview.wav}` + sibling `../edge_ai_assignment2/speech_pool.npz` |
| 8 | Feature extraction outputs available | **COMPLETE** | 8 `student1_esp32/feature_arrays/*.npz`, 6 `student2_python/feature_arrays/*.npz`, 1 clean `dataset/*.npz` & `.csv` |
| 9 | Packet and frame logs available | **COMPLETE** | 11 JSON logs in `student1_esp32/logs/` + `mission1_throughput.csv` (75 runs) |
| 10 | Validation and ML outputs available | **COMPLETE** | `student4_validation/outputs/{mission4_validation_summary.json,mission5_feature_comparison.{json,csv},mission5_classifier_results.{json,csv},nearest_centroid_model.npz,plots/*.png}` |
| 11 | Frontend source code available | **COMPLETE** | `student3_frontend/src/` (10 pages, 5 charts, 4 UI components, API/fallback layers) + `vite.config.ts` |
| 12 | Backend/API integration available | **COMPLETE** | `student2_python/api/server.py` (Flask) + `shared/frontend_api_contract.json` (`v1.1.0`) + Vite `/api/*` & `/repo/*` bridges |
| 13 | README and setup instructions complete | **COMPLETE** | Root `README.md`, per-student `README.md`, `IMPLEMENTATION_AND_INTEGRATION_GUIDE.md` for Students 3 & 4 |
| 14 | Required dependencies documented | **COMPLETE** | `student2_python/requirements.txt` (`numpy,pyserial,matplotlib,scipy,pandas,scikit-learn,flask,pytest`), `student3_frontend/package.json` & `package-lock.json` |
| 15 | No essential technical files missing | **COMPLETE** | `test_frontend_api_contract_all_paths_exist` confirms every asset in `frontend_api_contract.json` resolves cleanly on disk |

---

## 2. Structural & Cleanliness Notes

- **Unmodified Faculty Assets Preserved:** `starter_files/{README.md,TEAMS.csv,team_audio.py,board_link.py}` match the faculty starter pack; `speech_pool.npz` (~13 MB) is kept out of Git via `.gitignore` and resolved cleanly via `student2_python/src/paths.py` (`../edge_ai_assignment2/speech_pool.npz`).
- **NPZ Key Naming Convention Note:** `dataset/doorbell_team1_esp32_features.npz` uses singular keys (`clip_id`, `label`), while `student1_esp32/feature_arrays/esp32_clips_*.npz` and `student2_python/feature_arrays/*.npz` use plural keys (`clip_ids`, `labels`). All consumers are aligned and covered by pytest.
- **Git Branch State:** All Stage B and Stage C review artifacts sit on branch `stage-b-review` (PR #11) and have not yet been merged into `main` pending final user permission.

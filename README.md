# Smart-Doorbell — Edge AI (Module 2: "The Doorbell's Ears")

**Team 1 (`Paradise`)** · **Course:** AI255TBD Edge AI  
**Board Operator (Student 1):** Siddharth Dhanush R  
**Target Hardware:** ESP32-S3-DevKitC-1 N16R8 (`16 MB` Flash, `8 MB` OPI PSRAM)

---

## Repository Layout

```text
Smart-Doorbell/
├── starter_files/            # Unmodified faculty README.md, TEAMS.csv, team_audio.py, board_link.py
│                             # (Place speech_pool.npz here or in ../edge_ai_assignment2/)
├── shared/                   # Team-wide configs, protocol spec, and frontend API contract
├── dataset/                  # 144-clip manifest, validation report, team_01_preview.wav,
│                             # clean ESP32 7,056-frame dataset (.npz/.csv), and data_card.md
├── student1_esp32/           # Firmware (doorbell_board + starter), benchmarks, hardware logs, reports
├── student2_python/          # Codec, PySerial/Mock sender, NumPy HTK log-mel, Flask API, pytest suite
├── student3_frontend/        # Dashboard implementation & integration guide (for Student 3)
└── student4_validation/      # Missions 4 & 5 validation & ML guide (for Student 4)
```

## Quick Start (No Board Needed for Students 2, 3 & 4)

```powershell
# 1. Install Python dependencies
py -m pip install -r student2_python/requirements.txt

# 2. Run all Python unit & API tests
py -m pytest -v

# 3. Start Student 2's board-free JSON API server for the dashboard
py student2_python/api/server.py --port 5000
```

> **Note on `speech_pool.npz`:** Because `speech_pool.npz` (~13 MB) is excluded by `.gitignore`, place a local copy in `starter_files/speech_pool.npz` (or keep it in `../edge_ai_assignment2/speech_pool.npz`) before regenerating raw audio waveforms or `/api/clips/<id>`. All pre-extracted `.npz`/`.csv` feature arrays, logs, and benchmark reports are already committed in the repository.

## Role Guides
- **Student 1:** [student1_esp32/README.md](student1_esp32/README.md) & [Phase 5 Handover](student1_esp32/documentation/phase5_final_handover_report.md)
- **Student 2:** [student2_python/README.md](student2_python/README.md)
- **Student 3:** [student3_frontend/IMPLEMENTATION_AND_INTEGRATION_GUIDE.md](student3_frontend/IMPLEMENTATION_AND_INTEGRATION_GUIDE.md)
- **Student 4:** [student4_validation/IMPLEMENTATION_AND_INTEGRATION_GUIDE.md](student4_validation/IMPLEMENTATION_AND_INTEGRATION_GUIDE.md)

# Student 2 — Python Backend & Audio Processing (Team 1: Paradise)

**Primary Specification:** `edge_ai_assignment2/README.md`  
**Owner (Student 2):** Rakshith Raghavendra (assisted by Siddharth Dhanush R)

## Environment Setup

On Windows (using `py` launcher for Python 3.14):

```powershell
py -m pip install -r student2_python/requirements.txt
```

## Phase 1: Dataset Inspection & Manifest

Generates `dataset/dataset_manifest.csv` and `dataset/dataset_validation.json` from `edge_ai_assignment2/team_audio.py` (`team=1`, `144` clips) without modifying `team_audio.py` or `speech_pool.npz`:

```powershell
py student2_python/src/dataset_inspect.py --team 1 --fs 16000
```

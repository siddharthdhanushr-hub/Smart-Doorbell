# Student 2 — Python Backend & Audio Processing (Team 1: Paradise)

**Primary Specification:** `../edge_ai_assignment2/README.md`  
**Owner (Student 2):** Rakshith Raghavendra (completed with Siddharth Dhanush R)

## Environment Setup
```powershell
py -m pip install -r student2_python/requirements.txt
```

## Modules
- `src/dataset_inspect.py` — Validates all 144 Team 1 clips from `edge_ai_assignment2/team_audio.py` and generates `dataset/dataset_manifest.csv` and `dataset/dataset_validation.json`.
- `src/mission2_audio_analysis.py` — Runs the `48 kHz` vs `8 kHz` aliasing spectrum experiment (`antialias=False` vs `True`) and `int16`/`int8` SQNR comparisons.
- `preprocessing/audio_codec.py` — Exact `quantise()`, `dequantise()`, `pack()`, `unpack()`, `sqnr_db()` matching `README.md` Section 5.
- `transmission/serial_sender.py` — `build_frame()`, `parse_uplink_frames()`, `ClipLoader`, and board-free `MockBoard`.
- `transmission/batch_pipeline.py` — `transmit_clip()` and `transmit_batch()` reusable pipelines.
- `logmel/reference_logmel.py` — Pure NumPy reference `features(x, fs, win, hop, nfft, mels, mfcc)` matching `features.h` within `<= 0.0001 dB`.

## Running Tests & Exports (No Board Required)
```powershell
py -m pytest -v student2_python/tests
py student2_python/src/dataset_inspect.py --team 1 --fs 16000
py student2_python/src/mission2_audio_analysis.py
py student2_python/logmel/reference_logmel.py --team 1
```

## Known Limitations & Design Notes
- `edge_ai_assignment2/team_audio.py` and `speech_pool.npz` are kept untouched in `../edge_ai_assignment2/` per faculty rules.
- Feature extraction uses the custom pure-NumPy HTK mel recipe (`20 Hz..fs/2`, unnormalized power `/ nfft`, symmetric `np.hanning`, `10*log10(max(m, 1e-10))`) rather than Librosa defaults so laptop and ESP32 values align numerically.

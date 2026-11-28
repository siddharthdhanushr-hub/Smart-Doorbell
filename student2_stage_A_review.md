# Student 2 Stage A Review Report — Python Backend & Audio Processing

**Project:** Smart-Doorbell — Edge AI Module 2 (*"The Doorbell's Ears"*)  
**Team:** Team 1 (`Paradise`) · **Target Hardware:** ESP32-S3-DevKitC-1 N16R8  
**Review Date:** 2026-11-28  
**Reviewer Mode:** Static code audit, committed dataset/NPZ/log verification, and offline Python `pytest` / script execution (no physical ESP32-S3 attached; `speech_pool.npz` absent locally per `.gitignore`).

---

## 1. Tasks Reviewed

1. **Dataset & Metadata Audit:** Verified `dataset/dataset_manifest.csv`, `dataset/dataset_validation.json`, `dataset/data_card.md`, `dataset/team_01_preview.wav`, `dataset/doorbell_team1_esp32_features.{npz,csv}`, `student2_python/src/dataset_inspect.py`, and `starter_files/` integrity.
2. **Python Environment & Dependencies:** Checked `student2_python/requirements.txt`, `student2_python/README.md`, root `README.md`, `pytest.ini`, `pyrightconfig.json`, and clean-environment importability on Python 3.13 (`C:\Users\raksh\AppData\Local\Programs\Python\Python313\python.exe`).
3. **Audio Preprocessing (`preprocessing/audio_codec.py`, `src/mission2_audio_analysis.py`):** Verified `quantise()`, `dequantise()`, `pack()`, `unpack()`, `pack_and_reconstruct()`, `sqnr_db()`, `f32`/`i16`/`i8` formats, scaling, clipping, mono handling, and resampling/anti-aliasing logic.
4. **Serial Transmitter & Protocol (`transmission/serial_sender.py`, `starter_files/board_link.py`, `shared/communication_protocol.json`):** Verified `0xA5 0x5A` / `0xB5 0x5B` framing, IEEE CRC-32 coverage, `4096 B` payload cap, sequence gap/duplicate detection, `MockBoard`, `ClipLoader`, and Student 1 transmission logs (`student1_esp32/logs/`).
5. **Complete & Batch Pipeline (`transmission/batch_pipeline.py`):** Verified `transmit_clip()` and `transmit_batch()` clip ID mapping, sample offsets, payload sizing, and `MockBoard` transmission statistics.
6. **Python Log-Mel & MFCC Extraction (`logmel/reference_logmel.py`, `shared/logmel_config.json`):** Verified pure-NumPy HTK log-mel/MFCC implementation (used intentionally instead of Librosa to match ESP32 `features.h`), frame parameters, Hann windowing, FFT/power spectrum, mel bounds, log10 floor, DCT-II orthonormality, and `.npz` exports.
7. **Reproducibility & Naming Conventions:** Verified deterministic repeatability of `features()`, cross-file consistency across `student2_python/feature_arrays/`, `student1_esp32/feature_arrays/`, and `dataset/`, configuration alignment with `shared/*.json`, and README accuracy.
8. **Code Quality Review:** Checked modularity, duplicated logic, exception handling, hardcoded paths/values, unused/missing dependencies, and logging/docstrings.
9. **Targeted Bug Fixing & Re-Testing:** Applied minimal, non-invasive fixes for confirmed defects and re-verified with `py_compile` and `pytest`.

---

## 2. Dataset Verification Results

- **Original Starter Files Unmodified:** Confirmed via `git diff --stat starter_files/` (zero changes to `team_audio.py`, `board_link.py`, `TEAMS.csv`, and `README.md`).
- **Missing External Asset (`speech_pool.npz`):** Excluded by `.gitignore` and not present in `starter_files/` or `../edge_ai_assignment2/`. Live synthesis via `team_audio.get_clip()` could not run on this machine; all dataset metadata, preview WAV, and committed feature archives were audited directly.
- **Manifest (`dataset/dataset_manifest.csv`) & Validation (`dataset/dataset_validation.json`):**
  - **Total clips:** `144` (`valid_clips = 144`, `invalid_clip_ids = []`).
  - **Clip IDs:** Contiguous `0..143` (`clip_id == list(range(144))` verified).
  - **Labels (balanced):** `on`: 24, `off`: 24, `stop`: 24, `go`: 24, `_unknown`: 24, `_silence`: 24.
  - **Audio Properties:** `sample_rate = 16000` Hz, `num_channels = 1` (mono), `duration_s = 1.0` s (`16000` samples/clip), `format = float32`, `antialias = True`, `clipped = False` across all 144 clips (global peak `0.67562 < 1.0`).
  - **Duplicates:** `120` non-silence clips map to `120` unique `pool_index` values (`duplicate_non_silence_pool_recordings = 0`).
- **Preview Audio (`dataset/team_01_preview.wav`):** Verified `1` channel, `16-bit` PCM (`sampwidth = 2`), `16000 Hz`, `240000` frames (`15.0 s`).
- **Clean ESP32 Feature Dataset (`dataset/doorbell_team1_esp32_features.npz` & `.csv`):**
  - Both contain `7,056` rows/frames (`49` frames/clip × `144` clips; `143` inter-clip straddling frames excluded per `dataset/data_card.md`).
  - Class balance verified: `1,176` frames per class across all 6 classes, `144` unique `clip_id`s, `44` CSV columns (`clip_id`, `label`, `first_sample`, `compute_us`, `mel_00`..`mel_39`).
  - `doorbell_team1_esp32_features.npz` reshaped `(144, 49, 40)` matches `student1_esp32/feature_arrays/esp32_clips_16k_i16_S1.0_speed1.npz` bit-for-bit (`True`).
- **Python vs. ESP32 Feature Array Cross-Check:**
  - `python_ref_team1_16000hz_f32_...npz['features']` == `python_ref_clips_16k_i16_S1.0_speed1.npz['features_orig_f32']` (`max_abs = 0.0`).
  - `python_ref_team1_16000hz_i16_...npz['features']` == `python_ref_clips_16k_i16_S1.0_speed1.npz['features_quantised']` (`max_abs = 0.0`).
  - `esp32_clips_16k_i16_S1.0_speed1.npz` vs `python_ref_clips_16k_i16_S1.0_speed1.npz['features_quantised']`: `MAE = 1.606e-6 dB`, `MaxAbs = 0.000137 dB`.
  - All 6 `student2_python/feature_arrays/*.npz` files are finite (`NaN`/`Inf` free) with exact `clip_ids` (`0..143`) and matching `labels`.

---

## 3. Tests Performed

1. **Baseline `pytest` collection (`student2_python/tests` + `student4_validation/tests`):**
   - `python -m pytest -v student2_python/tests student4_validation/tests`
2. **Baseline `pytest` execution (excluding Flask collection error):**
   - `python -m pytest -v student2_python/tests/test_phase2_codec_and_protocol.py student2_python/tests/test_phase4_reference_logmel.py`
3. **Standalone Programmatic Verification (`verify_student2.py`):**
   - Package availability check (`numpy`, `scipy`, `matplotlib`, `pandas`, `pytest`, `serial`, `flask`, `sklearn`, `librosa`).
   - Manifest CSV (`144` rows), preview WAV, dataset CSV (`7,056` rows), and all 15 `.npz` files across `student2_python/`, `student1_esp32/`, and `dataset/`.
   - Multi-signal codec SQNR checks (`f32`, `i16`, `i8` at `S=1.0, 0.25` on `tone+noise` and `silence`, plus zero-signal and zero-error boundary cases).
   - `MockBoard` + `batch_pipeline` (`transmit_clip`, `transmit_batch`, `dump`, `bad_len`, `parse_uplink_frames`).
   - `reference_logmel.features()` deterministic repeatability and `win > nfft` silent-truncation reproduction.
4. **Post-Fix Verification:**
   - `py_compile` across all modified Python files (`server.py`, `reference_logmel.py`, `batch_pipeline.py`, `serial_sender.py`, `dataset_inspect.py`).
   - Power-of-2 `nfft` check across all 7 `ALLOWED_FS` rates (`48000, 24000, 16000, 12000, 8000, 6000, 4000`).
   - Re-ran `pytest -v student2_python/tests/test_phase2_codec_and_protocol.py student2_python/tests/test_phase4_reference_logmel.py` (10 tests total including 2 newly added regression tests).

---

## 4. Passed Tests

After fixes, **9 of 10** tests in `test_phase2_codec_and_protocol.py` and `test_phase4_reference_logmel.py` passed (`2.54 s`), plus all offline verification checks:

- `test_quantise_pack_unpack_i16_and_i8` — **PASSED**
- `test_quantise_f32_exact` — **PASSED**
- `test_quantise_clipping_with_smaller_scale` — **PASSED**
- `test_frame_crc_and_mock_board_skip` — **PASSED** (`bad_crc=1`, `seq_gaps=2`, `frames_ok=9`)
- `test_batch_pipeline_with_mock_board` *(added)* — **PASSED** (`transmit_clip`, `transmit_batch`, `MockBoard.dump`, empty `clip_ids` `ValueError`)
- `test_logmel_shape_and_first_sample` — **PASSED** (`(49, 40)`, `float32`, `first_sample` `0..15360`)
- `test_mfcc_dct_orthonormal` — **PASSED** (`gram == I_13` within `1e-12`, `(98, 13)`)
- `test_mel_filterbank_htk_bounds` — **PASSED** (`(40, 257)`, `[0, 1]`, non-zero band sums)
- `test_features_rejects_invalid_nfft_and_win` *(added)* — **PASSED** (`win > nfft` and non-power-of-2 `nfft` raise `ValueError`)
- **Offline script checks** — **PASSED** (`dataset_manifest.csv`, `team_01_preview.wav`, `doorbell_team1_esp32_features.{npz,csv}`, NPZ cross-consistency `0.0` / `1.6e-6 dB`, `sqnr_db` multi-signal & edge cases, `MockBoard` `transmit_clip`/`transmit_batch`, `py_compile`, and `nfft` scaling across all 7 `ALLOWED_FS` values).

---

## 5. Failed Tests

- `student2_python/tests/test_api_server.py` (collection error): `ModuleNotFoundError: No module named 'flask'` (Flask is not installed in this machine's Python 3.13 environment and was missing from `student2_python/requirements.txt`).
- `student2_python/tests/test_phase2_codec_and_protocol.py::test_clip_loader_team1` (**FAILED**): `FileNotFoundError: speech_pool.npz must be in the same folder as team_audio.py` (blocked solely by the `.gitignore`-excluded `speech_pool.npz`).
- *(Outside Student 2 scope, observed in initial combined run)* `student4_validation/tests/test_metrics_and_split.py` (collection error): `ModuleNotFoundError: No module named 'sklearn'` in this machine's Python 3.13 environment.

---

## 6. Bugs Discovered

1. **Missing `flask` dependency in `student2_python/requirements.txt` (High):** `api/server.py` and `tests/test_api_server.py` import `flask`, yet `requirements.txt` did not list `flask`, breaking fresh environment setup and test collection.
2. **Wrong `nfft` for `fs > 16000` and unhandled `FileNotFoundError` in `student2_python/api/server.py` (Medium):**
   - `clip_detail()` hardcoded `nfft = 512 if fs == 16000 else 256` while allowing `fs=24000` (`win=720`) and `fs=48000` (`win=1440`), causing `win > nfft` and silent FFT truncation.
   - Missing `speech_pool.npz` caused an unhandled `FileNotFoundError` (HTTP 500) on `/api/clips/<clip_id>` instead of a clean JSON error response.
3. **Missing parameter validation in `student2_python/logmel/reference_logmel.py` (Medium):** `features()` allowed `win > nfft`, non-power-of-2 `nfft`, `win < 2`, `hop < 1`, etc. (unlike ESP32 `features.h`), silently truncating frames in `np.fft.rfft`.
4. **Empty `clip_ids` bug & unused imports in `student2_python/transmission/batch_pipeline.py` (Low):** `transmit_batch(..., clip_ids=[])` produced `max_bytes=0`, which `doorbell_board.ino` rejects when `store != "none"`; unused `json` and `pack` imports were present (and unused `Iterable`, `Optional` in `serial_sender.py`).
5. **Empty-rows guard missing in `student2_python/src/dataset_inspect.py` (Low):** `rows[0].keys()` in `main()` lacked an empty-list check.
6. **Stale hardcoded numbers in `student2_python/src/mission2_audio_analysis.py` (Low, unedited):** Line 185 rationale string says `"max amplitude 0.6705 < 1.0"` and `">69 dB"`, whereas the measured values in `mission2_audio_analysis.json` are `0.67562` and `74.21 dB`.

---

## 7. Bugs Fixed

All fixes were kept minimal and preserved existing interfaces:

1. **[student2_python/requirements.txt](file:///c:/Users/raksh/OneDrive/Desktop/Smart-Doorbell/student2_python/requirements.txt):** Added `flask>=3.0`.
2. **[student2_python/api/server.py](file:///c:/Users/raksh/OneDrive/Desktop/Smart-Doorbell/student2_python/api/server.py):**
   - Replaced hardcoded `nfft` ternary with `nfft = 1 << (win - 1).bit_length()` (verified across all 7 `ALLOWED_FS` rates: `128..2048`).
   - Wrapped `ta.get_clip(...)` in `try/except FileNotFoundError` returning JSON HTTP `503` with a clear hint to place `speech_pool.npz` in `starter_files/`.
3. **[student2_python/logmel/reference_logmel.py](file:///c:/Users/raksh/OneDrive/Desktop/Smart-Doorbell/student2_python/logmel/reference_logmel.py):** Added input validation in `features()` enforcing `fs > 40`, `win >= 2`, `hop >= 1`, `nfft >= win` and power-of-2, `mels >= 1`, and `0 <= mfcc <= mels`; removed unused `json` and `Dict` imports.
4. **[student2_python/transmission/batch_pipeline.py](file:///c:/Users/raksh/OneDrive/Desktop/Smart-Doorbell/student2_python/transmission/batch_pipeline.py):** Added `if not ids: raise ValueError("clip_ids must not be empty")` in `transmit_batch()`, defined `ClipLoaderProtocol` for clean static typing, and removed unused `json`, `pack`, and `np` imports.
5. **[student2_python/transmission/serial_sender.py](file:///c:/Users/raksh/OneDrive/Desktop/Smart-Doorbell/student2_python/transmission/serial_sender.py):** Removed unused `Iterable`, `Optional`, and `unpack` imports.
6. **[student2_python/src/dataset_inspect.py](file:///c:/Users/raksh/OneDrive/Desktop/Smart-Doorbell/student2_python/src/dataset_inspect.py):** Added `if not rows: raise RuntimeError(...)` guard before writing `dataset_manifest.csv`.
7. **[student2_python/tests/test_phase2_codec_and_protocol.py](file:///c:/Users/raksh/OneDrive/Desktop/Smart-Doorbell/student2_python/tests/test_phase2_codec_and_protocol.py) & [student2_python/tests/test_phase4_reference_logmel.py](file:///c:/Users/raksh/OneDrive/Desktop/Smart-Doorbell/student2_python/tests/test_phase4_reference_logmel.py):** Added `test_batch_pipeline_with_mock_board` and `test_features_rejects_invalid_nfft_and_win`.

---

## 8. Tests Not Performed

- **Live ESP32-S3 USB/UART Serial Transmission:** No physical ESP32-S3 board was attached during this review (`pyserial` is also absent in this local Python environment). Live hardware protocol compatibility was verified by inspecting `starter_files/board_link.py`, `student1_esp32/firmware/doorbell_board/doorbell_board.ino`, and committed hardware logs (`mission1_pipe_results.json`, `mission4_skip_after_fix.json`, `phase5_144clips_all_runs.json`).
- **Live Audio Synthesis & End-to-End Flask `/api/clips/<id>` Test (`test_api_server.py`, `test_clip_loader_team1`, `dataset_inspect.py`, `mission2_audio_analysis.py`):** Not executed live because `speech_pool.npz` and `flask` are not present on this machine.
- **Librosa Comparison Execution:** `librosa` is not used (by design, as `student2_python/README.md` documents the pure-NumPy HTK recipe to stay within `<= 0.0001 dB` of `features.h`) and is not installed here.

---

## 9. Remaining Issues

1. **Local Environment Dependencies & `speech_pool.npz`:** Running `test_api_server.py`, `test_clip_loader_team1`, and `/api/clips/<id>` requires installing the updated `student2_python/requirements.txt` (with `flask` and `pyserial`) and placing `speech_pool.npz` in `starter_files/`.
2. **Two NPZ Naming/Schema Conventions in `student2_python/feature_arrays/`:**
   - `reference_logmel.py` writes `python_ref_team1_16000hz_{fmt}_S{scale}_win{win}_hop{hop}_mels{mels}_mfcc{mfcc}.npz` (`features`, `clip_ids`, `labels`, `first_sample`, scalar metadata).
   - `student1_esp32/benchmarks/phase5_full_pipeline.py` writes `python_ref_clips_{tag}.npz` (`features_orig_f32`, `features_quantised`, `clip_ids`, `labels`).
   Both are documented and aligned numerically, though a single unified schema would reduce confusion in future stages.
3. **Code Duplication & MockBoard Fidelity (Non-blocking):**
   - `REPO_ROOT` / `ASSIGNMENT_DIR` `sys.path` setup is repeated across multiple scripts instead of a shared helper in `paths.py`.
   - `MockBoard.stream()` returns an empty `features` array `(0, dim)` even when `feat=True` and omits `first_sample`, `compute_us`, and `lag_s`.
   - `dataset_inspect.py` writes `"source": "edge_ai_assignment2/team_audio.py"` regardless of `--assignment-dir`, and `mission2_audio_analysis.py` rationale text retains `"0.6705"` / `">69 dB"` instead of interpolating `0.67562` / `74.21 dB`.

---

## 10. Readiness for Stage B Integration

**Status: READY (with documented environment prerequisites)**

- **Codec, Protocol Framing, Batch Pipeline, and Pure-NumPy HTK Log-Mel/MFCC:** Verified deterministic, numerically aligned with ESP32 `features.h` (`1.61e-6 dB` MAE), and passing all offline unit tests.
- **Dataset & Feature Exports:** All `144` clips (`7,056` clean frames) and `6` Python reference `.npz` archives are intact, finite, balanced, and verified against ESP32 hardware outputs.
- **Before Stage B live integration runs:** Install `py -m pip install -r student2_python/requirements.txt` in a clean environment, place `speech_pool.npz` in `starter_files/`, and execute `py -m pytest -v` to confirm `test_api_server.py` and `test_clip_loader_team1` pass end-to-end.

---

### Verified Inventory

- **Python Source Files (`student2_python/`):**
  - `student2_python/src/paths.py`
  - `student2_python/src/dataset_inspect.py`
  - `student2_python/src/mission2_audio_analysis.py`
  - `student2_python/preprocessing/audio_codec.py`
  - `student2_python/transmission/serial_sender.py`
  - `student2_python/transmission/batch_pipeline.py`
  - `student2_python/logmel/reference_logmel.py`
  - `student2_python/api/server.py`
  - `student2_python/tests/test_phase2_codec_and_protocol.py`
  - `student2_python/tests/test_phase4_reference_logmel.py`
  - `student2_python/tests/test_api_server.py`
- **Feature Arrays (`student2_python/feature_arrays/` & `dataset/`):**
  - `student2_python/feature_arrays/python_ref_team1_16000hz_f32_S1.0_win480_hop320_mels40_mfcc0.npz`
  - `student2_python/feature_arrays/python_ref_team1_16000hz_i16_S1.0_win480_hop320_mels40_mfcc0.npz`
  - `student2_python/feature_arrays/python_ref_clips_16k_i16_S1.0_speed1.npz`
  - `student2_python/feature_arrays/python_ref_clips_16k_i8_S1.0.npz`
  - `student2_python/feature_arrays/python_ref_clips_16k_i8_S0.25.npz`
  - `student2_python/feature_arrays/python_ref_clips_8k_i16_S1.0_noaa.npz`
  - `dataset/doorbell_team1_esp32_features.npz` & `dataset/doorbell_team1_esp32_features.csv`
- **Dataset Metadata & Preview (`dataset/`):**
  - `dataset/dataset_manifest.csv`
  - `dataset/dataset_validation.json`
  - `dataset/data_card.md`
  - `dataset/team_01_preview.wav`
- **Configuration Files (`shared/`, `student2_python/`, root):**
  - `shared/audio_config.json`
  - `shared/communication_protocol.json`
  - `shared/frontend_api_contract.json`
  - `shared/hardware_config.json`
  - `shared/logmel_config.json`
  - `student2_python/requirements.txt`
  - `pytest.ini`
  - `pyrightconfig.json`

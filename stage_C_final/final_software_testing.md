# Final Software Testing Report (Python Pipeline, API & Validation)

**Environment:** Windows 11, `Python 3.14.7`, `pytest 9.1.1`, `../edge_ai_assignment2/speech_pool.npz` present  
**Final Re-Test Execution:** `C:\WINDOWS\py.exe -m pytest -v student2_python/tests student4_validation/tests` → **`18 passed in 3.99s`** (0 failed, 0 skipped)

---

## 1. Python Pipeline Modules Verified (`student2_python/`)

1. **`src/dataset_inspect.py` & `dataset/dataset_validation.json`:** Verified `144` valid clips (`24`/class), `16,000 Hz`, mono, `1.0 s`, `0` clipped (`dataset_global_peak_abs = 0.67562`), `0` duplicate pool indices.
2. **`preprocessing/audio_codec.py`:** Verified `quantise()`, `dequantise()`, `pack()`, `unpack()`, and `sqnr_db()` across `<f4`, `<i2`, and `int8`, scale `S` clipping, and invalid-input errors (`test_phase2_codec_and_protocol.py` — 3 codec tests passed).
3. **`transmission/serial_sender.py` & `batch_pipeline.py`:**
   - Verified binary framing `build_frame()` / `parse_uplink_frames()` CRC-32 validation (`bad_crc=1` rejection), `ClipLoader` loading real Team 1 audio, `transmit_clip()`, `transmit_batch()`, and `MockBoard` skip accounting (`skip=(2, 5)` and Stage B `skip=(0,)` regression fix).
4. **`logmel/reference_logmel.py`:**
   - Verified `(49, 40)` `float32` output, symmetric `np.hanning`, HTK mel filterbank bounds `[20 Hz .. 8000 Hz]`, orthonormal `build_dct_matrix` (`gram = I_13` within `1e-12`), MFCC `(98, 13)`, and invalid-config `ValueError` assertions (`4/4` tests passed).
5. **`api/server.py` (Flask Backend):**
   - Verified `/api/health`, `/api/configs`, `/api/dataset`, `/api/clips/<id>`, and `/api/benchmarks/mission{1,2,3,4_5}` via `test_api_server.py` AND live HTTP calls (`HTTP 200`, `(16000,)` waveform, `(49, 40)` Python + ESP32 log-mel).

---

## 2. Student 4 Validation & ML Suite Verified (`student4_validation/`)

- **`tests/test_metrics_and_split.py` (`5/5` passed):** Verifies exact MAE/MSE/RMSE formulas, NaN/shape mismatch checks, zero-leakage stratified 96/48 clip split, separable cluster 100% sanity check, split reproducibility, and real Mission 4 log metrics (`144` valid clips, `6.0×` COM11, `2.5×` @ 921.6k / `6.0×` @ 2M COM12).
- **`tests/test_stage_b_integration.py` (`2/2` passed):** Verifies all paths in `shared/frontend_api_contract.json` (`v1.1.0`) exist on disk and confirms `mission5_feature_comparison.json` compares `8k_i16_S1.0_noaa` against the true `"8 kHz filtered (antialias=True) Python float32 reference"` (`mae_db > 5.0`).
- **Stage C End-to-End Inference Check (`task-934`):** Loaded `student4_validation/outputs/nearest_centroid_model.npz` against live `COM11` hardware features on 6 held-out test clips (`0, 25, 48, 73, 105, 126`) → `6/6` accurate class predictions and `<= 1.87e-06 dB` MAE.

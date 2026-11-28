# Student 2 Integration Review — Python Backend, Audio Pipeline & API

**Component:** `student2_python/` · **Owner:** Rakshith Raghavendra (with Siddharth Dhanush R)  
**Stage B Status:** **PASS** *(All 11 Student 2 unit/API tests + Stage B parity checks passing after 1 `MockBoard` fix)*

---

## 1. Dataset Discovery, Preprocessing & Codec (`src/`, `preprocessing/`)

- **Path Resolution (`src/paths.py`):** Verified `resolve_starter_dir()` prefers `starter_files/` if `speech_pool.npz` exists locally, and otherwise falls back cleanly to sibling `../edge_ai_assignment2/` (active in this workspace).
- **Dataset Validation (`src/dataset_inspect.py`):** Deterministic `144` clips (`24`/class across `on`, `off`, `stop`, `go`, `_unknown`, `_silence`), `16,000 Hz`, mono, `1.0 s` (`16,000` samples), `0` clipped (`max_abs < 1.0`), `0` duplicate pool indices.
- **Audio Codec (`preprocessing/audio_codec.py`):** Exact Section 5 quantisation/dequantisation equations (`<f4`, `<i2`, `int8`), scale `S`, SQNR computation, and payload validation (`ValueError` on non-positive scale, bad format, or non-integer sample length).
- **Aliasing & SQNR Analysis (`src/mission2_audio_analysis.py`):** `documentation/mission2_audio_analysis.json` aligns with `HardwarePerformancePage` (`7,348 Hz` tone aliases to `652 Hz` at `8 kHz` without AA; `51.8 dB` suppression with AA; `74.21 dB` mean SQNR for `i16 S=1.0` across 144 clips).

---

## 2. Protocol & Serial Transmission (`transmission/`)

- **`serial_sender.py`:** `build_frame()` & `parse_uplink_frames()` match `doorbell_board.ino` byte-for-byte (`0xA5 0x5A`, `<IH` `seq`/`len`, `MAX_PAYLOAD_BYTES=4096`, IEEE `zlib.crc32`).
- **Bug Found & Fixed (`BUG-04`):** `MockBoard.stream()` previously checked `if last_seq >= 0 and rseq != last_seq + 1:`, missing skipped packet `0` (`seq=0`). Fixed to detect `if last_seq < 0 and rseq > 0: seq_gaps += rseq` matching firmware `doorbell_board.ino` line 200; verified with regression assertion `skip=(0,)` in `test_phase2_codec_and_protocol.py`.
- **Known `MockBoard` Limitation (`BUG-06`):** `MockBoard.stream()` counts received samples only (no zero-fill on gaps, asserted by existing `test_phase2_codec_and_protocol.py` line 77) and returns empty `features = np.zeros((0, dim))` — clearly tagged `mock: True` so it cannot be mistaken for hardware execution.
- **`batch_pipeline.py`:** `transmit_clip()` and `transmit_batch()` validate empty clip lists, propagate `speed`/`store`/`skip`, and pass tests with `MockBoard`.

---

## 3. Pure-NumPy Reference Log-Mel (`logmel/reference_logmel.py`)

- Recipe strictly follows `README.md` Section 5 & `shared/logmel_config.json` (not Librosa defaults): symmetric `np.hanning(win)`, unnormalized `|rfft|^2 / nfft`, HTK `2595 * log10(1 + f/700)` (`20 Hz .. fs/2`), `10 * log10(max(m, 1e-10))`, optional orthonormal DCT-II.
- Input guardrails raise `ValueError` when `nfft < win`, non-power-of-2 `nfft`, or invalid `fs`/`hop`/`mels`/`mfcc`.
- **Cross-Check:** Clip 0 freshly extracted Python `i16` log-mel vs committed `esp32_clips_16k_i16_S1.0_speed1.npz` gives **`MAE = 1.62e-06 dB`**, **`max = 2.67e-05 dB`** (`< 0.05 dB` requirement).

---

## 4. Backend Flask API (`api/server.py`)

- Offline board-free Flask app (`live_board_required: false`) verified via `pytest` (`test_api_server.py`) AND live HTTP requests on port `5000`:
  - `GET /api/health` → `200` (`status: ok`, `live_board_required: false`)
  - `GET /api/configs` → `200` (`hardware`, `audio`, `logmel`, `protocol`)
  - `GET /api/dataset` → `200` (`144`-row manifest, validation summary, `data_card_md`)
  - `GET /api/clips/<id>?fs=...&antialias=...` → `200` (`16,000`/`8,000` waveform, Python `(49, 40)` log-mel, and matched ESP32 `(49, 40)` log-mel when `fs=16000 & antialias=true`)
  - `GET /api/benchmarks/mission{1,2,3,4_5}` → `200`
  - Missing `speech_pool.npz` returns clean HTTP `503` JSON on `/api/clips/<id>` rather than uncaught traceback.

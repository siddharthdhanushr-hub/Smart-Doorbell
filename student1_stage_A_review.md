# Stage A Review — Student 1: ESP32-S3 Hardware & Embedded Systems

**Reviewer Role:** Stage A Technical Auditor  
**Target Team / Project:** Team 1 (`Paradise`) · Smart Doorbell – Edge AI (`ESP32-S3-DevKitC-1 N16R8`)  
**Review Date:** 2026-11-28  
**Branch Audited:** `siddharth`  

---

## 1. Tasks Reviewed

1. **ESP32-S3 Setup & Configuration:** Inspected `shared/hardware_config.json`, `student1_esp32/documentation/setup_and_phase1.md`, `student1_esp32/README.md`, `student1_esp32/firmware/doorbell_board/partitions.csv`, and compiled via `arduino-cli` (`esp32:esp32 3.3.12`).
2. **Serial Communication:** Audited `doorbell_board.ino`, `starter_files/board_link.py`, `shared/communication_protocol.json`, `student1_esp32/benchmarks/mission1_pipe_benchmark.py`, `mission1_throughput.csv`, and `mission1_pipe_results.json` (`f32`, `i16`, `i8`, little-endian byte order, `A5 5A`/`B5 5B` framing, `CRC-32`).
3. **Audio Reception & Buffering:** Audited `runStream()`, `pushSamples()`, `fbuf`/`fout`, `storeBuf` allocation, sample-rate/format decoding, and Mission 4 packet-gap sample alignment (`mission4_skip_before_fix.json`, `mission4_skip_after_fix.json`).
4. **Audio Storage & Persistence:** Audited `freeStore()`, `heap_caps_malloc` (SRAM vs OPI PSRAM), `cmdSave()` (`LittleFS /rec.bin`), `cmdDump()`, `partitions.csv` (`6.88 MiB` LittleFS), `mission2_probe_baseline.json`, `mission2_save144_opi_16m.json`, and `mission2_verify_opi_16m.json`.
5. **ESP32 Log-Mel Extraction:** Audited `student1_esp32/firmware/doorbell_board/features.h` against `shared/logmel_config.json` and `student2_python/logmel/reference_logmel.py`, plus all 8 exported `.npz` files in `student1_esp32/feature_arrays/` and `dataset/doorbell_team1_esp32_features.*`.
6. **Hardware Performance & Logs:** Audited `mission3_starter_10s.json`, `mission3_optimized_results.json`, `mission4_com_speed_ramp.json`, and `phase5_144clips_all_runs.json`.
7. **Code Quality:** Audited modularity, memory management, error handling, integer/unsigned edge cases, compiler warnings (`--warnings all`), and hardcoded limits.

---

## 2. Tests Performed During This Review

| Test | Command / Method | Scope | Outcome |
|---|---|---|---|
| **Port Discovery** | `py starter_files/board_link.py ports` + `Win32_PnPEntity` | Check if physical ESP32-S3 is attached | Only Bluetooth ports (`COM3, COM6, COM7, COM10`) present — **no physical board connected** |
| **Firmware Compilation (Before Fixes)** | `arduino-cli compile --warnings all --fqbn esp32:esp32:esp32s3:CDCOnBoot=cdc,FlashSize=16M,PartitionScheme=custom,PSRAM=opi` | Verify build & warnings | Exited `0`, surfaced `-Wformat` (`uint32_t` vs `%u`) and `-Wvolatile` (`uartErrors++`) warnings |
| **Firmware Compilation (After Fixes)** | Same command after patching `doorbell_board.ino` & `features.h` | Verify zero warnings/errors | **Passed with 0 warnings** (`392,700 B` flash / `2%`, `33,728 B` global RAM / `10%`) |
| **Artifact & Data Integrity Audit** | Python check over all 8 `student1_esp32/feature_arrays/*.npz`, `dataset/doorbell_team1_esp32_features.*`, and `mission1_throughput.csv` | Shapes, `dtype`, finiteness (`NaN`/`Inf`), row counts, throughput math | **Passed** (`(144, 49, 40)` / `(7199, 40)` / `(7056, 40)`, 100% finite, max CSV throughput calc diff `0.0049 B/s`) |
| **JSON Schema Validation** | `json.loads()` across every `.json` file in repo | Syntax & parse validity | **Passed** (`ALL JSON VALID`) |
| **Python & Mock Serial Suite** | `py -m pytest -v` | Codec, framing/CRC, `MockBoard`, reference log-mel, Flask API | **Passed (`9/9` in `2.76s`)** |

---

## 3. Passed Tests

- **Firmware build (`--warnings all`):** Clean exit `0`, **0 compiler warnings**, `392,700 B` program storage (`2%` of 16 MB), `33,728 B` global variables (`10%` of 320 KB DRAM).
- **All 8 ESP32 `.npz` feature files:** Valid `float32`, 0 `NaN`/0 `Inf`, exact shapes (`(144, 49, 40)` clip-aligned and `(7199, 40)` raw stream).
- **Labelled dataset (`doorbell_team1_esp32_features.npz` & `.csv`):** `7,056` rows across all `144` unique clips (`44` CSV columns), 100% finite.
- **Mission 1 throughput CSV arithmetic (`75` rows):** Recomputed `bytes_sent / (board_ms / 1000)` matches `throughput_board_bps` within `0.0049 B/s`.
- **All JSON configs & logs:** 100% valid JSON.
- **Python unit & mock tests:** `9/9` passing.

---

## 4. Failed Tests

- None of the runnable build, data-integrity, JSON, or Python tests failed.
- **Prior Evidence Anomaly Noted:** `student1_esp32/logs/mission4_skip_after_fix.json` still contains `"expected_last_first_sample": 159520, "tail_shift_samples": -160` because `mission4_packet_loss_test.py` was patched to `159360` *after* that log file was saved (the recorded `last_5_first_samples` ending at `159360` is actually `0`-sample shift).

---

## 5. Bugs Discovered

1. **Internal SRAM leak + missing null-pointer checks in `runStream()` (`doorbell_board.ino`):** `fbuf` and `fout` were `malloc`'d before validating `store`/`max`/`psram`, were not checked for `NULL`, were allocated even when `feat=0`, and were **not freed** on early `ERR` exits (`ERR store needs max`, `ERR store must be none...`, `ERR no psram`, `ERR alloc ...`). Each failed `STREAM` leaked `~2,080 B` of internal SRAM (visible in `mission2_probe_baseline.json`: `largest` shrank `159,732 -> 155,636 -> 151,540`).
2. **`uint32_t` underflow in `finishStream()` (`doorbell_board.ino`):** `uint32_t secs_ms = st.tLast - st.t0;` could underflow to `~4.29e9 ms` if bytes arrived (`st.t0 = millis()`) but zero valid frames passed CRC (`st.framesOk == 0`, `st.tLast == 0`) before the 3-second timeout.
3. **Silent byte drop on misaligned `'D'` payload (`doorbell_board.ino`):** `len / fmtBytes` silently ignored remainder bytes if `len % fmtBytes != 0` while `storeBuf` copied all `len` bytes, desyncing `storeLen` vs `st.samples * fmtBytes`.
4. **Compiler warnings (`-Wformat=` and `-Wvolatile`):** `snprintf` passed `uint32_t` (`unsigned long` on Xtensa GCC) to `%u`, and `uartErrors++` triggered C++20 `-Wvolatile`.
5. **Missing sample-rate lower bound in `FeaturePipeline::begin()` (`features.h`):** `c.fs <= 40` was unchecked while `fmin = 20.0 Hz`, allowing inverted mel bounds (`fs <= 40`) or `log10(<=0)` for negative `fs`.
6. **Stale documentation in `shared/communication_protocol.json`:** Still listed `"SAVE": "-> TODO in Mission 2 (currently returns ERR SAVE not written yet)"` even though `cmdSave()` is implemented and verified.
7. **Command line buffer margin (`doorbell_board.ino`):** `readLine()` used `160`-byte buffers (tight for long `STREAM` commands with high-precision floats).

---

## 6. Bugs Fixed

| File | Fix Applied | Verification |
|---|---|---|
| [doorbell_board.ino](file:///c:/Users/dhanu/OneDrive/Desktop/EDGE%20AI2/Smart-Doorbell/student1_esp32/firmware/doorbell_board/doorbell_board.ino) | Added `freeStreamBufs()`, `NULL` check on `fbuf`/`fout`, free mel tables when `feat=0`, and call `freeStreamBufs()` on all early `ERR` exits | Compiled with `0` warnings |
| [doorbell_board.ino](file:///c:/Users/dhanu/OneDrive/Desktop/EDGE%20AI2/Smart-Doorbell/student1_esp32/firmware/doorbell_board/doorbell_board.ino) | Guarded `secs_ms = (st.framesOk > 0 && st.tLast >= st.t0) ? (st.tLast - st.t0) : 0;` against `uint32_t` underflow | Compiled with `0` warnings |
| [doorbell_board.ino](file:///c:/Users/dhanu/OneDrive/Desktop/EDGE%20AI2/Smart-Doorbell/student1_esp32/firmware/doorbell_board/doorbell_board.ino) | Added `if (len % fmtBytes != 0) { st.badLen++; continue; }` and expanded `readLine` buffers from `160` to `256` bytes | Compiled with `0` warnings |
| [doorbell_board.ino](file:///c:/Users/dhanu/OneDrive/Desktop/EDGE%20AI2/Smart-Doorbell/student1_esp32/firmware/doorbell_board/doorbell_board.ino) | Fixed all `-Wformat=` casts (`(unsigned)`) and replaced `uartErrors++` with `uartErrors = uartErrors + 1;` | `--warnings all` exited `0` with **0 warnings** |
| [features.h](file:///c:/Users/dhanu/OneDrive/Desktop/EDGE%20AI2/Smart-Doorbell/student1_esp32/firmware/doorbell_board/features.h) | Added `c.fs <= 40` check in `FeaturePipeline::begin()` | Compiled with `0` warnings |
| [communication_protocol.json](file:///c:/Users/dhanu/OneDrive/Desktop/EDGE%20AI2/Smart-Doorbell/shared/communication_protocol.json) | Updated `SAVE` status and firmware `source_of_truth` to match verified Stage A firmware | `ALL JSON VALID` |

---

## 7. Tests Not Performed (Hardware Disconnected)

Because no physical ESP32-S3 is connected during this review (`board_link.py ports` returned only Bluetooth virtual COM ports), physical tests could **not** be re-executed and are marked **NOT RE-TESTED**:

- **NOT RE-TESTED (on patched firmware):** Flashing today's bug-fixed `doorbell_board.ino` / `features.h` to the physical ESP32-S3 and running a post-fix smoke test (`PING`, `INFO`, `ERR alloc` non-leak check, `SAVE`, `DUMP flash`).
- **NOT RE-TESTED:** Mission 1 throughput & baud-rate benchmark (`COM12` @ `115.2k / 921.6k / 2M`, `COM11` USB CDC, packet sizes `8..1024`) — previously executed on 2026-11-26 (`mission1_throughput.csv`, 75 runs).
- **NOT RE-TESTED:** Mission 2 SRAM probe, 144-clip PSRAM + LittleFS `SAVE`, and physical unplug/replug `dump("flash")` — previously executed on 2026-11-26 (`mission2_save144_opi_16m.json`, `mission2_verify_opi_16m.json`).
- **NOT RE-TESTED:** Mission 3 real-time `compute_us` & speed sweep — previously executed on 2026-11-26 (`mission3_optimized_results.json`).
- **NOT RE-TESTED:** Mission 4 `skip=(10, 11, 200)`, `COM12` speed ramp, and full 144-clip extraction — previously executed on 2026-11-26 (`mission4_skip_after_fix.json`, `mission4_com_speed_ramp.json`, `phase5_144clips_all_runs.json`).

---

## 8. Hardware Limitations (Observed & Verified in Logs)

1. **Native USB CDC (`COM11`) RX overflow under unthrottled bursts:** With a `32,768 B` RX buffer and no hardware flow control, `speed=0` bursts `>= 64 KB` or `speed >= 8×` (`>= 256 KB/s`) drop/corrupt frames (`bad_crc = 13..80`, `seq_gaps = 26..170`). Safe zero-loss ceiling is **`<= 6×` (`192 KB/s`)** on `5 s` bursts and **`1×–4×`** for sustained 144-clip streams.
2. **UART bridge (`COM12`) baud ceiling:** `115,200` baud (`11,377 B/s`) fails real-time for all `16 kHz` modes and `8 kHz i16`. `921,600` baud (`90,909 B/s`) keeps up to `2.5×` without lag; `2,000,000` baud (`194,727 B/s`) keeps up to `6.0×` without dropping bytes (TX backpressure caps rate instead of overflowing RX).
3. **Internal SRAM limit:** Max contiguous internal SRAM allocation measured was `142,070 B` (`4.44 s` of `16 kHz i16`), far below the `4,608,000 B` required for 144 clips — **8 MB OPI PSRAM** (`PSRAM=opi`) is mandatory.
4. **PSRAM volatility & Flash partition defaults:** PSRAM loses all contents on power cut (`n=0` after unplug/replug). Default 4 MB (`1.44 MB` LittleFS) and default 16 MB (`3.38 MB` SPIFFS) Arduino partition schemes are too small; custom `partitions.csv` (`6.88 MiB` LittleFS) is required for `/rec.bin` (`4.61 MB`, `SAVE` takes `10.56 s`–`34.32 s`).
5. **HWCDC TX buffer sizing:** `Serial.setTxBufferSize(32768)` + `256`-byte TX chunk pacing in `writeAll()` is required so `DUMP flash` transfers all `4,608,000` bytes without dropping tail packets during Flash SPI reads.

---

## 9. Remaining Issues

1. **Reflash Required Before Live Demo:** The Stage A bug fixes in `doorbell_board.ino` and `features.h` compile with zero warnings, but have **not yet been uploaded** to the physical board since no board was attached today. Student 1 should upload the updated `doorbell_board` sketch and run a quick `PING` / `INFO` / `skip=(10, 11, 200)` / `SAVE` + `CRC flash` check before the live demo.
2. **Stale Summary Fields in `mission4_skip_after_fix.json`:** Lines 50–51 still show `"expected_last_first_sample": 159520, "tail_shift_samples": -160` from before `mission4_packet_loss_test.py` line 67 was corrected to `159360`. Re-running `mission4_packet_loss_test.py --port <PORT> --tag after_fix` once the board is connected will refresh that JSON with `"tail_shift_samples": 0`.
3. **Hardcoded Firmware Constants (Acceptable for Stage B, Noted for Clarity):** `REC_PATH = "/rec.bin"`, `MAX_PAYLOAD = 4096`, `UART_BAUD_DEFAULT = 921600`, and `mel fmin = 20.0 Hz` are compile-time constants matching `shared/communication_protocol.json` and `shared/logmel_config.json`.

---

## 10. Readiness for Stage B Integration

**Status: READY FOR STAGE B (Students 3 & 4 Unblocked)**

- Every Stage B input required by **Student 4** (all 4 aligned 144-clip ESP32 `.npz` arrays, `7,056`-frame labelled dataset, `mission1`–`mission4` packet/loss logs, `data_card.md`) and **Student 3** (`shared/*.json`, `frontend_api_contract.json`, `student2_python/api/server.py`, benchmark CSV/PNGs) is complete, validated, finite, and verified on disk.
- No Stage B task requires physical board access.

---

## Verified Hardware Output Files Inventory

| Category | Verified Repo-Relative Path | Details |
|---|---|---|
| **Firmware** | `student1_esp32/firmware/doorbell_board/doorbell_board.ino` | Stage A reviewed & patched (0 compiler warnings) |
| **Firmware DSP** | `student1_esp32/firmware/doorbell_board/features.h` | Radix-2 FFT + sparse HTK mel (`fs > 40` check added) |
| **Partition Table** | `student1_esp32/firmware/doorbell_board/partitions.csv` | `4.5 MB` APP ×2 + `6.88 MiB` LittleFS |
| **Starter Baseline** | `student1_esp32/firmware/doorbell_board_starter/` | Untouched starter reference (`.ino` + `features.h`) |
| **Shared Configs** | `shared/hardware_config.json`, `shared/communication_protocol.json`, `shared/audio_config.json`, `shared/logmel_config.json`, `shared/frontend_api_contract.json` | Valid JSON, updated protocol spec |
| **Benchmarks & Plots** | `student1_esp32/benchmarks/mission1_throughput.csv`, `mission1_speed_vs_baud.png`, `mission1_packet_size.png` | `75` verified COM12/COM11 runs (`max calc err 0.0049 B/s`) |
| **Hardware Logs** | `student1_esp32/logs/phase1_port_test.json`, `mission1_pipe_results.json`, `mission2_probe_baseline.json`, `mission2_save144_opi_16m.json`, `mission2_verify_opi_16m.json`, `mission3_starter_10s.json`, `mission3_optimized_results.json`, `mission4_skip_before_fix.json`, `mission4_skip_after_fix.json`, `mission4_com_speed_ramp.json`, `phase5_144clips_all_runs.json` | All 11 JSON logs valid |
| **ESP32 Feature Arrays** | `student1_esp32/feature_arrays/esp32_clips_{16k_i16_S1.0_speed1,16k_i8_S1.0,16k_i8_S0.25,8k_i16_S1.0_noaa}.npz` + `esp32_raw_*.npz` | 8 `.npz` files, all `float32`, 100% finite |
| **Clean Dataset** | `dataset/doorbell_team1_esp32_features.npz`, `dataset/doorbell_team1_esp32_features.csv`, `dataset/data_card.md` | `7,056` clean frames across `144` clips (`1,176`/class) |
| **Docs** | `student1_esp32/README.md`, `student1_esp32/documentation/{setup_and_phase1,mission1_predictions_and_llm_log,phase2_com12_report,mission1_complete_report,mission2_complete_report,mission3_complete_report,phase5_final_handover_report}.md` | Complete Mission 1–4 + Phase 5 docs |

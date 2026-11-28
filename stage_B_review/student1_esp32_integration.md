# Student 1 Integration Review — ESP32-S3 Firmware & Hardware

**Component:** `student1_esp32/` · **Target Board:** `ESP32-S3-DevKitC-1 N16R8` (`MAC a4:cb:8f:d4:74:98`)  
**Stage B Status:** **PASS** *(Physical `COM11` verified live; `COM12` UART bridge `NOT TESTED – HARDWARE REQUIRED` in Stage B)*

---

## 1. Board Setup, Compilation & Live Upload Verification

- **FQBN Compiled:** `esp32:esp32:esp32s3:CDCOnBoot=cdc,FlashSize=16M,PartitionScheme=custom,PSRAM=opi` (`partitions.csv`: `4.5 MB` APP ×2 + `6.88 MiB` LittleFS).
- **Stage B Build (`arduino-cli --warnings all`):**
  - Exited with code `0` (`0` compiler warnings).
  - Program storage: **`392,700 B`** (2% of 16 MB).
  - Global dynamic memory: **`33,728 B`** (10% of 320 KB DRAM), leaving `293,952 B`.
- **Stage B Live Upload (`COM11`):** Flashed cleanly via `esptool v5.3.1` at `921,600` baud (`234,409 B` compressed in `2.5 s`, hash verified, hard reset via RTS).

---

## 2. Serial Port Identification & Post-Flash State

- **`arduino-cli board list` / `board_link.py ports`:** Detected live **`COM11`** (`USB Serial Device`, `ESP32 Family Device`). `COM12` WCH UART bridge was not connected during Stage B.
- **Post-Flash `PING` / `INFO` (`COM11`):**
  - `PING` → `True` (`PONG`)
  - `INFO` → `cpu_mhz=240`, `heap_free=295828`, `heap_largest=241652`, `psram_size=8388608`, `psram_free=8317200`, `psram_largest=8257524`, `flash_chip=16777216`, `fs_total=7208960`, `fs_used=4628480`.

---

## 3. Protocol Compatibility, Buffering, Error Handling & Persistent Storage

- **Framing (`doorbell_board.ino` lines 56–61, 182–230):** Uses little-endian `0xA5 0x5A | type(1B) | seq(u32) | len(u16) | payload | crc32(u32)` uplink and `0xB5 0x5B` downlink (`MAX_PAYLOAD=4096`), `Serial.setRxBufferSize(32768)`, `Serial.setTxBufferSize(32768)`, and `writeAll()` 256-byte chunk pacing for reliable multi-MB dumps.
- **Gap Alignment Fix (`doorbell_board.ino` lines 200–223):** Detects gaps from `seq=0` (`st.lastSeq < 0 && seq > 0`) as well as mid-stream (`seq != st.lastSeq + 1`), inserts zero bytes into `storeBuf`, increments `st.samples`, resets `fcount`, and realigns `skipToHop` to next hop boundary.
  - **Stage B Live Verification (`skip=(0, 10, 11, 200)` across 6 clips = 96,000 samples):** Reported `packets_sent=296`, `seq_gaps=4`, `samples=96000`, `features=293`, `first_sample` head `[320, 640, 960, 1280]`, tail **`95360 == expected_last_first_sample`**.
- **Duplicate & Corrupted Frame Rejection (`doorbell_board.ino` lines 197–198):**
  - **Stage B Live Verification (dup `seq=0` + corrupted CRC `seq=1` + valid `seq=2` + `E`):** Returned `why=end frames_ok=3 bad_crc=1 bad_len=0 seq_gaps=1 dup=1 samples=960`.
- **Memory Tiers & Power-Cut Persistence:**
  - **PSRAM:** Live 6-clip stream (`192,000 B`) matched host `CRC-32` (`psram_crc_match=true`) and exact raw dump (`psram_dump_exact_bytes=true`).
  - **LittleFS `/rec.bin` Persistence:** Verified `CRC flash` both **before** and **after** re-flashing Stage B firmware: `n=4,608,000 B`, **`crc=0x55c3d431` (`1438897201`)** survived unplug/replug AND firmware upload intact. (`SAVE` command was not re-executed in Stage B so the 4.608 MB `/rec.bin` file stays intact on flash.)

---

## 4. ESP32 Log-Mel Implementation (`features.h`)

- Verified line-by-line against `shared/logmel_config.json` and `student2_python/logmel/reference_logmel.py`:
  - Symmetric Hann (`0.5f - 0.5f * cosf(2*pi*n/(win-1))`, matches `np.hanning(win)`).
  - Precomputed bit-reversal and twiddle LUTs + Cooley-Tukey iterative radix-2 FFT (`fftRadix2()`).
  - Unnormalized power `(|re|^2 + |im|^2) / nfft`.
  - HTK mel triangles `20 Hz .. fs/2` using sparse bin bounds `[melStart[m], melEnd[m])` and `10*log10f(max(s, 1e-10f))`.
  - **Live Timing & Parity (`COM11`, 6 clips @ `speed=1.0`):** `compute_us_mean = 683.75 us` (`max = 742 us`, 3.4% of `20,000 us` hop), **`MAE = 1.67e-06 dB`**, `max |diff| = 6.866e-05 dB` vs live Python `reference_logmel.py` (`f32` `MAE=1.59e-06 dB`; `i8 S=0.25` `MAE=1.37e-06 dB`).

---

## 5. Tests Not Performed in Stage B (`HARDWARE REQUIRED`)

- `COM12` WCH UART bridge baud tests (`BAUD 115200 / 921600 / 2000000`) and `COM12` speed-ramp lag curve (`mission4_com_speed_ramp.json`): **NOT TESTED in Stage B** (`COM12` USB-UART adapter was not connected; Stage A logs verified intact).

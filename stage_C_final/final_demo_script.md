# Final Live Demonstration Script — Smart Doorbell Edge AI (`Team 1 Paradise`)

**Target Time:** ~5 Minutes · **Directory:** `Smart-Doorbell\`  
**Prerequisites:** Connected `ESP32-S3-DevKitC-1 N16R8` on `COM11` (USB CDC), sibling `..\edge_ai_assignment2\speech_pool.npz`, Python 3 + Node.js installed.

---

## Part 1 — Introduction (~30 s)
- **Problem:** Always-on acoustic keyword spotting ("The Doorbell's Ears": `on`, `off`, `stop`, `go`, `_unknown`, `_silence`) requires low-latency on-device DSP, zero-loss framing under high-rate streaming, anti-aliased sampling (`7,348 Hz` room whine hazard), and exact parity with Python ML baselines.
- **Project Objectives:** Benchmark USB CDC (`COM11`) vs UART (`COM12`), optimize SRAM/PSRAM/LittleFS flash persistence (`4.608 MB`), speed up on-device 40-band HTK log-mel extraction within `<= 0.05 dB` of NumPy, validate dataset/packet alignment (`144` clips), train a leakage-free classifier, and visualize all real measurements cleanly in a dashboard.

---

## Part 2 — Architecture Overview (~45 s)
- Walk through the 4 subsystems:
  1. **ESP32-S3 Hardware (Student 1):** Dual-core LX7 @ `240 MHz`, `8 MB` OPI PSRAM, `6.88 MiB` LittleFS flash, custom `doorbell_board.ino` + radix-2 `features.h`.
  2. **Python Audio & API Backend (Student 2):** Pure-NumPy codec (`f32`/`i16`/`i8`), `0xA5 0x5A` / `0xB5 0x5B` CRC-32 framing, pure-NumPy HTK log-mel baseline, Flask API on `:5000`.
  3. **Validation & ML (Student 4):** Dataset/packet audit (`7,056` clean frames), per-band/class error heatmaps, clip-split Nearest-Centroid classifier.
  4. **Dashboard (Student 3):** React 19 + Vite `/repo/*` + `/api/*` 10-page dashboard.

---

## Part 3 — Live Hardware Demonstration (`COM11`, ~90 s)
Verify ESP32 port, check persistent flash `/rec.bin` (`CRC 0x55c3d431`), and run live 1-clip real-time `16 kHz i16` feature extraction + parity check:
```powershell
cd "c:\Users\dhanu\OneDrive\Desktop\EDGE AI2\Smart-Doorbell"
py starter_files\board_link.py --port COM11 info
py -c "import sys; sys.path.insert(0, 'starter_files'); from board_link import Board; b=Board('COM11'); print(b.crc('flash')); b.close()"
py -c "import sys, numpy as np; sys.path.insert(0,'.'); sys.path.insert(0,'../edge_ai_assignment2'); import team_audio as ta; from board_link import Board; from student2_python.preprocessing.audio_codec import pack, unpack; from student2_python.logmel.reference_logmel import features; x=ta.get_clip(1,0,fs=16000,antialias=True); p=pack(x,'i16',1.0); b=Board('COM11'); r=b.stream(p,16000,'i16',1.0,480,320,512,40,0,True,'psram',len(p),1.0,320); print('PSRAM CRC:', hex(b.crc('psram')['crc'])); b.free(); b.close(); pq,_=features(unpack(p,'i16',1.0),16000,480,320,512,40,0); print('Frames:', r['features'].shape, 'Compute us mean:', round(r['compute_us'].mean(),2), 'MAE dB:', round(float(np.abs(r['features']-pq).mean()),6))"
```
- **Talking Points:** Point out `CRC flash` `0x55c3d431` (`4,608,000 B` survived power cuts), `0` lost features, `~684 us/frame` (`3.4%` CPU load vs `20 ms` hop), and `~0.000002 dB` MAE vs Python.

---

## Part 4 — Software & ML Pipeline Demonstration (~45 s)
Run the automated test suite and Student 4 comparison/classifier outputs:
```powershell
py -m pytest -v student2_python/tests student4_validation/tests
py -m student4_validation.src.validate_dataset_and_packets
py -m student4_validation.src.compare_features
py -m student4_validation.src.nearest_centroid_eval
```
- **Talking Points:** Highlight `18 passed`, `7,056` clean frames (`143` straddling excluded), `16k i16` matching Laptop `f32` at **`75.00%`**, and `8k No-AA` collapsing to **`25.00%`** (`8.05 dB` MAE) due to `7,348 Hz → 652 Hz` aliasing.

---

## Part 5 — Live Frontend Dashboard Walkthrough (~60 s)
Start Flask backend and Vite frontend in two terminals:
```powershell
# Terminal 1 (from Smart-Doorbell\)
py student2_python/api/server.py --port 5000

# Terminal 2 (from Smart-Doorbell\student3_frontend\)
npm run dev -- --port 5173
```
Open `http://127.0.0.1:5173` in Chrome and step through:
1. **Overview & Architecture:** `144/144` clips, `685 us` latency, `0` lost packets, `0xA5 0x5A` pipeline SVG.
2. **Audio Input & Log-Mel:** Toggle Clip `#0 (on)` and `#120 (_silence)` with `8 kHz` + `Antialias` (`live_api` badge).
3. **Communication & Packet Integrity:** Show `COM11` vs `COM12` throughput and `skip=(10, 11, 200)` zero-fill fix (`159,360` alignment).
4. **Hardware Performance, Comparison & ML Evaluation:** Show `74.21 dB` SQNR, `0.003914 dB` (`16k i16`) vs `8.0510 dB` (`8k No-AA`), and the `6 × 6` Nearest-Centroid confusion matrix.

---

## Part 6 — Results & Conclusion (~30 s)
Summarize shipping config (`16 kHz antialias=True i16 S=1.0`), `2,725×` FFT speedup, power-cut-persistent `4.608 MB` LittleFS capture, synthetic audio / Nearest-Centroid limitations, and on-device TinyML next steps.

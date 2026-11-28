# Limitations & Future Work

---

## 1. Technical & Experimental Limitations

1. **Synthesized Serial Audio vs Physical Live Microphone:**
   - All 144 clips originate from `starter_files/team_audio.py` (`speech_pool.npz`) mixed with simulated Team 1 room acoustics (`7,347.98 Hz` regulator whine, `100.0 Hz` hum, Gaussian noise) and streamed over USB CDC / UART — not captured from a live I2S/PDM MEMS microphone under variable real-world reverberation or outdoor noise.
2. **USB CDC Pipe Ceiling (`COM11`):**
   - Native USB CDC overflows the ESP32-S3's `32,768 B` RX buffer at **`>= 256 KB/s`** (`8×` real-time `16 kHz i16` or `4×` `16 kHz f32`, verified live during Stage B/C). Real-time streaming (`32 KB/s` `i16`, `64 KB/s` `f32`) works with zero packet loss.
3. **Default Board Menu Trap (`PSRAM` Disabled / Small `LittleFS`):**
   - Stock Arduino IDE ESP32-S3 defaults set `PSRAM=disabled` (`0 B`) and limit storage (`1.44 MB`), preventing 144-clip buffering (`4.608 MB`). Custom `partitions.csv` (`6.88 MiB` LittleFS) + `PSRAM=opi` + `FlashSize=16M` are mandatory.
4. **Simple Baseline Classifier & Dataset Size:**
   - The `80`-dim `[mean, std]` Nearest-Centroid model (`96` train / `48` test clips, `75.00%` accuracy) discards fine sub-word temporal transitions, leading to expected confusion between short commands such as `go` and `on`.
5. **Runtime Server Coupling for Static Previews:**
   - Standalone opening of `dist/index.html` without Vite dev/preview middleware cannot fetch `/repo/student4_validation/outputs/*.json`; full dashboard metrics require Vite (`npm run dev` or `npm run preview`) plus Flask (`server.py --port 5000`).

---

## 2. Future Engineering Improvements

1. **On-Device Keyword Spotting (TinyML / TFLite Micro):** Deploy a compact DS-CNN or 1D-CNN in INT8 directly on ESP32-S3 using PSRAM + ESP-NN SIMD kernels instead of streaming raw frames back to Python.
2. **Live I2S Microphone Front-End + Wake-Word Trigger:** Attach an INMP441 I2S MEMS microphone with DMA ring-buffering and voice-activity detection (VAD) so LittleFS `/rec.bin` stores triggered utterances autonomously.
3. **DMA-Safe Double Buffering over USB/Wi-Fi:** Move serial RX parsing (`runStream()`) onto Core 0 via FreeRTOS task queues to sustain higher burst speeds above `256 KB/s` or stream asynchronously over ESP32-S3 Wi-Fi.
4. **Embedded Frontend Bundling into Flask:** Optionally serve Student 4 JSONs/PNGs and `student3_frontend/dist/` directly from `server.py` so a single Python command launches the entire dashboard offline.
5. **Temporal Sequence Modelling:** Replace global `[mean, std]` pooling with temporal deltas or small convolutional architectures trained on multi-speaker real recordings with SpecAugment.

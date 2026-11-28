# Final Engineering Methodology — Smart Doorbell Edge AI

**Course:** AI255TBD Edge AI Module 2 (*"The Doorbell's Ears"*) · **Team:** 1 (`Paradise`)

---

## 1. Deterministic Dataset Generation & Team Acoustics

144 one-second clips (`24` clips × `6` classes: `on`, `off`, `stop`, `go`, `_unknown`, `_silence`) are synthesized via `starter_files/team_audio.py` using multi-voice word recordings from `speech_pool.npz` mixed with Team 1's simulated room acoustics (`7,347.98 Hz` regulator whine at `0.0505` amp, `100.0 Hz` mains hum, and `0.007695` Gaussian background noise). Downsampling from `48 kHz` uses a 255-tap Blackman low-pass filter (`antialias=True`) to eliminate high-frequency aliasing.

---

## 2. Quantisation & Codec Strategy

Samples $x \in [-1, 1]$ are quantised with scale $S$ and bit depth $b \in \{16, 8\}$ (or passed verbatim as `<f4`):
$$q = \text{clip}\left(\left\lfloor \frac{x}{S}(2^{b-1}-1) \right\rceil,\; -2^{b-1},\; 2^{b-1}-1\right), \qquad \hat{x} = \frac{q \cdot S}{2^{b-1}-1}$$
Shipping configuration is **`fs=16000 Hz`, `antialias=True`, `fmt=i16`, `scale=1.0`** because dataset peak amplitude is `0.67562 < 1.0` (`0%` clipping), achieving `74.21 dB` mean SQNR across all 144 clips at `32,000 B/s` (`4,608,000 B` total).

---

## 3. Reliable Binary Serial Framing & Gap Recovery

Frames wrap up to `4,096 B` of sample payload in `[0xA5 0x5A | type(1B) | seq(u32 LE) | len(u16 LE) | payload | crc32(u32 LE)]`.  
On packet loss (`seq != lastSeq + 1`, or `lastSeq < 0 && seq > 0`), `doorbell_board.ino`:
1. Computes lost sample count `gapPkts * pktSamples`,
2. Advances `st.samples` and inserts zero bytes into `storeBuf`,
3. Resets `fcount = 0` and aligns `skipToHop` to the next `hop` boundary so every emitted `'F'` frame carries an unshifted global sample timestamp (`first_sample`).

---

## 4. Matched Pure-NumPy & Fixed Radix-2 FFT Log-Mel Recipe

To guarantee bit-compatible DSP parity between Python and ESP32-S3 (`<= 0.05 dB` spec):
1. Frame `win=480` samples at `hop=320` samples (`49` frames/clip).
2. Multiply by **symmetric** Hann window (`np.hanning(win)` / `0.5 - 0.5*cos(2*pi*n/(win-1))`).
3. Zero-pad to `nfft=512` and compute `512`-point FFT (Cooley-Tukey iterative radix-2 DIT with precomputed bit-reversal and twiddle LUTs in `features.h`).
4. Compute unnormalized power spectrum $P[k] = (\text{Re}[k]^2 + \text{Im}[k]^2) / N_{\text{FFT}}$ for $k=0\dots 256$.
5. Apply `40` HTK triangular mel filters ($m(f) = 2595\log_{10}(1 + f/700)$) from `20 Hz` to `fs/2` using sparse non-zero bin bounds `[melStart[m], melEnd[m])`.
6. Convert power to dB: $10\log_{10}(\max(E_m, 10^{-10}))$ without mean/variance normalization.

---

## 5. Inter-Clip Boundary Filtering & Leakage-Free ML Evaluation

Streaming all 144 clips continuously yields `7,199` frames, of which `143` cross clip boundaries (`first_sample // fs != (first_sample + win - 1) // fs`). Those `143` straddling frames are excluded, leaving **`7,056`** clean frames (`49/clip`, `1,176/class`).  
For classification, frames from each clip $i$ are aggregated into an `80`-dim embedding $[\mu_{40}(i), \sigma_{40}(i)]$, split **by `clip_id`** into **`96` train (`16`/class)** and **`48` test (`8`/class)** (`seed=42`), standardized using training statistics only, and evaluated with a Nearest-Centroid classifier.

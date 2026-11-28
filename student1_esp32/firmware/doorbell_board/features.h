// features.h -- Optimized ESP32-S3 Feature Pipeline (Mission 3)
// Exact match to Module 2 Section 5 recipe:
//   frame -> Hann (symmetric, numpy.hanning) -> zero-pad to nfft -> |FFT|^2 / nfft
//   -> HTK mel triangles, 20 Hz .. fs/2 -> 10*log10(max(m,1e-10)) -> optional DCT-II (ortho)
//
// Optimization (Mission 3):
//   Replaced O(N^2) textbook DFT (which called cosf/sinf 246,720 times/frame)
//   with an iterative Cooley-Tukey radix-2 DIT FFT using precomputed bit-reversal
//   and twiddle-factor tables in begin(), plus sparse [melStart..melEnd) bounds
//   for the mel triangle dot products. Zero trig calls or allocations in compute().
#pragma once
#include <math.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>

struct FeatCfg {
  int fs = 16000, win = 480, hop = 320, nfft = 512, mels = 40, mfcc = 0;
};

class FeaturePipeline {
 public:
  FeatCfg c;
  bool ok = false;

  bool begin(const FeatCfg &cfg) {
    end();
    c = cfg;
    if (c.fs <= 40 || c.nfft < 16 || c.nfft > 2048 || (c.nfft & (c.nfft - 1)) || c.win > c.nfft || c.win < 2 ||
        c.hop < 1 || c.mels < 1 || c.mels > 128 || c.mfcc < 0 || c.mfcc > c.mels) return false;
    nb = c.nfft / 2 + 1;
    log2n = 0;
    for (int t = c.nfft; t > 1; t >>= 1) log2n++;

    window = alloc(c.win);
    re = alloc(c.nfft);
    im = alloc(c.nfft);
    pw = alloc(nb);
    melw = alloc((size_t)c.mels * nb);
    melv = alloc(c.mels);
    twRe = alloc(c.nfft / 2);
    twIm = alloc(c.nfft / 2);
    bitrev = (uint16_t *)malloc(sizeof(uint16_t) * c.nfft);
    melStart = (uint16_t *)malloc(sizeof(uint16_t) * c.mels);
    melEnd = (uint16_t *)malloc(sizeof(uint16_t) * c.mels);
    if (c.mfcc) dct = alloc((size_t)c.mfcc * c.mels);

    if (!window || !re || !im || !pw || !melw || !melv || !twRe || !twIm ||
        !bitrev || !melStart || !melEnd || (c.mfcc && !dct)) {
      end();
      return false;
    }

    // Symmetric Hann window (matches np.hanning(win))
    for (int n = 0; n < c.win; n++) {
      window[n] = 0.5f - 0.5f * cosf(2.0f * (float)M_PI * n / (c.win - 1));
    }

    // Precompute bit-reversal indices and radix-2 FFT twiddle factors: e^{-j 2*pi*k/nfft}
    for (int i = 0; i < c.nfft; i++) {
      uint16_t r = 0;
      for (int b = 0; b < log2n; b++) {
        if (i & (1 << b)) r |= (uint16_t)(1 << (log2n - 1 - b));
      }
      bitrev[i] = r;
    }
    for (int k = 0; k < c.nfft / 2; k++) {
      double a = 2.0 * M_PI * k / c.nfft;
      twRe[k] = (float)cos(a);
      twIm[k] = (float)(-sin(a));
    }

    // HTK mel filterbank + sparse bin range [melStart[m], melEnd[m])
    auto hz2mel = [](double f) { return 2595.0 * log10(1.0 + f / 700.0); };
    auto mel2hz = [](double m) { return 700.0 * (pow(10.0, m / 2595.0) - 1.0); };
    double m0 = hz2mel(20.0), m1 = hz2mel(c.fs / 2.0);
    double *edge = (double *)malloc(sizeof(double) * (c.mels + 2));
    if (!edge) { end(); return false; }
    for (int i = 0; i < c.mels + 2; i++) edge[i] = mel2hz(m0 + (m1 - m0) * i / (c.mels + 1));
    for (int m = 0; m < c.mels; m++) {
      uint16_t firstNz = (uint16_t)nb, lastNz = 0;
      for (int k = 0; k < nb; k++) {
        double f = (double)k * c.fs / c.nfft, lo = edge[m], ce = edge[m + 1], hi = edge[m + 2], w = 0;
        if (f > lo && f <= ce) w = (f - lo) / (ce - lo);
        else if (f > ce && f < hi) w = (hi - f) / (hi - ce);
        melw[(size_t)m * nb + k] = (float)w;
        if (w > 0.0) {
          if (k < firstNz) firstNz = (uint16_t)k;
          lastNz = (uint16_t)(k + 1);
        }
      }
      if (firstNz >= lastNz) { firstNz = 0; lastNz = 0; }
      melStart[m] = firstNz;
      melEnd[m] = lastNz;
    }
    free(edge);

    for (int q = 0; q < c.mfcc; q++)
      for (int m = 0; m < c.mels; m++)
        dct[(size_t)q * c.mels + m] = (float)((q == 0 ? sqrt(1.0 / c.mels) : sqrt(2.0 / c.mels)) *
                                              cos(M_PI * q * (2 * m + 1) / (2.0 * c.mels)));
    ok = true;
    return true;
  }

  int outSize() const { return c.mfcc ? c.mfcc : c.mels; }

  // frame: c.win float samples (already dequantised). out: outSize() floats.
  void compute(const float *frame, float *out) {
    // Load windowed + zero-padded input directly in bit-reversed order
    for (int i = 0; i < c.nfft; i++) {
      uint16_t src = bitrev[i];
      re[i] = (src < (uint16_t)c.win) ? (frame[src] * window[src]) : 0.0f;
      im[i] = 0.0f;
    }

    fftRadix2();

    const float invN = 1.0f / (float)c.nfft;
    for (int k = 0; k < nb; k++) {
      pw[k] = (re[k] * re[k] + im[k] * im[k]) * invN;
    }

    for (int m = 0; m < c.mels; m++) {
      const float *w = melw + (size_t)m * nb;
      const int k0 = melStart[m], k1 = melEnd[m];
      float s = 0.0f;
      for (int k = k0; k < k1; k++) s += w[k] * pw[k];
      melv[m] = 10.0f * log10f(s > 1e-10f ? s : 1e-10f);
    }

    if (!c.mfcc) { memcpy(out, melv, sizeof(float) * c.mels); return; }
    for (int q = 0; q < c.mfcc; q++) {
      const float *d = dct + (size_t)q * c.mels;
      float s = 0.0f;
      for (int m = 0; m < c.mels; m++) s += d[m] * melv[m];
      out[q] = s;
    }
  }

  void end() {
    float **ps[] = {&window, &re, &im, &pw, &melw, &melv, &dct, &twRe, &twIm};
    for (auto p : ps) { free(*p); *p = nullptr; }
    free(bitrev); bitrev = nullptr;
    free(melStart); melStart = nullptr;
    free(melEnd); melEnd = nullptr;
    ok = false;
  }
  ~FeaturePipeline() { end(); }

 private:
  int nb = 0, log2n = 0;
  float *window = nullptr, *re = nullptr, *im = nullptr, *pw = nullptr, *melw = nullptr,
        *melv = nullptr, *dct = nullptr, *twRe = nullptr, *twIm = nullptr;
  uint16_t *bitrev = nullptr, *melStart = nullptr, *melEnd = nullptr;

  static float *alloc(size_t n) { return (float *)malloc(sizeof(float) * n); }

  void fftRadix2() {
    const int N = c.nfft;
    for (int s = 0; s < log2n; s++) {
      const int half = 1 << s;
      const int step = N >> (s + 1);
      const int span = half << 1;
      for (int i = 0; i < N; i += span) {
        for (int k = 0; k < half; k++) {
          const int twIdx = k * step;
          const float wr = twRe[twIdx];
          const float wi = twIm[twIdx];
          const int idx1 = i + k;
          const int idx2 = idx1 + half;
          const float r2 = re[idx2];
          const float i2 = im[idx2];
          const float tr = wr * r2 - wi * i2;
          const float ti = wr * i2 + wi * r2;
          re[idx2] = re[idx1] - tr;
          im[idx2] = im[idx1] - ti;
          re[idx1] += tr;
          im[idx1] += ti;
        }
      }
    }
  }
};

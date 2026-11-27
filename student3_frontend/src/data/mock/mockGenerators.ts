import type {
  ClipDetailPayload,
  ManifestRow,
  Student4ClassifierResults,
  Student4FeatureComparison,
  Student4ValidationSummary,
} from '../../types/dashboard';

/**
 * Strictly separated MOCK / DEMO data generators.
 * Used ONLY when:
 *   1) Student 2's Flask /api/clips/<id> endpoint (or speech_pool.npz) is unavailable, or
 *   2) The user explicitly enables "Preview Mock Student 4 Outputs" before Student 4 merges.
 * Never blended silently with verified hardware measurements.
 */

function seededRandom(seed: number): () => number {
  let state = (seed + 1) * 2654435761;
  return () => {
    state = (state ^ (state << 13)) >>> 0;
    state = (state ^ (state >>> 17)) >>> 0;
    state = (state ^ (state << 5)) >>> 0;
    return (state >>> 0) / 4294967296;
  };
}

export function generateMockClipDetail(
  clipId: number,
  fs: number,
  antialias: boolean,
  manifestRow?: ManifestRow,
): ClipDetailPayload {
  const classes = ['on', 'off', 'stop', 'go', '_unknown', '_silence'];
  const label = manifestRow?.label ?? classes[Math.floor(clipId / 24) % classes.length];
  const peak = Number(manifestRow?.peak_abs ?? (label === '_silence' ? 0.036 : 0.48));
  const rand = seededRandom(clipId * 97 + fs + (antialias ? 1 : 0));

  // Generate downsampled preview waveform (max 1000 points for crisp rendering, or full length)
  const nSamples = fs;
  const waveform = new Array<number>(nSamples);
  const isSilence = label === '_silence';
  const wordCenter = 0.25 + (clipId % 5) * 0.08;
  const wordWidth = 0.14 + (clipId % 3) * 0.03;
  const baseFreq = 180 + (clipId % 7) * 55;

  for (let i = 0; i < nSamples; i++) {
    const t = i / fs;
    const hum = 0.008 * Math.sin(2 * Math.PI * 100 * t);
    const whineFreq = fs === 8000 && !antialias ? 652 : 7348;
    const whine = antialias && fs < 16000 ? 0 : 0.025 * Math.sin(2 * Math.PI * whineFreq * t);
    const noise = (rand() - 0.5) * 0.015;
    let speech = 0;
    if (!isSilence) {
      const env = Math.exp(-Math.pow((t - wordCenter) / wordWidth, 2));
      speech =
        peak *
        0.75 *
        env *
        (0.6 * Math.sin(2 * Math.PI * baseFreq * t) +
          0.3 * Math.sin(2 * Math.PI * (baseFreq * 2.15) * t) +
          0.2 * Math.sin(2 * Math.PI * (baseFreq * 3.4) * t));
    }
    waveform[i] = Math.max(-1, Math.min(1, speech + hum + whine + noise));
  }

  const hop = fs === 16000 ? 320 : Math.round(0.02 * fs);
  const frames = 49;
  const mels = 40;
  const firstSample = Array.from({ length: frames }, (_, idx) => idx * hop);

  const pythonLogmel: number[][] = [];
  const esp32Logmel: number[][] | null = fs === 16000 && antialias ? [] : null;

  for (let f = 0; f < frames; f++) {
    const t = (f * hop) / fs;
    const speechEnv = isSilence ? 0 : Math.exp(-Math.pow((t - wordCenter) / wordWidth, 2));
    const pyRow: number[] = [];
    const espRow: number[] = [];
    for (let m = 0; m < mels; m++) {
      const formant1 = Math.exp(-Math.pow((m - (6 + (clipId % 6))) / 4.2, 2));
      const formant2 = Math.exp(-Math.pow((m - (16 + (clipId % 8))) / 5.5, 2));
      const whineBand = m >= 36 && (!antialias || fs >= 16000) ? 16 : 0;
      const humBand = m <= 2 ? 10 : 0;
      const speechEnergy = speechEnv * (32 * formant1 + 24 * formant2);
      const val = -48 + speechEnergy + whineBand + humBand + (rand() - 0.5) * 2.2;
      const clamped = Number(val.toFixed(4));
      pyRow.push(clamped);
      if (espRow && esp32Logmel) {
        espRow.push(Number((clamped + (rand() - 0.5) * 0.008).toFixed(4)));
      }
    }
    pythonLogmel.push(pyRow);
    if (esp32Logmel) {
      esp32Logmel.push(espRow);
    }
  }

  return {
    clip_id: clipId,
    label,
    fs,
    antialias,
    waveform,
    first_sample: firstSample,
    python_logmel: pythonLogmel,
    esp32_logmel: esp32Logmel,
    esp32_source: esp32Logmel ? 'mock_simulated_preview' : null,
    origin: 'mock',
    note: 'Simulated waveform & log-mel spectrogram (Flask API or speech_pool.npz offline).',
  };
}

export const MOCK_STUDENT4_VALIDATION_SUMMARY: Student4ValidationSummary = {
  dataset: {
    total_clips: 144,
    valid_clips: 144,
    clean_frames: 7056,
    excluded_straddling_frames: 143,
    frames_per_class: 1176,
  },
  controlled_skip_test: {
    skip_packets: [10, 11, 200],
    before_fix_tail_shift_samples: -1120,
    after_fix_tail_shift_samples: 0,
  },
  port_limits: {
    usb_com11_max_zero_loss_speed: 6.0,
    com12_921600_max_lag_free_speed: 2.5,
    com12_2000000_max_lag_free_speed: 6.0,
  },
};

export const MOCK_STUDENT4_FEATURE_COMPARISON: Student4FeatureComparison = {
  '16k_i16_S1.0_speed1': {
    mae_db: 0.003914,
    mse_db2: 0.000185,
    rmse_db: 0.013601,
    max_abs_db: 0.124218,
    per_band_mae_db: Array.from({ length: 40 }, (_, i) => Number((0.002 + (i % 7) * 0.0006).toFixed(5))),
    per_class_mae_db: {
      on: 0.0034,
      off: 0.0038,
      stop: 0.0035,
      go: 0.0037,
      _unknown: 0.0041,
      _silence: 0.005,
    },
  },
  '16k_i8_S1.0': {
    mae_db: 1.089735,
    mse_db2: 4.92,
    rmse_db: 2.218107,
    max_abs_db: 16.42551,
    per_band_mae_db: Array.from({ length: 40 }, (_, i) => Number((0.65 + (i < 10 ? 0.85 : i * 0.02)).toFixed(3))),
    per_class_mae_db: {
      on: 0.84,
      off: 0.91,
      stop: 0.78,
      go: 0.88,
      _unknown: 0.95,
      _silence: 2.18,
    },
  },
  '16k_i8_S0.25': {
    mae_db: 0.821018,
    mse_db2: 5.48,
    rmse_db: 2.34094,
    max_abs_db: 34.247005,
    per_band_mae_db: Array.from({ length: 40 }, (_, i) => Number((0.5 + (i > 25 ? 0.65 : 0.28)).toFixed(3))),
    per_class_mae_db: {
      on: 0.74,
      off: 0.79,
      stop: 0.92,
      go: 0.81,
      _unknown: 0.87,
      _silence: 0.79,
    },
  },
  '8k_i16_S1.0_noaa': {
    mae_db: 3.42,
    mse_db2: 24.8,
    rmse_db: 4.98,
    max_abs_db: 29.6,
    per_band_mae_db: Array.from({ length: 40 }, (_, i) => Number((i >= 10 && i <= 15 ? 11.4 : 1.35).toFixed(3))),
    per_class_mae_db: {
      on: 3.12,
      off: 3.25,
      stop: 3.04,
      go: 3.19,
      _unknown: 3.31,
      _silence: 4.61,
    },
  },
};

export const MOCK_STUDENT4_CLASSIFIER_RESULTS: Student4ClassifierResults = {
  split: {
    method: 'stratified_clip_level',
    train_clips: 96,
    test_clips: 48,
    random_seed: 42,
  },
  classes: ['on', 'off', 'stop', 'go', '_unknown', '_silence'],
  evaluations: [
    {
      setting: 'Laptop float32 (16 kHz, AA=True)',
      accuracy: 0.8542,
      precision_macro: 0.8615,
      recall_macro: 0.8542,
      f1_macro: 0.8531,
      confusion_matrix: [
        [7, 0, 0, 1, 0, 0],
        [0, 7, 1, 0, 0, 0],
        [0, 0, 7, 0, 1, 0],
        [1, 0, 0, 6, 1, 0],
        [0, 1, 0, 1, 6, 0],
        [0, 0, 0, 0, 0, 8],
      ],
    },
    {
      setting: 'ESP32 16k int16 S=1.0',
      accuracy: 0.8542,
      precision_macro: 0.8615,
      recall_macro: 0.8542,
      f1_macro: 0.8531,
      confusion_matrix: [
        [7, 0, 0, 1, 0, 0],
        [0, 7, 1, 0, 0, 0],
        [0, 0, 7, 0, 1, 0],
        [1, 0, 0, 6, 1, 0],
        [0, 1, 0, 1, 6, 0],
        [0, 0, 0, 0, 0, 8],
      ],
    },
    {
      setting: 'ESP32 16k int8 S=1.0',
      accuracy: 0.7708,
      precision_macro: 0.779,
      recall_macro: 0.7708,
      f1_macro: 0.7685,
      confusion_matrix: [
        [6, 1, 0, 1, 0, 0],
        [0, 6, 1, 0, 1, 0],
        [0, 1, 6, 0, 1, 0],
        [1, 0, 1, 5, 1, 0],
        [0, 1, 0, 1, 6, 0],
        [0, 0, 0, 0, 0, 8],
      ],
    },
    {
      setting: 'ESP32 16k int8 S=0.25',
      accuracy: 0.7917,
      precision_macro: 0.8012,
      recall_macro: 0.7917,
      f1_macro: 0.7894,
      confusion_matrix: [
        [6, 0, 0, 1, 1, 0],
        [0, 7, 1, 0, 0, 0],
        [0, 1, 6, 0, 1, 0],
        [1, 0, 0, 6, 1, 0],
        [0, 1, 1, 1, 5, 0],
        [0, 0, 0, 0, 0, 8],
      ],
    },
    {
      setting: 'ESP32 8k int16 S=1.0 (No AA)',
      accuracy: 0.6875,
      precision_macro: 0.701,
      recall_macro: 0.6875,
      f1_macro: 0.6832,
      confusion_matrix: [
        [5, 1, 0, 1, 1, 0],
        [1, 5, 1, 0, 1, 0],
        [0, 1, 6, 0, 1, 0],
        [1, 0, 1, 5, 1, 0],
        [1, 1, 1, 1, 4, 0],
        [0, 0, 0, 0, 0, 8],
      ],
    },
  ],
};

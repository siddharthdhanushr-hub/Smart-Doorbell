export type DataOrigin = 'live_api' | 'recorded' | 'mock' | 'awaiting';

export type PageId =
  | 'overview'
  | 'architecture'
  | 'audio'
  | 'communication'
  | 'packets'
  | 'logmel'
  | 'hardware'
  | 'comparison'
  | 'dataset'
  | 'ml';

export interface HealthResponse {
  status: string;
  team: number;
  team_name: string;
  live_board_required: boolean;
  data_mode: string;
}

export interface HardwareConfig {
  team_number: number;
  team_name: string;
  board_operator: string;
  target_board: string;
  chip_detected: {
    chip_type: string;
    cpu_mhz: number;
    crystal_mhz: number;
    mac: string;
    flash_chip_bytes: number;
    psram_detected_by_esptool: string;
  };
  arduino_ide: {
    esp32_core_package: string;
    esp32_core_version_installed: string;
    fqbn_phase1: string;
    fqbn_mission2: string;
    board_menu: string;
    mission2_settings_verified: Record<string, string>;
  };
  usb_ports: {
    usb_native_cdc: {
      port: string;
      pnp_device_id: string;
      baud_note: string;
    };
    com_uart_bridge: {
      port: string;
      pnp_device_id: string;
      default_baud: number;
      rx_buffer_bytes: number;
    };
  };
  board_info_measured: {
    phase1_default: Record<string, number>;
    mission2_opi_16m: Record<string, number>;
  };
}

export interface AudioConfig {
  team_number: number;
  classes: string[];
  clips_per_class: number;
  total_clips: number;
  clip_duration_s: number;
  channels: number;
  mic_native_fs_hz: number;
  allowed_fs_hz: number[];
  default_fs_hz: number;
  default_antialias: boolean;
  byte_order: string;
  supported_formats: Record<string, { bits: number; bytes_per_sample: number; numpy_dtype: string }>;
}

export interface LogmelConfig {
  team_number: number;
  fs: number;
  win_samples: number;
  win_ms: number;
  hop_samples: number;
  hop_ms: number;
  nfft: number;
  mels: number;
  mfcc: number;
  window: string;
  fmin_hz: number;
  fmax_hz: number;
  mel_scale: string;
  spectrum: string;
  log_conversion: string;
  normalisation: string;
  frames_per_1s_clip: number;
  output_shape_per_clip: [number, number];
  output_dtype: string;
  secondary_test_config_25ms_10ms_mfcc13?: {
    fs: number;
    win_samples: number;
    hop_samples: number;
    nfft: number;
    mels: number;
    mfcc: number;
    frames_per_1s_clip: number;
    output_shape_per_clip: [number, number];
  };
}

export interface CommunicationProtocol {
  protocol_name: string;
  endianness: string;
  max_payload_bytes: number;
  crc_algorithm: string;
  crc_coverage: string[];
  text_commands: Record<string, string>;
  binary_frames: {
    uplink_laptop_to_board: { magic: string; layout: string; types: Record<string, string> };
    downlink_board_to_laptop: { magic: string; layout: string; types: Record<string, string> };
  };
}

export interface ConfigsPayload {
  hardware: HardwareConfig;
  audio: AudioConfig;
  logmel: LogmelConfig;
  protocol: CommunicationProtocol;
}

export interface ManifestRow {
  clip_id: string | number;
  source: string;
  label: string;
  sample_rate: string | number;
  num_channels: string | number;
  duration_s: string | number;
  sample_count: string | number;
  format: string;
  antialias: string;
  pool_index: string | number;
  pool_word: string;
  pool_voice: string;
  peak_abs: string | number;
  rms: string | number;
  clipped: string;
  valid: string;
}

export interface DatasetValidation {
  team: number;
  fs: number;
  antialias: boolean;
  total_clips: number;
  expected_clips: number;
  valid_clips: number;
  invalid_clip_ids: number[];
  class_distribution: Record<string, number>;
  duplicate_non_silence_pool_recordings: number;
  team_room_parameters: {
    whine: number;
    whine_amp: number;
    hum: number;
    noise: number;
  };
  speech_pool_total_recordings: number;
  speech_pool_sample_rate: number;
  speech_pool_dtype: string;
}

export interface DatasetPayload {
  validation: DatasetValidation;
  manifest: ManifestRow[];
  data_card_md: string | null;
}

export interface ClipDetailPayload {
  clip_id: number;
  label: string;
  fs: number;
  antialias: boolean;
  waveform: number[];
  first_sample: number[];
  python_logmel: number[][];
  esp32_logmel: number[][] | null;
  esp32_source: string | null;
  origin: DataOrigin;
  note?: string;
}

export interface Mission1Run {
  test_group: string;
  port_label: string;
  port: string;
  baud: number;
  repeat: number;
  fs: number;
  fmt: string;
  speed: number;
  samples_per_packet: number;
  bytes_sent: number;
  packets_sent: number;
  send_seconds: number;
  board_ms: number;
  throughput_laptop_bps: number;
  throughput_board_bps: number;
  effective_samples_per_s: number;
  frames_ok: number;
  bad_crc: number;
  bad_len: number;
  seq_gaps: number;
  dup: number;
  samples_rx: number;
  uart_errors: number;
  why: string;
}

export interface Mission1Payload {
  csv_rows: Record<string, string>[];
  results: {
    timestamp: string;
    com_port: string;
    usb_port: string;
    repeats: number;
    runs: Mission1Run[];
  };
}

export interface Mission2Payload {
  probe_baseline: {
    sram_max_bytes: number;
    sram_max_seconds_16khz_i16: number;
    psram_test_ok: boolean;
    psram_error?: string;
    info: Record<string, unknown>;
    sram_probe_attempts: Array<{ bytes: number; ok: boolean; stored?: number; err?: string }>;
  };
  save144: {
    expected_bytes: number;
    host_crc32_hex: string;
    send_seconds: number;
    psram_exact_match: boolean;
    flash_crc_match: boolean;
    save_reply: { n: number; us: number; crc: number };
    info_before: Record<string, unknown>;
    info_after: Record<string, unknown>;
  };
  verify_power_cut: {
    flash_dump_bytes: number;
    expected_bytes: number;
    host_crc32_hex: string;
    flash_crc_hex: string;
    flash_exact_byte_match: boolean;
    psram_survived_power_cut: boolean;
    psram_crc_after_replug: { where: string; n: number; crc: number };
    flash_crc_after_replug: { where: string; n: number; crc: number };
  };
  python_audio_analysis: {
    aliasing: {
      silence_clip_id: number;
      peak_48khz_hz: number;
      peak_48khz_db: number;
      peak_8khz_no_aa_hz: number;
      peak_8khz_no_aa_db: number;
      reconstructed_true_freq_hz: number;
      level_8khz_with_aa_at_alias_db: number;
      attenuation_db: number;
    };
    sqnr: {
      word_clip_id: number;
      word_peak_abs: number;
      silence_clip_id: number;
      silence_peak_abs: number;
      dataset_global_peak_abs: number;
      single_clip_table: Array<{
        fmt: string;
        scale: number;
        word_sqnr_db: number;
        word_clipped_pct: number;
        silence_sqnr_db: number;
        silence_clipped_pct: number;
      }>;
      all_144_clips_summary: Record<
        string,
        { mean_sqnr_db: number; min_sqnr_db: number; max_sqnr_db: number }
      >;
    };
    recommended_config: {
      fs: number;
      antialias: boolean;
      fmt: string;
      scale: number;
      rationale: string;
    };
  };
}

export interface Mission3Payload {
  starter_10s: {
    expected_features: number;
    received_features: number;
    lost_features: number;
    compute_us: { min: number; mean: number; max: number };
    lag_s: { min: number; mean: number; max: number };
    numerical_diff_vs_numpy_quantised: {
      matched_frames: number;
      max_abs_diff_db: number;
      mean_abs_diff_db: number;
      rmse_db: number;
    };
  };
  optimized: {
    info_before: Record<string, unknown>;
    mel40_10s_realtime: {
      expected_features: number;
      received_features: number;
      lost_features: number;
      compute_us: { min: number; mean: number; max: number };
      lag_s: { min: number; mean: number; max: number };
      numerical_diff_vs_numpy_quantised: {
        matched_frames: number;
        max_abs_diff_db: number;
        mean_abs_diff_db: number;
        rmse_db: number;
      };
    };
    mfcc13_25ms_10ms_10s_realtime: {
      expected_features: number;
      received_features: number;
      lost_features: number;
      compute_us: { min: number; mean: number; max: number };
      downlink_bytes_per_s_steady: number;
      numerical_diff_vs_numpy_quantised: {
        matched_frames: number;
        max_abs_diff_db: number;
        mean_abs_diff_db: number;
        rmse_db: number;
      };
    };
    speed_sweep_5s: Array<{
      feat: boolean;
      speed: number;
      expected: number;
      received: number;
      lost: number;
      seq_gaps: number;
      bad_crc: number;
      samples: number;
      avg_us: number;
      ms: number;
    }>;
  };
}

export interface SkipTestRun {
  tag: string;
  skip_packets: number[];
  expected_total_packets: number;
  packets_sent: number;
  expected_features_no_loss: number;
  received_features: number;
  lost_features: number;
  board: {
    frames_ok: number;
    bad_crc: number;
    seq_gaps: number;
    dup: number;
    samples: number;
    stored: number;
    features: number;
  };
  first_sample_after_gap1: number[];
  first_sample_after_gap2: number[];
  last_5_first_samples: number[];
  expected_last_first_sample: number;
  tail_shift_samples: number;
}

export interface Full144Run {
  tag: string;
  fs: number;
  antialias: boolean;
  fmt: string;
  scale: number;
  win: number;
  hop: number;
  nfft: number;
  mels: number;
  speed: number;
  bytes_sent: number;
  host_crc32_hex: string;
  packets_sent: number;
  send_seconds: number;
  expected_features: number;
  received_features: number;
  lost_features: number;
  bad_crc_back: number;
  compute_us_mean: number | null;
  compute_us_max: number | null;
  lag_s_mean: number | null;
  lag_s_max: number | null;
  board: {
    frames_ok: number;
    bad_crc: number;
    bad_len: number;
    seq_gaps: number;
    dup: number;
    samples: number;
    stored: number;
    where: string;
    features: number;
    max_us: number;
    avg_us: number;
    uart_errors: number;
    ms: number;
  };
  flash_crc_match: boolean | null;
  mae_vs_quantised_numpy_db: number;
  max_diff_vs_quantised_numpy_db: number;
  mae_vs_orig_f32_numpy_db: number;
  max_diff_vs_orig_f32_numpy_db: number;
}

export interface Mission45Payload {
  skip_before_fix: SkipTestRun;
  skip_after_fix: SkipTestRun;
  com_speed_ramp: {
    runs: Array<{
      port: string;
      baud: number;
      speed: number;
      target_uplink_bps: number;
      expected_features: number;
      received_features: number;
      lost_features: number;
      seq_gaps: number;
      bad_crc: number;
      uart_errors: number;
      samples_rx: number;
      expected_samples: number;
      board_ms: number;
      send_seconds: number;
      lag_s_max: number;
    }>;
  };
  all_144_runs: {
    timestamp: string;
    runs: Full144Run[];
  };
}

export interface Student4ValidationSummary {
  dataset: {
    total_clips: number;
    valid_clips: number;
    clean_frames: number;
    excluded_straddling_frames: number;
    frames_per_class: number;
  };
  controlled_skip_test: {
    skip_packets: number[];
    before_fix_tail_shift_samples: number;
    after_fix_tail_shift_samples: number;
  };
  port_limits: {
    usb_com11_max_zero_loss_speed: number;
    com12_921600_max_lag_free_speed: number;
    com12_2000000_max_lag_free_speed: number;
  };
}

export interface FeatureSettingMetrics {
  mae_db: number;
  mse_db2: number;
  rmse_db: number;
  max_abs_db: number;
  per_band_mae_db: number[];
  per_class_mae_db: Record<string, number>;
  reference_baseline?: string;
}

export type Student4FeatureComparison = Record<string, FeatureSettingMetrics>;

export interface ClassifierSettingEval {
  setting: string;
  accuracy: number;
  precision_macro: number;
  recall_macro: number;
  f1_macro: number;
  confusion_matrix: number[][];
}

export interface Student4ClassifierResults {
  split: {
    method: string;
    train_clips: number;
    test_clips: number;
    random_seed: number;
  };
  classes: string[];
  evaluations: ClassifierSettingEval[];
}

export interface DashboardBundle {
  backendStatus: {
    flaskOnline: boolean;
    repoBridgeOnline: boolean;
    modeLabel: string;
  };
  configs: ConfigsPayload;
  dataset: DatasetPayload;
  mission1: Mission1Payload;
  mission2: Mission2Payload;
  mission3: Mission3Payload;
  mission45: Mission45Payload;
  student4: {
    validationSummary: Student4ValidationSummary | null;
    featureComparison: Student4FeatureComparison | null;
    classifierResults: Student4ClassifierResults | null;
    origin: DataOrigin;
  };
}

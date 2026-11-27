import { generateMockClipDetail } from '../data/mock/mockGenerators';
import {
  RECORDED_CONFIGS,
  RECORDED_DATASET,
  RECORDED_MISSION1,
  RECORDED_MISSION2,
  RECORDED_MISSION3,
  RECORDED_MISSION45,
} from '../data/recorded/recordedSnapshot';
import type {
  ClipDetailPayload,
  ConfigsPayload,
  DashboardBundle,
  DatasetPayload,
  HealthResponse,
  ManifestRow,
  Mission1Payload,
  Mission2Payload,
  Mission3Payload,
  Mission45Payload,
  Student4ClassifierResults,
  Student4FeatureComparison,
  Student4ValidationSummary,
} from '../types/dashboard';

async function fetchJsonOrNull<T>(url: string, timeoutMs = 2500): Promise<T | null> {
  const ctrl = new AbortController();
  const timer = setTimeout(() => ctrl.abort(), timeoutMs);
  try {
    const res = await fetch(url, { signal: ctrl.signal });
    if (!res.ok) return null;
    return (await res.json()) as T;
  } catch {
    return null;
  } finally {
    clearTimeout(timer);
  }
}

async function fetchTextOrNull(url: string, timeoutMs = 2500): Promise<string | null> {
  const ctrl = new AbortController();
  const timer = setTimeout(() => ctrl.abort(), timeoutMs);
  try {
    const res = await fetch(url, { signal: ctrl.signal });
    if (!res.ok) return null;
    return await res.text();
  } catch {
    return null;
  } finally {
    clearTimeout(timer);
  }
}

export function parseCsv(text: string): Record<string, string>[] {
  const lines = text.trim().split(/\r?\n/);
  if (lines.length < 2) return [];
  const headers = lines[0].split(',').map((h) => h.trim());
  const rows: Record<string, string>[] = [];
  for (let i = 1; i < lines.length; i++) {
    const line = lines[i].trim();
    if (!line) continue;
    const cols = line.split(',');
    const row: Record<string, string> = {};
    headers.forEach((h, idx) => {
      row[h] = (cols[idx] ?? '').trim();
    });
    rows.push(row);
  }
  return rows;
}

export async function loadDashboardBundle(): Promise<DashboardBundle> {
  const health = await fetchJsonOrNull<HealthResponse>('/api/health', 1500);
  const flaskOnline = health?.status === 'ok';

  // Try Student 2 Flask API first, then Vite /repo static bridge, then verified snapshot fallback.
  let configs: ConfigsPayload | null = flaskOnline
    ? await fetchJsonOrNull<ConfigsPayload>('/api/configs')
    : null;

  let repoBridgeOnline = false;
  if (!configs) {
    const [hardware, audio, logmel, protocol] = await Promise.all([
      fetchJsonOrNull<ConfigsPayload['hardware']>('/repo/shared/hardware_config.json'),
      fetchJsonOrNull<ConfigsPayload['audio']>('/repo/shared/audio_config.json'),
      fetchJsonOrNull<ConfigsPayload['logmel']>('/repo/shared/logmel_config.json'),
      fetchJsonOrNull<ConfigsPayload['protocol']>('/repo/shared/communication_protocol.json'),
    ]);
    if (hardware && audio && logmel && protocol) {
      repoBridgeOnline = true;
      configs = { hardware, audio, logmel, protocol };
    }
  } else {
    // Check whether /repo/ bridge is available for Student 4 files and static plots
    const probe = await fetchJsonOrNull('/repo/shared/audio_config.json', 1000);
    repoBridgeOnline = probe !== null;
  }

  let dataset: DatasetPayload | null = flaskOnline
    ? await fetchJsonOrNull<DatasetPayload>('/api/dataset')
    : null;
  if (!dataset && repoBridgeOnline) {
    const [validation, manifestCsv, dataCardMd] = await Promise.all([
      fetchJsonOrNull<DatasetPayload['validation']>('/repo/dataset/dataset_validation.json'),
      fetchTextOrNull('/repo/dataset/dataset_manifest.csv'),
      fetchTextOrNull('/repo/dataset/data_card.md'),
    ]);
    if (validation && manifestCsv) {
      dataset = {
        validation,
        manifest: parseCsv(manifestCsv) as unknown as ManifestRow[],
        data_card_md: dataCardMd,
      };
    }
  }

  let mission1: Mission1Payload | null = flaskOnline
    ? await fetchJsonOrNull<Mission1Payload>('/api/benchmarks/mission1')
    : null;
  if (!mission1 && repoBridgeOnline) {
    const [csvText, results] = await Promise.all([
      fetchTextOrNull('/repo/student1_esp32/benchmarks/mission1_throughput.csv'),
      fetchJsonOrNull<Mission1Payload['results']>('/repo/student1_esp32/logs/mission1_pipe_results.json'),
    ]);
    if (results) {
      mission1 = {
        csv_rows: csvText ? parseCsv(csvText) : [],
        results,
      };
    }
  }

  let mission2: Mission2Payload | null = flaskOnline
    ? await fetchJsonOrNull<Mission2Payload>('/api/benchmarks/mission2')
    : null;
  if (!mission2 && repoBridgeOnline) {
    const [probe, save144, verify, audioAnalysis] = await Promise.all([
      fetchJsonOrNull<Mission2Payload['probe_baseline']>('/repo/student1_esp32/logs/mission2_probe_baseline.json'),
      fetchJsonOrNull<Mission2Payload['save144']>('/repo/student1_esp32/logs/mission2_save144_opi_16m.json'),
      fetchJsonOrNull<Mission2Payload['verify_power_cut']>('/repo/student1_esp32/logs/mission2_verify_opi_16m.json'),
      fetchJsonOrNull<Mission2Payload['python_audio_analysis']>('/repo/student2_python/documentation/mission2_audio_analysis.json'),
    ]);
    if (probe && save144 && verify && audioAnalysis) {
      mission2 = {
        probe_baseline: probe,
        save144,
        verify_power_cut: verify,
        python_audio_analysis: audioAnalysis,
      };
    }
  }

  let mission3: Mission3Payload | null = flaskOnline
    ? await fetchJsonOrNull<Mission3Payload>('/api/benchmarks/mission3')
    : null;
  if (!mission3 && repoBridgeOnline) {
    const [starter, optimized] = await Promise.all([
      fetchJsonOrNull<Mission3Payload['starter_10s']>('/repo/student1_esp32/logs/mission3_starter_10s.json'),
      fetchJsonOrNull<Mission3Payload['optimized']>('/repo/student1_esp32/logs/mission3_optimized_results.json'),
    ]);
    if (starter && optimized) {
      mission3 = { starter_10s: starter, optimized };
    }
  }

  let mission45: Mission45Payload | null = flaskOnline
    ? await fetchJsonOrNull<Mission45Payload>('/api/benchmarks/mission4_5')
    : null;
  if (!mission45 && repoBridgeOnline) {
    const [skipBefore, skipAfter, comRamp, all144] = await Promise.all([
      fetchJsonOrNull<Mission45Payload['skip_before_fix']>('/repo/student1_esp32/logs/mission4_skip_before_fix.json'),
      fetchJsonOrNull<Mission45Payload['skip_after_fix']>('/repo/student1_esp32/logs/mission4_skip_after_fix.json'),
      fetchJsonOrNull<Mission45Payload['com_speed_ramp']>('/repo/student1_esp32/logs/mission4_com_speed_ramp.json'),
      fetchJsonOrNull<Mission45Payload['all_144_runs']>('/repo/student1_esp32/logs/phase5_144clips_all_runs.json'),
    ]);
    if (skipBefore && skipAfter && comRamp && all144) {
      mission45 = {
        skip_before_fix: skipBefore,
        skip_after_fix: skipAfter,
        com_speed_ramp: comRamp,
        all_144_runs: all144,
      };
    }
  }

  // Student 4 outputs (loaded directly when Student 4 commits them)
  const [valSummary, featComparison, clfResults] = repoBridgeOnline
    ? await Promise.all([
        fetchJsonOrNull<Student4ValidationSummary>('/repo/student4_validation/outputs/mission4_validation_summary.json', 1200),
        fetchJsonOrNull<Student4FeatureComparison>('/repo/student4_validation/outputs/mission5_feature_comparison.json', 1200),
        fetchJsonOrNull<Student4ClassifierResults>('/repo/student4_validation/outputs/mission5_classifier_results.json', 1200),
      ])
    : [null, null, null];

  const hasStudent4 = Boolean(valSummary || featComparison || clfResults);

  const modeLabel = flaskOnline
    ? 'Student 2 Flask API + Recorded Hardware Logs'
    : repoBridgeOnline
      ? 'Repo Static Bridge + Recorded Hardware Logs'
      : 'Embedded Verified Recorded Snapshot';

  return {
    backendStatus: {
      flaskOnline,
      repoBridgeOnline,
      modeLabel,
    },
    configs: configs ?? RECORDED_CONFIGS,
    dataset: dataset ?? RECORDED_DATASET,
    mission1: mission1 ?? RECORDED_MISSION1,
    mission2: mission2 ?? RECORDED_MISSION2,
    mission3: mission3 ?? RECORDED_MISSION3,
    mission45: mission45 ?? RECORDED_MISSION45,
    student4: {
      validationSummary: valSummary,
      featureComparison: featComparison,
      classifierResults: clfResults,
      origin: hasStudent4 ? 'recorded' : 'awaiting',
    },
  };
}

export async function loadClipDetail(
  clipId: number,
  fs: number,
  antialias: boolean,
  manifestRow?: ManifestRow,
  flaskOnline = true,
): Promise<ClipDetailPayload> {
  if (flaskOnline) {
    const apiRes = await fetchJsonOrNull<Omit<ClipDetailPayload, 'origin'>>(
      `/api/clips/${clipId}?fs=${fs}&antialias=${antialias}`,
      3500,
    );
    if (apiRes && Array.isArray(apiRes.waveform) && Array.isArray(apiRes.python_logmel)) {
      return {
        ...apiRes,
        origin: 'live_api',
      };
    }
  }
  return generateMockClipDetail(clipId, fs, antialias, manifestRow);
}

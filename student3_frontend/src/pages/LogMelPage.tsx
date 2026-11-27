import { useMemo } from 'react';
import type { ClipDetailPayload, DashboardBundle } from '../types/dashboard';
import { SpectrogramCanvas } from '../components/charts/SpectrogramCanvas';
import { EmptyAwaitingCard } from '../components/ui/EmptyAwaitingCard';
import { KpiCard } from '../components/ui/KpiCard';
import { SectionCard } from '../components/ui/SectionCard';

interface LogMelPageProps {
  bundle: DashboardBundle;
  clipId: number;
  fs: number;
  antialias: boolean;
  onChangeClip: (id: number) => void;
  clipDetail: ClipDetailPayload | null;
  clipLoading: boolean;
}

export function LogMelPage({
  bundle,
  clipId,
  fs,
  antialias,
  onChangeClip,
  clipDetail,
  clipLoading,
}: LogMelPageProps) {
  const cfg = bundle.configs.logmel;
  const manifest = bundle.dataset.manifest;

  const diffStats = useMemo(() => {
    if (!clipDetail?.python_logmel || !clipDetail?.esp32_logmel) return null;
    const py = clipDetail.python_logmel;
    const esp = clipDetail.esp32_logmel;
    let sumAbs = 0;
    let sumSq = 0;
    let maxAbs = 0;
    let count = 0;
    for (let f = 0; f < Math.min(py.length, esp.length); f++) {
      for (let m = 0; m < Math.min(py[f].length, esp[f].length); m++) {
        const d = Math.abs(esp[f][m] - py[f][m]);
        sumAbs += d;
        sumSq += d * d;
        if (d > maxAbs) maxAbs = d;
        count++;
      }
    }
    if (count === 0) return null;
    return {
      mae: sumAbs / count,
      rmse: Math.sqrt(sumSq / count),
      maxAbs,
    };
  }, [clipDetail]);

  return (
    <div className="space-y-6">
      {/* Extraction Config KPIs */}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <KpiCard
          title="Feature Matrix Shape"
          value={`${cfg.output_shape_per_clip[0]} × ${cfg.output_shape_per_clip[1]}`}
          unit={cfg.output_dtype}
          subtitle={`${cfg.frames_per_1s_clip} frames/s × ${cfg.mels} HTK mel bands`}
          origin="recorded"
          accent="cyan"
        />
        <KpiCard
          title="Window & Hop"
          value={`${cfg.win_samples} / ${cfg.hop_samples}`}
          unit="samples"
          subtitle={`${cfg.win_ms} ms Hann window · ${cfg.hop_ms} ms hop · nfft=${cfg.nfft}`}
          origin="recorded"
          accent="cyan"
        />
        <KpiCard
          title="Frequency Range"
          value={`${cfg.fmin_hz}–${cfg.fmax_hz}`}
          unit="Hz"
          subtitle={`${cfg.mel_scale} · ${cfg.log_conversion}`}
          origin="recorded"
          accent="emerald"
        />
        <KpiCard
          title="Selected Clip Diff (MAE)"
          value={diffStats ? diffStats.mae.toFixed(6) : null}
          unit="dB"
          subtitle={
            diffStats
              ? `RMSE: ${diffStats.rmse.toFixed(6)} dB · Max: ${diffStats.maxAbs.toFixed(5)} dB`
              : 'ESP32 recorded clip array applies to 16 kHz antialias=True'
          }
          origin={clipDetail?.origin === 'live_api' && clipDetail.esp32_logmel ? 'recorded' : 'mock'}
          accent="amber"
        />
      </div>

      {/* Quick Clip Selector */}
      <SectionCard
        title="Log-Mel Spectrogram Inspector"
        subtitle={`Viewing Clip #${clipId} (${clipDetail?.label ?? '...'}) · ${fs.toLocaleString()} Hz · antialias=${String(antialias)}`}
        origin={clipDetail?.origin ?? 'mock'}
        headerRight={
          <div className="flex items-center gap-2">
            <label className="text-xs text-slate-400">Clip #:</label>
            <select
              value={clipId}
              onChange={(e) => onChangeClip(Number(e.target.value))}
              className="rounded-lg border border-slate-700 bg-slate-950 px-2.5 py-1 font-mono text-xs text-slate-100"
            >
              {manifest.map((r) => (
                <option key={String(r.clip_id)} value={Number(r.clip_id)}>
                  #{r.clip_id} ({r.label})
                </option>
              ))}
            </select>
          </div>
        }
      >
        {clipLoading ? (
          <div className="flex h-56 items-center justify-center rounded-lg border border-slate-800 bg-slate-950 text-xs text-slate-400">
            Computing log-mel spectrogram for clip #{clipId}...
          </div>
        ) : clipDetail ? (
          <div className="grid gap-6 lg:grid-cols-2">
            <SpectrogramCanvas
              matrix={clipDetail.python_logmel}
              title={`Python Reference Log-Mel (${clipDetail.origin === 'live_api' ? 'NumPy HTK' : 'Simulated'})`}
              unit="dB"
              height={240}
            />

            {clipDetail.esp32_logmel ? (
              <SpectrogramCanvas
                matrix={clipDetail.esp32_logmel}
                title={
                  clipDetail.origin === 'live_api'
                    ? 'ESP32-S3 Board Log-Mel (Recorded 16k i16)'
                    : 'ESP32-S3 Board Log-Mel (Simulated Preview)'
                }
                unit="dB"
                height={240}
              />
            ) : (
              <EmptyAwaitingCard
                variant="empty"
                title="ESP32 Recorded Array Only Available for 16 kHz (AA=True)"
                description="Switch Audio Input to 16,000 Hz with Antialias enabled (or inspect the 4 full-run settings on the Laptop vs ESP32 Comparison page)."
              />
            )}
          </div>
        ) : null}

        {/* Extraction Specification Table */}
        <div className="mt-5 grid gap-3 rounded-lg border border-slate-800 bg-slate-950/60 p-3 text-xs sm:grid-cols-2 lg:grid-cols-4">
          <div>
            <span className="text-slate-400">Window Function</span>
            <p className="mt-0.5 font-mono text-slate-200">{cfg.window}</p>
          </div>
          <div>
            <span className="text-slate-400">Spectrum</span>
            <p className="mt-0.5 font-mono text-slate-200">{cfg.spectrum}</p>
          </div>
          <div>
            <span className="text-slate-400">Normalisation</span>
            <p className="mt-0.5 font-mono text-slate-200">{cfg.normalisation}</p>
          </div>
          <div>
            <span className="text-slate-400">Secondary MFCC Test</span>
            <p className="mt-0.5 font-mono text-slate-200">
              {cfg.secondary_test_config_25ms_10ms_mfcc13
                ? `${cfg.secondary_test_config_25ms_10ms_mfcc13.output_shape_per_clip.join('×')} (MFCC-13)`
                : 'N/A'}
            </p>
          </div>
        </div>
      </SectionCard>
    </div>
  );
}

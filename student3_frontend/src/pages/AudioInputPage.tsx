import { useMemo } from 'react';
import type { ClipDetailPayload, DashboardBundle } from '../types/dashboard';
import { WaveformCanvas } from '../components/charts/WaveformCanvas';
import { EmptyAwaitingCard } from '../components/ui/EmptyAwaitingCard';
import { KpiCard } from '../components/ui/KpiCard';
import { SectionCard } from '../components/ui/SectionCard';

interface AudioInputPageProps {
  bundle: DashboardBundle;
  clipId: number;
  fs: number;
  antialias: boolean;
  onChangeClip: (id: number) => void;
  onChangeFs: (fs: number) => void;
  onChangeAntialias: (aa: boolean) => void;
  clipDetail: ClipDetailPayload | null;
  clipLoading: boolean;
}

export function AudioInputPage({
  bundle,
  clipId,
  fs,
  antialias,
  onChangeClip,
  onChangeFs,
  onChangeAntialias,
  clipDetail,
  clipLoading,
}: AudioInputPageProps) {
  const manifest = bundle.dataset.manifest;
  const classes = bundle.configs.audio.classes;

  const selectedRow = useMemo(
    () => manifest.find((r) => Number(r.clip_id) === clipId) ?? manifest[0],
    [manifest, clipId],
  );

  const clipsInSelectedClass = useMemo(() => {
    const lbl = selectedRow?.label;
    return manifest.filter((r) => r.label === lbl);
  }, [manifest, selectedRow]);

  return (
    <div className="space-y-6">
      {/* Controls */}
      <SectionCard
        title="Audio Clip Selector & Resampling Controls"
        subtitle="Inspect any of the 144 Team 1 clips across 6 command classes"
        origin={clipDetail?.origin ?? 'mock'}
        originLabel={
          clipDetail?.origin === 'live_api'
            ? 'Live Flask /api/clips'
            : 'Mock / Simulated Preview (Flask API or speech_pool.npz offline)'
        }
      >
        <div className="grid gap-4 md:grid-cols-4">
          <div>
            <label className="mb-1 block text-xs font-medium text-slate-400">Filter by Class</label>
            <select
              value={selectedRow?.label ?? 'on'}
              onChange={(e) => {
                const firstInClass = manifest.find((r) => r.label === e.target.value);
                if (firstInClass) onChangeClip(Number(firstInClass.clip_id));
              }}
              className="w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-xs text-slate-100"
            >
              {classes.map((c) => (
                <option key={c} value={c}>
                  {c}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="mb-1 block text-xs font-medium text-slate-400">Clip ID (0..143)</label>
            <select
              value={clipId}
              onChange={(e) => onChangeClip(Number(e.target.value))}
              className="w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 font-mono text-xs text-slate-100"
            >
              {clipsInSelectedClass.map((r) => (
                <option key={String(r.clip_id)} value={Number(r.clip_id)}>
                  #{r.clip_id} ({r.label} · {r.pool_voice})
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="mb-1 block text-xs font-medium text-slate-400">Sampling Rate (Hz)</label>
            <select
              value={fs}
              onChange={(e) => onChangeFs(Number(e.target.value))}
              className="w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 font-mono text-xs text-slate-100"
            >
              {[16000, 8000, 48000, 24000, 12000].map((rate) => (
                <option key={rate} value={rate}>
                  {rate.toLocaleString()} Hz
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="mb-1 block text-xs font-medium text-slate-400">Anti-Alias Low-Pass Filter</label>
            <button
              type="button"
              onClick={() => onChangeAntialias(!antialias)}
              className={`w-full rounded-lg border px-3 py-2 text-xs font-medium ${
                antialias
                  ? 'border-emerald-500/40 bg-emerald-500/15 text-emerald-200'
                  : 'border-amber-500/40 bg-amber-500/15 text-amber-200'
              }`}
            >
              {antialias ? 'Antialias: ENABLED (255-tap Blackman)' : 'Antialias: DISABLED (Aliasing Active)'}
            </button>
          </div>
        </div>
      </SectionCard>

      {/* Metadata KPIs */}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <KpiCard
          title="Selected Clip & Label"
          value={`#${clipId} · ${selectedRow?.label ?? 'N/A'}`}
          subtitle={`Voice: ${selectedRow?.pool_voice ?? 'N/A'}`}
          origin="recorded"
        />
        <KpiCard
          title="Sample Rate & Samples"
          value={fs.toLocaleString()}
          unit="Hz"
          subtitle={`${fs.toLocaleString()} mono samples · ${bundle.configs.audio.clip_duration_s.toFixed(1)} s`}
          origin="recorded"
        />
        <KpiCard
          title="Peak Amplitude (16k Ref)"
          value={selectedRow ? Number(selectedRow.peak_abs).toFixed(4) : null}
          unit="norm"
          subtitle={`RMS: ${selectedRow ? Number(selectedRow.rms).toFixed(4) : 'N/A'} · Clipped: ${selectedRow?.clipped ?? 'N/A'}`}
          origin="recorded"
          accent="emerald"
        />
        <KpiCard
          title="Team 1 Room Noise"
          value={`${bundle.dataset.validation.team_room_parameters.whine.toFixed(0)} Hz`}
          unit="whine"
          subtitle={`Hum: ${bundle.dataset.validation.team_room_parameters.hum} Hz · Noise std: ${bundle.dataset.validation.team_room_parameters.noise.toFixed(4)}`}
          origin="recorded"
          accent="amber"
        />
      </div>

      {/* Waveform */}
      <SectionCard
        title="Time-Domain Audio Waveform"
        subtitle={`Clip #${clipId} (${selectedRow?.label ?? ''}) at ${fs.toLocaleString()} Hz · antialias=${String(antialias)}`}
        origin={clipDetail?.origin ?? 'mock'}
      >
        {clipLoading ? (
          <div className="flex h-48 items-center justify-center rounded-lg border border-slate-800 bg-slate-950 text-xs text-slate-400">
            Loading waveform for clip #{clipId}...
          </div>
        ) : clipDetail ? (
          <div className="space-y-3">
            <WaveformCanvas samples={clipDetail.waveform} fs={clipDetail.fs} height={220} />
            <div className="flex flex-wrap items-center justify-between gap-2 text-xs text-slate-400">
              <span>X-axis: Time (0.00 s to 1.00 s) · Y-axis: Normalized amplitude (-1.0 to +1.0)</span>
              {clipDetail.note ? <span className="text-amber-300">{clipDetail.note}</span> : null}
            </div>
          </div>
        ) : (
          <EmptyAwaitingCard
            variant="error"
            title="Waveform unavailable"
            description="Could not load waveform from API or mock generator."
          />
        )}
      </SectionCard>
    </div>
  );
}

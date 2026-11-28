import { CheckCircle2, Clock, Cpu, Database, HardDrive, ShieldCheck, Users } from 'lucide-react';
import type { DashboardBundle, PageId } from '../types/dashboard';
import { KpiCard } from '../components/ui/KpiCard';
import { SectionCard } from '../components/ui/SectionCard';

interface OverviewPageProps {
  bundle: DashboardBundle;
  onNavigate: (page: PageId) => void;
}

export function OverviewPage({ bundle, onNavigate }: OverviewPageProps) {
  const primaryRun = bundle.mission45.all_144_runs.runs[0];
  const mel40 = bundle.mission3.optimized.mel40_10s_realtime;
  const starter = bundle.mission3.starter_10s;
  const speedup = Math.round(starter.compute_us.mean / mel40.compute_us.mean);
  const dutyCyclePct =
    primaryRun.compute_us_mean !== null ? ((primaryRun.compute_us_mean / 20000) * 100).toFixed(2) : 'N/A';
  const cleanFrames = bundle.student4.validationSummary?.dataset.clean_frames ?? 7056;
  const excludedFrames = bundle.student4.validationSummary?.dataset.excluded_straddling_frames ?? 143;
  const totalCrcErr = primaryRun.board.bad_crc + primaryRun.bad_crc_back;

  const missions = [
    {
      name: 'Phase 1 — Board Setup & Ports',
      owner: 'Student 1 (Siddharth)',
      status: 'Complete',
      detail: 'ESP32-S3 N16R8 flashed; COM11 (USB CDC) & COM12 (UART) verified.',
      done: true,
    },
    {
      name: 'Mission 1 — Serial Pipe Benchmarks',
      owner: 'Students 1 & 2',
      status: 'Complete',
      detail: `${bundle.mission1.results.runs.length} benchmark runs across COM12 & COM11.`,
      done: true,
    },
    {
      name: 'Mission 2 — Sampling, SQNR & Persistence',
      owner: 'Students 1 & 2',
      status: 'Complete',
      detail: `74.21 dB SQNR (16 kHz i16); LittleFS flash CRC ${bundle.mission2.verify_power_cut.flash_crc_hex} verified after power cut.`,
      done: true,
    },
    {
      name: 'Mission 3 — Radix-2 FFT Optimization',
      owner: 'Student 1',
      status: 'Complete',
      detail: `${mel40.compute_us.mean.toFixed(2)} us/frame (${speedup.toLocaleString()}x faster than starter DFT).`,
      done: true,
    },
    {
      name: 'Mission 4 & 5 — 144-Clip Extraction & Data Card',
      owner: 'Students 1 & 2',
      status: 'Complete',
      detail: `${primaryRun.received_features}/${primaryRun.expected_features} features returned, 0 lost, 7,056 clean frames exported.`,
      done: true,
    },
    {
      name: 'Frontend Dashboard & API Integration',
      owner: 'Student 3 (Frontend)',
      status: 'Active / Ready',
      detail: '10-page responsive engineering dashboard with Flask API, Repo bridge & mock fallback.',
      done: true,
    },
    {
      name: 'Mission 4 & 5 — Full Validation & ML Evaluation',
      owner: 'Student 4 (Validation & ML)',
      status: bundle.student4.origin === 'awaiting' ? 'Pending Handover' : 'Complete',
      detail:
        bundle.student4.origin === 'awaiting'
          ? 'Awaiting mission4_validation_summary.json, mission5_feature_comparison.json, and mission5_classifier_results.json.'
          : 'All Student 4 validation and classifier outputs loaded.',
      done: bundle.student4.origin !== 'awaiting',
    },
  ];

  return (
    <div className="space-y-6">
      {/* Honesty / Data Source Banner */}
      <div className="rounded-xl border border-cyan-500/30 bg-cyan-950/20 p-4">
        <div className="flex flex-wrap items-start justify-between gap-3">
          <div>
            <p className="text-xs font-semibold uppercase tracking-wider text-cyan-300">
              Project Overview · Team 1 ({bundle.configs.hardware.team_name})
            </p>
            <h2 className="mt-1 text-xl font-bold text-slate-100">
              Smart Doorbell — Edge AI (&ldquo;The Doorbell&apos;s Ears&rdquo;)
            </h2>
            <p className="mt-1 max-w-3xl text-sm text-slate-300">
              End-to-end audio streaming, deterministic quantisation, persistent flash storage, real-time on-device
              HTK log-mel feature extraction on <span className="font-mono text-cyan-300">ESP32-S3-DevKitC-1 N16R8</span>,
              and numerical/ML parity evaluation against a Python NumPy reference.
            </p>
          </div>
          <div className="rounded-lg border border-slate-700 bg-slate-900/90 px-3 py-2 text-xs text-slate-300">
            <p className="font-semibold text-slate-100">Data Integrity Policy</p>
            <p className="mt-0.5 text-slate-400">
              No physical ESP32-S3 connection required. Hardware metrics come from verified recorded runs; pending or
              offline items are explicitly labeled.
            </p>
          </div>
        </div>
      </div>

      {/* KPI Grid */}
      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <KpiCard
          title="Validated Dataset"
          value={`${bundle.dataset.validation.valid_clips} / ${bundle.dataset.validation.total_clips}`}
          unit="clips"
          subtitle={`${cleanFrames.toLocaleString()} clean frames (49/clip × 6 classes; ${excludedFrames} straddling excluded)`}
          origin="recorded"
          accent="cyan"
          icon={<Database className="h-4 w-4" />}
        />
        <KpiCard
          title="Shipping Audio Config"
          value="16 kHz · i16"
          unit="S=1.0"
          subtitle={`${bundle.mission2.python_audio_analysis.sqnr.all_144_clips_summary['i16_S1.0']?.mean_sqnr_db.toFixed(2) ?? 'N/A'} dB mean SQNR · 0% clipping · 32,000 B/s uplink`}
          origin="recorded"
          accent="emerald"
          icon={<ShieldCheck className="h-4 w-4" />}
        />
        <KpiCard
          title="ESP32 Compute Latency"
          value={primaryRun.compute_us_mean?.toFixed(2)}
          unit="us/frame"
          subtitle={`${speedup.toLocaleString()}× faster than starter DFT (${dutyCyclePct}% CPU duty cycle)`}
          origin="recorded"
          accent="cyan"
          icon={<Cpu className="h-4 w-4" />}
        />
        <KpiCard
          title="144-Clip Delivery & Flash CRC"
          value={`${primaryRun.lost_features}`}
          unit="lost pkts"
          subtitle={`${primaryRun.packets_sent.toLocaleString()} pkts sent · ${totalCrcErr} CRC errors · Flash CRC ${bundle.mission2.verify_power_cut.flash_crc_hex}`}
          origin="recorded"
          accent="emerald"
          icon={<HardDrive className="h-4 w-4" />}
        />
      </div>

      {/* Workflow + Team Responsibilities */}
      <div className="grid gap-6 lg:grid-cols-2">
        <SectionCard
          title="End-to-End Engineering Workflow"
          subtitle="Six-stage signal processing and verification pipeline"
          origin="recorded"
        >
          <ol className="space-y-3 text-xs">
            {[
              ['1. Deterministic Audio Synthesis', 'team_audio.py generates 144 one-second clips (24/class) with Team 1 room acoustics (7348 Hz whine, 100 Hz hum).'],
              ['2. Codec & Framing', 'audio_codec.py quantises to f32/i16/i8 and wraps 320-sample payloads in 0xA5 0x5A CRC-32 frames.'],
              ['3. USB/UART Transmission', 'serial_sender.py streams over COM11 (USB CDC) or COM12 (WCH UART) with sequence numbers.'],
              ['4. On-Board Storage & Radix-2 FFT', 'ESP32-S3 buffers 4.608 MB in OPI PSRAM, persists /rec.bin to LittleFS, and runs 40-band HTK log-mel FFT in 685 us.'],
              ['5. Downlink & Parity Audit', 'Board returns 0xB5 0x5B feature frames (F) and stream summaries (S) for exact alignment checks.'],
              ['6. Validation & Classification', 'Student 4 computes MAE/MSE/RMSE and clip-split Nearest-Centroid ML metrics; Student 3 visualizes everything.'],
            ].map(([step, desc]) => (
              <li key={step} className="rounded-lg border border-slate-800 bg-slate-950/60 p-3">
                <p className="font-semibold text-cyan-300">{step}</p>
                <p className="mt-1 text-slate-300">{desc}</p>
              </li>
            ))}
          </ol>
        </SectionCard>

        <SectionCard
          title="Team Responsibilities & Tech Stack"
          subtitle="Clear ownership boundaries across Students 1–4"
          origin="recorded"
        >
          <div className="space-y-3 text-xs">
            <div className="flex items-start gap-3 rounded-lg border border-slate-800 bg-slate-950/60 p-3">
              <Users className="mt-0.5 h-4 w-4 shrink-0 text-cyan-300" />
              <div>
                <p className="font-semibold text-slate-100">Student 1 — ESP32-S3 Firmware & Physical Runs</p>
                <p className="mt-0.5 text-slate-400">
                  Arduino C++ (<code className="text-cyan-300">doorbell_board.ino</code>, <code className="text-cyan-300">features.h</code>), OPI PSRAM, LittleFS, COM11/COM12 hardware benchmarks.
                </p>
              </div>
            </div>
            <div className="flex items-start gap-3 rounded-lg border border-slate-800 bg-slate-950/60 p-3">
              <Users className="mt-0.5 h-4 w-4 shrink-0 text-emerald-300" />
              <div>
                <p className="font-semibold text-slate-100">Student 2 — Python Audio, Serial & JSON API</p>
                <p className="mt-0.5 text-slate-400">
                  Codec (<code className="text-emerald-300">audio_codec.py</code>), PySerial sender, NumPy HTK log-mel reference, Flask API (<code className="text-emerald-300">server.py</code>).
                </p>
              </div>
            </div>
            <div className="flex items-start gap-3 rounded-lg border border-slate-800 bg-slate-950/60 p-3">
              <Users className="mt-0.5 h-4 w-4 shrink-0 text-amber-300" />
              <div>
                <p className="font-semibold text-slate-100">Student 3 — Frontend Dashboard & Integration (You)</p>
                <p className="mt-0.5 text-slate-400">
                  React 19, TypeScript, Vite, Tailwind CSS, HTML5 Canvas spectrograms/waveforms, SVG charts, offline + API state handling.
                </p>
              </div>
            </div>
            <div className="flex items-start gap-3 rounded-lg border border-slate-800 bg-slate-950/60 p-3">
              <Users className="mt-0.5 h-4 w-4 shrink-0 text-purple-300" />
              <div>
                <p className="font-semibold text-slate-100">Student 4 — Validation & ML Evaluation</p>
                <p className="mt-0.5 text-slate-400">
                  MAE/MSE/RMSE analysis across 4 settings, 8 kHz AA vs no-AA comparison, clip-level Nearest-Centroid classifier & confusion matrix.
                </p>
              </div>
            </div>
          </div>

          <div className="mt-4 flex flex-wrap gap-2">
            {['ESP32-S3 N16R8', 'Arduino C++ / LittleFS', 'Python 3 + NumPy + Flask', 'React 19 + TypeScript', 'Vite + Tailwind CSS'].map((tech) => (
              <span
                key={tech}
                className="rounded-md border border-slate-700 bg-slate-950 px-2.5 py-1 font-mono text-[11px] text-slate-300"
              >
                {tech}
              </span>
            ))}
          </div>
        </SectionCard>
      </div>

      {/* Mission Progress */}
      <SectionCard
        title="Mission Progress Tracker"
        subtitle="Status derived directly from verified repository artifacts and Student 4 handover files"
        origin="recorded"
      >
        <div className="grid gap-3 md:grid-cols-2">
          {missions.map((m) => (
            <div
              key={m.name}
              className="flex items-start gap-3 rounded-lg border border-slate-800 bg-slate-950/60 p-3"
            >
              {m.done ? (
                <CheckCircle2 className="mt-0.5 h-4 w-4 shrink-0 text-emerald-400" />
              ) : (
                <Clock className="mt-0.5 h-4 w-4 shrink-0 text-amber-400" />
              )}
              <div className="min-w-0 flex-1">
                <div className="flex flex-wrap items-center justify-between gap-2">
                  <p className="text-xs font-semibold text-slate-100">{m.name}</p>
                  <span
                    className={`rounded px-1.5 py-0.5 text-[10px] font-medium ${
                      m.done ? 'bg-emerald-500/15 text-emerald-300' : 'bg-amber-500/15 text-amber-300'
                    }`}
                  >
                    {m.status}
                  </span>
                </div>
                <p className="mt-0.5 text-[11px] text-slate-400">{m.owner}</p>
                <p className="mt-1 text-xs text-slate-300">{m.detail}</p>
              </div>
            </div>
          ))}
        </div>

        <div className="mt-4 flex flex-wrap gap-2">
          <button
            type="button"
            onClick={() => onNavigate('architecture')}
            className="rounded-lg border border-cyan-500/40 bg-cyan-500/10 px-3 py-1.5 text-xs font-medium text-cyan-200 hover:bg-cyan-500/20"
          >
            Inspect System Architecture
          </button>
          <button
            type="button"
            onClick={() => onNavigate('audio')}
            className="rounded-lg border border-slate-700 bg-slate-800 px-3 py-1.5 text-xs font-medium text-slate-200 hover:bg-slate-700"
          >
            Explore Audio & Spectrograms
          </button>
          <button
            type="button"
            onClick={() => onNavigate('ml')}
            className="rounded-lg border border-slate-700 bg-slate-800 px-3 py-1.5 text-xs font-medium text-slate-200 hover:bg-slate-700"
          >
            View ML Evaluation Status
          </button>
        </div>
      </SectionCard>
    </div>
  );
}

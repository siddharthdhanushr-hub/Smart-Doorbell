import { useMemo } from 'react';
import type { DashboardBundle } from '../types/dashboard';
import { LineChart } from '../components/charts/LineChart';
import { KpiCard } from '../components/ui/KpiCard';
import { SectionCard } from '../components/ui/SectionCard';

export function PacketIntegrityPage({ bundle }: { bundle: DashboardBundle }) {
  const primary = bundle.mission45.all_144_runs.runs[0];
  const before = bundle.mission45.skip_before_fix;
  const after = bundle.mission45.skip_after_fix;
  const comRamp = bundle.mission45.com_speed_ramp.runs;
  const usbSweep = bundle.mission3.optimized.speed_sweep_5s.filter((r) => r.feat);

  const rampSeries = useMemo(() => {
    const com921 = comRamp.filter((r) => r.baud === 921600);
    const com2M = comRamp.filter((r) => r.baud === 2000000);
    return {
      lag921: com921.map((r) => ({ x: r.speed, y: r.lag_s_max })),
      lag2M: com2M.map((r) => ({ x: r.speed, y: r.lag_s_max })),
      usbLoss: usbSweep.map((r) => ({ x: r.speed, y: r.lost })),
      com921Loss: com921.map((r) => ({ x: r.speed, y: r.lost_features })),
      com2MLoss: com2M.map((r) => ({ x: r.speed, y: r.lost_features })),
    };
  }, [comRamp, usbSweep]);

  return (
    <div className="space-y-6">
      {/* 144-Clip Accounting KPIs */}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-5">
        <KpiCard
          title="Packets Sent"
          value={primary.packets_sent.toLocaleString()}
          unit="pkts"
          subtitle={`${primary.board.frames_ok.toLocaleString()} frames_ok (incl. END)`}
          origin="recorded"
          accent="cyan"
        />
        <KpiCard
          title="Features Received"
          value={`${primary.received_features.toLocaleString()} / ${primary.expected_features.toLocaleString()}`}
          subtitle="100% feature delivery across 144 clips"
          origin="recorded"
          accent="emerald"
        />
        <KpiCard
          title="Packet / Seq Losses"
          value={primary.board.seq_gaps}
          unit="gaps"
          subtitle={`Lost features: ${primary.lost_features}`}
          origin="recorded"
          accent="emerald"
        />
        <KpiCard
          title="Duplicate Packets"
          value={primary.board.dup}
          unit="dups"
          subtitle="Verified via u32 monotonic seq counter"
          origin="recorded"
          accent="emerald"
        />
        <KpiCard
          title="Corrupted (Bad CRC)"
          value={primary.board.bad_crc + primary.bad_crc_back}
          unit="errors"
          subtitle={`Uplink: ${primary.board.bad_crc} · Downlink: ${primary.bad_crc_back}`}
          origin="recorded"
          accent="emerald"
        />
      </div>

      {/* Controlled Skip Test Before vs After Fix */}
      <SectionCard
        title={`Controlled Packet-Loss Experiment — skip=(${before.skip_packets.join(', ')})`}
        subtitle="Demonstrating why sequence-gap sample alignment is essential for accurate frame timestamps"
        origin="recorded"
      >
        <div className="grid gap-4 md:grid-cols-2">
          <div className="rounded-lg border border-rose-500/30 bg-rose-950/15 p-4 text-xs">
            <div className="flex items-center justify-between">
              <span className="font-semibold text-rose-300">Before Firmware Gap Fix</span>
              <span className="rounded bg-rose-500/20 px-2 py-0.5 font-mono text-[11px] text-rose-200">
                tail_shift = {before.tail_shift_samples} samples
              </span>
            </div>
            <div className="mt-3 grid grid-cols-2 gap-2 font-mono text-[11px] text-slate-300">
              <span>Packets sent: {before.packets_sent} / {before.expected_total_packets}</span>
              <span>Seq gaps detected: {before.board.seq_gaps}</span>
              <span>Board samples: {before.board.samples.toLocaleString()}</span>
              <span>Features recv: {before.received_features} (lost {before.lost_features})</span>
            </div>
            <p className="mt-3 text-[11px] text-slate-300">
              Last 5 <code className="text-rose-200">first_sample</code> values:{' '}
              <span className="font-mono text-rose-200">{before.last_5_first_samples.join(', ')}</span>
            </p>
            <p className="mt-1 text-[11px] text-slate-400">
              Without zero-filling missing gaps, subsequent audio shifted backward by 3 packets (960 samples), causing
              every downstream feature timestamp to misalign with clip labels.
            </p>
          </div>

          <div className="rounded-lg border border-emerald-500/30 bg-emerald-950/15 p-4 text-xs">
            <div className="flex items-center justify-between">
              <span className="font-semibold text-emerald-300">After Firmware Gap Fix</span>
              <span className="rounded bg-emerald-500/20 px-2 py-0.5 font-mono text-[11px] text-emerald-200">
                samples = {after.board.samples.toLocaleString()} (aligned)
              </span>
            </div>
            <div className="mt-3 grid grid-cols-2 gap-2 font-mono text-[11px] text-slate-300">
              <span>Packets sent: {after.packets_sent} / {after.expected_total_packets}</span>
              <span>Seq gaps detected: {after.board.seq_gaps}</span>
              <span>Board samples: {after.board.samples.toLocaleString()}</span>
              <span>Features recv: {after.received_features} (lost {after.lost_features})</span>
            </div>
            <p className="mt-3 text-[11px] text-slate-300">
              Last 5 <code className="text-emerald-200">first_sample</code> values:{' '}
              <span className="font-mono text-emerald-200">{after.last_5_first_samples.join(', ')}</span>
            </p>
            <p className="mt-1 text-[11px] text-slate-400">
              Gap-aligned firmware preserves the exact 160,000-sample timeline and drops the 5 overlapping frames
              touching missing packets (3 + 2 frames across the 2 gaps), keeping all remaining 494 frames aligned.
            </p>
          </div>
        </div>
      </SectionCard>

      {/* Speed Ramp Charts */}
      <div className="grid gap-6 lg:grid-cols-2">
        <SectionCard
          title="Lost Features vs Stream Speed (USB COM11 vs UART COM12)"
          subtitle="COM11 USB overflows 32 KB RX buffer at >= 8x; COM12 UART drops 0 frames due to TX backpressure"
          origin="recorded"
        >
          <LineChart
            series={[
              { name: 'USB COM11 (feat=True)', color: '#f43f5e', points: rampSeries.usbLoss },
              { name: 'UART COM12 (921.6k)', color: '#22d3ee', points: rampSeries.com921Loss },
              { name: 'UART COM12 (2M)', color: '#34d399', points: rampSeries.com2MLoss, dashed: true },
            ]}
            xLabel="Playback Speed"
            xUnit="×"
            yLabel="Lost Features"
            yUnit="frames"
            xFormatter={(v) => `${v}×`}
            yFormatter={(v) => String(Math.round(v))}
          />
        </SectionCard>

        <SectionCard
          title="COM12 Max Pipeline Lag vs Stream Speed"
          subtitle="Backpressure preserves 0% byte loss on UART while queuing latency rises above 2.5× (921.6k) or 6× (2M)"
          origin="recorded"
        >
          <LineChart
            series={[
              { name: 'COM12 @ 921,600 baud', color: '#fbbf24', points: rampSeries.lag921 },
              { name: 'COM12 @ 2,000,000 baud', color: '#34d399', points: rampSeries.lag2M },
            ]}
            xLabel="Playback Speed"
            xUnit="×"
            yLabel="Max Lag"
            yUnit="s"
            xFormatter={(v) => `${v}×`}
            yFormatter={(v) => v.toFixed(3)}
          />
        </SectionCard>
      </div>
    </div>
  );
}

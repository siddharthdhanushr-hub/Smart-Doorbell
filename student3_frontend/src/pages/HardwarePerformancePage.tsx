import type { DashboardBundle } from '../types/dashboard';
import { BarChart } from '../components/charts/BarChart';
import { KpiCard } from '../components/ui/KpiCard';
import { SectionCard } from '../components/ui/SectionCard';

export function HardwarePerformancePage({ bundle }: { bundle: DashboardBundle }) {
  const m2 = bundle.mission2;
  const m3 = bundle.mission3;
  const hw = bundle.configs.hardware;

  const sqnrSummary = m2.python_audio_analysis.sqnr.all_144_clips_summary;
  const sqnrLabels = Object.keys(sqnrSummary);
  const aliasing = m2.python_audio_analysis.aliasing;

  const speedup = Math.round(m3.starter_10s.compute_us.mean / m3.optimized.mel40_10s_realtime.compute_us.mean);
  const dutyCyclePct = (m3.optimized.mel40_10s_realtime.compute_us.mean / 20000) * 100;

  return (
    <div className="space-y-6">
      {/* Top Compute & Memory KPIs */}
      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <KpiCard
          title="Radix-2 FFT Speedup"
          value={`${speedup.toLocaleString()}×`}
          subtitle={`Starter DFT: ${(m3.starter_10s.compute_us.mean / 1000).toFixed(1)} ms → Optimized: ${m3.optimized.mel40_10s_realtime.compute_us.mean.toFixed(2)} us`}
          origin="recorded"
          accent="emerald"
        />
        <KpiCard
          title="CPU Duty Cycle (20 ms hop)"
          value={dutyCyclePct.toFixed(2)}
          unit="%"
          subtitle={`MFCC-13 (25/10 ms): ${m3.optimized.mfcc13_25ms_10ms_10s_realtime.compute_us.mean.toFixed(2)} us/frame`}
          origin="recorded"
          accent="cyan"
        />
        <KpiCard
          title="144-Clip Flash Persistence"
          value={m2.verify_power_cut.flash_exact_byte_match ? 'EXACT MATCH' : 'FAILED'}
          subtitle={`4,608,000 B · CRC ${m2.verify_power_cut.flash_crc_hex} survived unplug/replug`}
          origin="recorded"
          accent="emerald"
        />
        <KpiCard
          title="Anti-Aliasing Suppression"
          value={aliasing.attenuation_db.toFixed(2)}
          unit="dB"
          subtitle={`7,348 Hz whine aliases to ${aliasing.peak_8khz_no_aa_hz} Hz at 8 kHz without AA`}
          origin="recorded"
          accent="amber"
        />
      </div>

      {/* SQNR + Compute Time Charts */}
      <div className="grid gap-6 lg:grid-cols-2">
        <SectionCard
          title="Quantisation SQNR across all 144 Clips (Mission 2)"
          subtitle="int16 S=1.0 achieves 74.21 dB mean SQNR with 0% clipping; int8 S=0.25 clips loud speech peaks"
          origin="recorded"
        >
          <BarChart
            categories={sqnrLabels}
            series={[
              {
                name: 'Mean SQNR',
                color: '#22d3ee',
                values: sqnrLabels.map((k) => sqnrSummary[k].mean_sqnr_db),
              },
              {
                name: 'Min SQNR',
                color: '#f59e0b',
                values: sqnrLabels.map((k) => sqnrSummary[k].min_sqnr_db),
              },
            ]}
            yLabel="SQNR"
            yUnit="dB"
            valueFormatter={(v) => v.toFixed(2)}
          />
        </SectionCard>

        <SectionCard
          title="On-Device Log-Mel Processing Time (Mission 3)"
          subtitle="Optimized Radix-2 FFT + twiddle LUT + sparse Mel (note log scale gap: 1,863 ms vs 0.68 ms)"
          origin="recorded"
        >
          <BarChart
            categories={['Starter DFT (10s)', 'Optimized Mel-40', 'Optimized MFCC-13']}
            series={[
              {
                name: 'Mean Compute Time (ms)',
                color: '#34d399',
                values: [
                  m3.starter_10s.compute_us.mean / 1000,
                  m3.optimized.mel40_10s_realtime.compute_us.mean / 1000,
                  m3.optimized.mfcc13_25ms_10ms_10s_realtime.compute_us.mean / 1000,
                ],
              },
            ]}
            yLabel="Compute Latency"
            yUnit="ms"
            valueFormatter={(v) => (v < 10 ? v.toFixed(3) : v.toFixed(1))}
          />
        </SectionCard>
      </div>

      {/* Storage & Persistence Table + Memory Usage */}
      <div className="grid gap-6 lg:grid-cols-2">
        <SectionCard
          title="Audio Storage & Power-Cut Persistence Tests"
          subtitle="Full 144-clip corpus requires 4,608,000 bytes (16 kHz, int16, 144 s)"
          origin="recorded"
        >
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead>
                <tr className="border-b border-slate-800 text-slate-400">
                  <th className="py-2 pr-3">Tier</th>
                  <th className="py-2 pr-3 font-mono">Capacity</th>
                  <th className="py-2 pr-3">144-Clip Fit</th>
                  <th className="py-2">Power-Cut Persistence</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60">
                <tr>
                  <td className="py-2.5 pr-3 font-medium text-slate-200">Internal SRAM</td>
                  <td className="py-2.5 pr-3 font-mono text-slate-300">
                    {m2.probe_baseline.sram_max_bytes.toLocaleString()} B max
                  </td>
                  <td className="py-2.5 pr-3 text-rose-300">
                    No ({m2.probe_baseline.sram_max_seconds_16khz_i16} s max)
                  </td>
                  <td className="py-2.5 text-slate-400">Volatile</td>
                </tr>
                <tr>
                  <td className="py-2.5 pr-3 font-medium text-slate-200">OPI PSRAM</td>
                  <td className="py-2.5 pr-3 font-mono text-slate-300">
                    {hw.board_info_measured.mission2_opi_16m.psram_size.toLocaleString()} B (8 MiB)
                  </td>
                  <td className="py-2.5 pr-3 text-emerald-300">
                    Yes ({m2.save144.psram_exact_match ? 'CRC match' : 'Mismatch'})
                  </td>
                  <td className="py-2.5 text-amber-300">
                    Wiped (0 B after replug)
                  </td>
                </tr>
                <tr>
                  <td className="py-2.5 pr-3 font-medium text-slate-200">LittleFS Flash (/rec.bin)</td>
                  <td className="py-2.5 pr-3 font-mono text-slate-300">
                    {hw.board_info_measured.mission2_opi_16m.fs_total.toLocaleString()} B (6.88 MiB)
                  </td>
                  <td className="py-2.5 pr-3 text-emerald-300">
                    Yes (SAVE in {(m2.save144.save_reply.us / 1e6).toFixed(2)} s)
                  </td>
                  <td className="py-2.5 font-mono text-emerald-300">
                    CRC {m2.verify_power_cut.flash_crc_hex} (100% match)
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </SectionCard>

        <SectionCard
          title="Sampling & Aliasing + ESP32 Memory Footprint"
          subtitle="Room whine aliasing analysis (clip #120) and internal SRAM allocation"
          origin="recorded"
        >
          <div className="space-y-3 text-xs">
            <div className="rounded-lg border border-slate-800 bg-slate-950/70 p-3">
              <p className="font-semibold text-cyan-300">8 kHz Aliasing Proof (Clip #{aliasing.silence_clip_id})</p>
              <div className="mt-2 grid grid-cols-2 gap-2 font-mono text-[11px] text-slate-300">
                <span>48 kHz true tone: {aliasing.peak_48khz_hz} Hz ({aliasing.peak_48khz_db} dB)</span>
                <span>8 kHz no-AA alias: {aliasing.peak_8khz_no_aa_hz} Hz ({aliasing.peak_8khz_no_aa_db} dB)</span>
                <span>8 kHz with AA: {aliasing.level_8khz_with_aa_at_alias_db} dB</span>
                <span className="text-emerald-300">Attenuation: {aliasing.attenuation_db} dB</span>
              </div>
            </div>

            <div className="rounded-lg border border-slate-800 bg-slate-950/70 p-3">
              <p className="font-semibold text-emerald-300">ESP32-S3 Memory & Runtime Footprint</p>
              <div className="mt-2 grid grid-cols-2 gap-2 font-mono text-[11px] text-slate-300">
                <span>Free internal SRAM: {hw.board_info_measured.mission2_opi_16m.heap_free.toLocaleString()} B</span>
                <span>Feature extractor heap: ~53,636 B (18.6%)</span>
                <span>OPI PSRAM free (idle): {hw.board_info_measured.mission2_opi_16m.psram_free.toLocaleString()} B</span>
                <span>LittleFS used (/rec.bin): {hw.board_info_measured.mission2_opi_16m.fs_used_after_save144.toLocaleString()} B</span>
              </div>
            </div>
          </div>
        </SectionCard>
      </div>
    </div>
  );
}

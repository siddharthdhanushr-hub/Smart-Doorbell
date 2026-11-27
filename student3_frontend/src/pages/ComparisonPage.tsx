import { useState } from 'react';
import { MOCK_STUDENT4_FEATURE_COMPARISON } from '../data/mock/mockGenerators';
import type { DashboardBundle, Student4FeatureComparison } from '../types/dashboard';
import { BarChart } from '../components/charts/BarChart';
import { EmptyAwaitingCard } from '../components/ui/EmptyAwaitingCard';
import { SectionCard } from '../components/ui/SectionCard';

export function ComparisonPage({ bundle }: { bundle: DashboardBundle }) {
  const [previewMock, setPreviewMock] = useState(false);

  const runs = bundle.mission45.all_144_runs.runs;
  const s4Real: Student4FeatureComparison | null = bundle.student4.featureComparison;
  const s4Data: Student4FeatureComparison | null = s4Real ?? (previewMock ? MOCK_STUDENT4_FEATURE_COMPARISON : null);
  const s4Origin = s4Real ? 'recorded' : previewMock ? 'mock' : 'awaiting';

  const settingKeys = s4Data ? Object.keys(s4Data) : [];
  const firstSetting = settingKeys[0];
  const bandMae = firstSetting && s4Data ? s4Data[firstSetting].per_band_mae_db : [];
  const classLabels = firstSetting && s4Data ? Object.keys(s4Data[firstSetting].per_class_mae_db) : [];

  return (
    <div className="space-y-6">
      {/* Verified Hardware vs Python Reference Summary (Already in phase5_144clips_all_runs.json) */}
      <SectionCard
        title="ESP32-S3 vs Laptop Python Reference — Recorded 144-Clip Parity"
        subtitle="Comparing board output against both quantised NumPy (isolating FFT math error) and original float32 NumPy (total codec + math error)"
        origin="recorded"
      >
        <div className="grid gap-6 lg:grid-cols-2">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead>
                <tr className="border-b border-slate-800 text-slate-400">
                  <th className="py-2 pr-3">Setting Tag</th>
                  <th className="py-2 pr-3 font-mono">MAE vs Quant NumPy</th>
                  <th className="py-2 pr-3 font-mono">MAE vs Orig f32</th>
                  <th className="py-2 pr-3 font-mono">Max Diff (f32)</th>
                  <th className="py-2 font-mono">RMSE</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60 font-mono">
                {runs.map((r) => {
                  const s4Row = s4Data?.[r.tag];
                  return (
                    <tr key={r.tag}>
                      <td className="py-2.5 pr-3 font-sans font-medium text-slate-200">{r.tag}</td>
                      <td className="py-2.5 pr-3 text-emerald-300">{r.mae_vs_quantised_numpy_db.toFixed(6)} dB</td>
                      <td className="py-2.5 pr-3 text-cyan-300">{r.mae_vs_orig_f32_numpy_db.toFixed(6)} dB</td>
                      <td className="py-2.5 pr-3 text-amber-300">{r.max_diff_vs_orig_f32_numpy_db.toFixed(4)} dB</td>
                      <td className="py-2.5 text-slate-300">
                        {s4Row ? `${s4Row.rmse_db.toFixed(4)} dB` : <span className="text-slate-500">N/A (Student 4)</span>}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>

          <BarChart
            categories={runs.map((r) => r.tag)}
            series={[
              {
                name: 'MAE vs Orig float32 (dB)',
                color: '#22d3ee',
                values: runs.map((r) => r.mae_vs_orig_f32_numpy_db),
              },
              {
                name: 'MAE vs Quantised NumPy (dB)',
                color: '#34d399',
                values: runs.map((r) => r.mae_vs_quantised_numpy_db),
              },
            ]}
            yLabel="Mean Absolute Error"
            yUnit="dB"
            valueFormatter={(v) => v.toFixed(4)}
          />
        </div>
      </SectionCard>

      {/* Student 4 Full Comparison Integration (MSE / RMSE / Per-band / Per-class) */}
      <SectionCard
        title="Full Student 4 Feature Comparison (MSE, RMSE, Per-Band & Per-Class)"
        subtitle="Consumes student4_validation/outputs/mission5_feature_comparison.json (includes 8 kHz AA vs No-AA reference)"
        origin={s4Origin}
        headerRight={
          !s4Real ? (
            <button
              type="button"
              onClick={() => setPreviewMock(!previewMock)}
              className="rounded-lg border border-amber-500/40 bg-amber-500/10 px-3 py-1 text-xs font-medium text-amber-200 hover:bg-amber-500/20"
            >
              {previewMock ? 'Hide Mock Preview' : 'Preview Mock Student 4 Data'}
            </button>
          ) : null
        }
      >
        {!s4Data ? (
          <EmptyAwaitingCard
            title="Awaiting Student 4 Feature Comparison Output"
            description="Student 4 will publish full MAE, MSE, RMSE, per-band (40), per-class (6), and 8 kHz antialias=True baseline comparisons into student4_validation/outputs/. Missing metrics are never shown as zero."
            expectedFiles={['student4_validation/outputs/mission5_feature_comparison.json']}
            actionLabel="Preview Mock Layout"
            onAction={() => setPreviewMock(true)}
          />
        ) : (
          <div className="space-y-6">
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead>
                  <tr className="border-b border-slate-800 text-slate-400">
                    <th className="py-2 pr-3">Setting</th>
                    <th className="py-2 pr-3 font-mono">MAE (dB)</th>
                    <th className="py-2 pr-3 font-mono">MSE (dB²)</th>
                    <th className="py-2 pr-3 font-mono">RMSE (dB)</th>
                    <th className="py-2 font-mono">Max Abs (dB)</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/60 font-mono">
                  {settingKeys.map((k) => {
                    const row = s4Data[k];
                    return (
                      <tr key={k}>
                        <td className="py-2.5 pr-3 font-sans font-medium text-slate-200">{k}</td>
                        <td className="py-2.5 pr-3 text-cyan-300">{row.mae_db.toFixed(6)}</td>
                        <td className="py-2.5 pr-3 text-slate-300">{row.mse_db2.toFixed(6)}</td>
                        <td className="py-2.5 pr-3 text-emerald-300">{row.rmse_db.toFixed(6)}</td>
                        <td className="py-2.5 text-amber-300">{row.max_abs_db.toFixed(4)}</td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>

            <div className="grid gap-6 lg:grid-cols-2">
              <BarChart
                categories={classLabels}
                series={settingKeys.map((k, idx) => ({
                  name: k,
                  color: ['#34d399', '#22d3ee', '#fbbf24', '#f43f5e'][idx % 4],
                  values: classLabels.map((c) => s4Data[k].per_class_mae_db[c] ?? null),
                }))}
                yLabel="Per-Class MAE"
                yUnit="dB"
                valueFormatter={(v) => v.toFixed(3)}
              />

              <BarChart
                categories={bandMae.map((_, i) => `B${i}`)}
                series={settingKeys
                  .filter((k) => k === '8k_i16_S1.0_noaa' || k === '16k_i8_S1.0')
                  .map((k, idx) => ({
                    name: `${k} per-band MAE`,
                    color: idx === 0 ? '#f43f5e' : '#22d3ee',
                    values: s4Data[k].per_band_mae_db,
                  }))}
                yLabel="Per-Band MAE"
                yUnit="dB"
                valueFormatter={(v) => v.toFixed(2)}
              />
            </div>
          </div>
        )}
      </SectionCard>
    </div>
  );
}

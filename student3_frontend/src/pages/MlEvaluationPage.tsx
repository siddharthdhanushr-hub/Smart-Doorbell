import { useState } from 'react';
import { MOCK_STUDENT4_CLASSIFIER_RESULTS } from '../data/mock/mockGenerators';
import type { DashboardBundle, Student4ClassifierResults } from '../types/dashboard';
import { BarChart } from '../components/charts/BarChart';
import { ConfusionMatrix } from '../components/charts/ConfusionMatrix';
import { EmptyAwaitingCard } from '../components/ui/EmptyAwaitingCard';
import { KpiCard } from '../components/ui/KpiCard';
import { SectionCard } from '../components/ui/SectionCard';

export function MlEvaluationPage({ bundle }: { bundle: DashboardBundle }) {
  const [previewMock, setPreviewMock] = useState(false);
  const [selectedEvalIdx, setSelectedEvalIdx] = useState(1);

  const realResults: Student4ClassifierResults | null = bundle.student4.classifierResults;
  const activeResults: Student4ClassifierResults | null =
    realResults ?? (previewMock ? MOCK_STUDENT4_CLASSIFIER_RESULTS : null);

  const origin = realResults ? 'recorded' : previewMock ? 'mock' : 'awaiting';
  const evalList = activeResults?.evaluations ?? [];
  const selectedEval = evalList[selectedEvalIdx] ?? evalList[0];

  return (
    <div className="space-y-6">
      <SectionCard
        title="Nearest-Centroid Classifier Evaluation (Mission 5)"
        subtitle="Leakage-free stratified clip-level split (96 train / 48 test clips) over 80-dim clip features (mean + std across 49 frames)"
        origin={origin}
        headerRight={
          !realResults ? (
            <button
              type="button"
              onClick={() => setPreviewMock(!previewMock)}
              className="rounded-lg border border-amber-500/40 bg-amber-500/10 px-3 py-1 text-xs font-medium text-amber-200 hover:bg-amber-500/20"
            >
              {previewMock ? 'Exit Mock Preview' : 'Preview with Mock Data (Simulated)'}
            </button>
          ) : null
        }
      >
        {!activeResults ? (
          <EmptyAwaitingCard
            title="Awaiting Student 4 ML Evaluation Results"
            description="Student 4 has not yet committed mission5_classifier_results.json into student4_validation/outputs/. Per dashboard integrity rules, missing accuracy, precision, recall, F1, and confusion-matrix entries are never fabricated or shown as zero. You can preview the interactive layout using clearly badged simulated mock data."
            expectedFiles={['student4_validation/outputs/mission5_classifier_results.json']}
            actionLabel="Preview Mock ML Results"
            onAction={() => setPreviewMock(true)}
          />
        ) : (
          <div className="space-y-6">
            {/* Metric Cards for Selected Setting */}
            <div className="flex flex-wrap items-center justify-between gap-3 rounded-lg border border-slate-800 bg-slate-950/60 p-3">
              <div className="text-xs text-slate-300">
                Split: <span className="font-mono text-cyan-300">{activeResults.split.method}</span> ·{' '}
                {activeResults.split.train_clips} train / {activeResults.split.test_clips} test clips (seed{' '}
                {activeResults.split.random_seed})
              </div>
              <select
                value={selectedEvalIdx}
                onChange={(e) => setSelectedEvalIdx(Number(e.target.value))}
                className="rounded-lg border border-slate-700 bg-slate-950 px-3 py-1.5 text-xs text-slate-100"
              >
                {evalList.map((ev, idx) => (
                  <option key={ev.setting} value={idx}>
                    {ev.setting}
                  </option>
                ))}
              </select>
            </div>

            {selectedEval ? (
              <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
                <KpiCard
                  title="Accuracy"
                  value={(selectedEval.accuracy * 100).toFixed(2)}
                  unit="%"
                  subtitle={selectedEval.setting}
                  origin={origin}
                  accent="emerald"
                />
                <KpiCard
                  title="Macro Precision"
                  value={(selectedEval.precision_macro * 100).toFixed(2)}
                  unit="%"
                  subtitle="Across 6 command classes"
                  origin={origin}
                  accent="cyan"
                />
                <KpiCard
                  title="Macro Recall"
                  value={(selectedEval.recall_macro * 100).toFixed(2)}
                  unit="%"
                  subtitle="Balanced 8 test clips/class"
                  origin={origin}
                  accent="cyan"
                />
                <KpiCard
                  title="Macro F1-Score"
                  value={(selectedEval.f1_macro * 100).toFixed(2)}
                  unit="%"
                  subtitle="Clip-level nearest centroid"
                  origin={origin}
                  accent="amber"
                />
              </div>
            ) : null}

            {/* Comparison Bar Chart + Confusion Matrix */}
            <div className="grid gap-6 lg:grid-cols-2">
              <div className="rounded-lg border border-slate-800 bg-slate-950/50 p-4">
                <h3 className="mb-3 text-sm font-semibold text-slate-100">Accuracy & F1 Across Settings</h3>
                <BarChart
                  categories={evalList.map((e) => e.setting.replace('ESP32 ', ''))}
                  series={[
                    { name: 'Accuracy (%)', color: '#34d399', values: evalList.map((e) => e.accuracy * 100) },
                    { name: 'Macro F1 (%)', color: '#22d3ee', values: evalList.map((e) => e.f1_macro * 100) },
                  ]}
                  yLabel="Score"
                  yUnit="%"
                  valueFormatter={(v) => v.toFixed(1)}
                />
              </div>

              <div className="rounded-lg border border-slate-800 bg-slate-950/50 p-4">
                {selectedEval ? (
                  <ConfusionMatrix
                    classes={activeResults.classes}
                    matrix={selectedEval.confusion_matrix}
                    title={`Confusion Matrix — ${selectedEval.setting} (48 test clips)`}
                  />
                ) : null}
              </div>
            </div>
          </div>
        )}
      </SectionCard>
    </div>
  );
}

import { useMemo, useState } from 'react';
import type { DashboardBundle } from '../types/dashboard';
import { BarChart } from '../components/charts/BarChart';
import { KpiCard } from '../components/ui/KpiCard';
import { SectionCard } from '../components/ui/SectionCard';

function formatNumOrNA(val: string | number | undefined | null, digits: number): string {
  if (val === undefined || val === null || String(val).trim() === '') return 'N/A';
  const n = Number(val);
  return Number.isFinite(n) ? n.toFixed(digits) : 'N/A';
}

export function DatasetPage({ bundle }: { bundle: DashboardBundle }) {
  const [search, setSearch] = useState('');
  const [classFilter, setClassFilter] = useState('ALL');

  const val = bundle.dataset.validation;
  const manifest = bundle.dataset.manifest;
  const classes = Object.keys(val.class_distribution);
  const s4Dataset = bundle.student4.validationSummary?.dataset;

  const filtered = useMemo(() => {
    const q = search.trim().toLowerCase();
    return manifest.filter((r) => {
      if (classFilter !== 'ALL' && r.label !== classFilter) return false;
      if (!q) return true;
      return (
        String(r.clip_id).includes(q) ||
        r.label.toLowerCase().includes(q) ||
        String(r.pool_voice).toLowerCase().includes(q) ||
        String(r.pool_word).toLowerCase().includes(q)
      );
    });
  }, [manifest, search, classFilter]);

  return (
    <div className="space-y-6">
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <KpiCard
          title="Total Audio Recordings"
          value={val.total_clips}
          unit="clips"
          subtitle={`${val.valid_clips}/${val.expected_clips} validated · ${val.invalid_clip_ids.length} invalid`}
          origin="recorded"
          accent="cyan"
        />
        <KpiCard
          title="Clean ESP32 Dataset"
          value={(s4Dataset?.clean_frames ?? 7056).toLocaleString()}
          unit="frames"
          subtitle={`49 frames/clip × ${val.total_clips} clips (${s4Dataset?.excluded_straddling_frames ?? 143} straddling frames excluded)`}
          origin="recorded"
          accent="emerald"
        />
        <KpiCard
          title="Pool Duplicates"
          value={val.duplicate_non_silence_pool_recordings}
          unit="dups"
          subtitle={`Drawn from ${val.speech_pool_total_recordings}-clip speech pool`}
          origin="recorded"
          accent="emerald"
        />
        <KpiCard
          title="Team 1 Room Whine / Hum"
          value={`${val.team_room_parameters.whine.toFixed(1)} Hz`}
          subtitle={`Hum: ${val.team_room_parameters.hum} Hz · Noise std: ${val.team_room_parameters.noise.toFixed(5)}`}
          origin="recorded"
          accent="amber"
        />
      </div>

      {/* Class Distribution + Data Card */}
      <div className="grid gap-6 lg:grid-cols-2">
        <SectionCard
          title="Class Distribution (Clips & Clean Frames)"
          subtitle="Perfectly balanced across 6 classes (24 clips / 1,176 frames per class)"
          origin="recorded"
        >
          <BarChart
            categories={classes}
            series={[
              {
                name: 'Clips per Class',
                color: '#22d3ee',
                values: classes.map((c) => val.class_distribution[c]),
              },
            ]}
            yLabel="Recordings"
            yUnit="clips"
            valueFormatter={(v) => String(Math.round(v))}
          />
        </SectionCard>

        <SectionCard
          title="Dataset Data-Card Summary"
          subtitle="From dataset/data_card.md — provenance, leakage prevention & scope"
          origin="recorded"
        >
          <pre className="max-h-72 overflow-y-auto whitespace-pre-wrap rounded-lg border border-slate-800 bg-slate-950 p-3 font-mono text-[11px] leading-relaxed text-slate-300">
            {bundle.dataset.data_card_md ?? 'data_card.md not found.'}
          </pre>
        </SectionCard>
      </div>

      {/* Searchable Manifest Table */}
      <SectionCard
        title="Dataset Manifest Explorer"
        subtitle={`Showing ${filtered.length} of ${manifest.length} clips`}
        origin="recorded"
        headerRight={
          <div className="flex flex-wrap items-center gap-2">
            <select
              aria-label="Filter manifest by class"
              value={classFilter}
              onChange={(e) => setClassFilter(e.target.value)}
              className="rounded-lg border border-slate-700 bg-slate-950 px-2.5 py-1 text-xs text-slate-100"
            >
              <option value="ALL">All classes</option>
              {classes.map((c) => (
                <option key={c} value={c}>
                  {c}
                </option>
              ))}
            </select>
            <input
              type="text"
              aria-label="Search manifest by clip ID or voice"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search clip ID or voice..."
              className="rounded-lg border border-slate-700 bg-slate-950 px-2.5 py-1 text-xs text-slate-100 placeholder:text-slate-500"
            />
          </div>
        }
      >
        <div className="max-h-80 overflow-auto">
          <table className="w-full text-left text-xs">
            <thead className="sticky top-0 bg-slate-900">
              <tr className="border-b border-slate-800 text-slate-400">
                <th className="py-2 pr-3 font-mono">ID</th>
                <th className="py-2 pr-3">Label</th>
                <th className="py-2 pr-3">Pool Word</th>
                <th className="py-2 pr-3">Voice</th>
                <th className="py-2 pr-3 font-mono">Peak Abs</th>
                <th className="py-2 pr-3 font-mono">RMS</th>
                <th className="py-2">Valid</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/50">
              {filtered.map((r) => (
                <tr key={String(r.clip_id)} className="hover:bg-slate-800/30">
                  <td className="py-1.5 pr-3 font-mono text-cyan-300">#{r.clip_id}</td>
                  <td className="py-1.5 pr-3 font-medium text-slate-100">{r.label}</td>
                  <td className="py-1.5 pr-3 font-mono text-slate-300">{r.pool_word}</td>
                  <td className="py-1.5 pr-3 text-slate-400">{r.pool_voice}</td>
                  <td className="py-1.5 pr-3 font-mono text-slate-300">{formatNumOrNA(r.peak_abs, 4)}</td>
                  <td className="py-1.5 pr-3 font-mono text-slate-300">{formatNumOrNA(r.rms, 4)}</td>
                  <td className="py-1.5 text-emerald-300">{r.valid}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </SectionCard>
    </div>
  );
}

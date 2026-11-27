import { useState } from 'react';

export interface BarSeries {
  name: string;
  color: string;
  values: (number | null)[];
}

interface BarChartProps {
  categories: string[];
  series: BarSeries[];
  yLabel: string;
  yUnit?: string;
  height?: number;
  valueFormatter?: (v: number) => string;
}

export function BarChart({
  categories,
  series,
  yLabel,
  yUnit = '',
  height = 250,
  valueFormatter = (v) => v.toFixed(1),
}: BarChartProps) {
  const [hover, setHover] = useState<{ catIdx: number; seriesIdx: number } | null>(null);

  const width = 680;
  const padLeft = 64;
  const padRight = 18;
  const padTop = 20;
  const padBottom = 46;
  const plotW = width - padLeft - padRight;
  const plotH = height - padTop - padBottom;

  const allVals = series.flatMap((s) => s.values.filter((v): v is number => v !== null && Number.isFinite(v)));
  const maxVal = Math.max(1e-6, ...allVals);
  const yMax = maxVal * 1.12;
  const ticks = 5;

  const groupW = plotW / Math.max(1, categories.length);
  const barGap = 4;
  const innerW = Math.max(8, groupW - 14);
  const barW = Math.max(6, (innerW - barGap * (series.length - 1)) / Math.max(1, series.length));

  return (
    <div className="w-full">
      <div className="mb-2 flex flex-wrap items-center justify-between gap-2 text-xs text-slate-400">
        <span>
          Y-axis: <strong className="text-slate-200">{yLabel}</strong>
          {yUnit ? ` (${yUnit})` : ''}
        </span>
        <div className="flex flex-wrap items-center gap-3">
          {series.map((s) => (
            <span key={s.name} className="inline-flex items-center gap-1.5">
              <span className="h-2.5 w-2.5 rounded-sm" style={{ backgroundColor: s.color }} />
              <span className="text-slate-300">{s.name}</span>
            </span>
          ))}
        </div>
      </div>

      <div className="relative w-full overflow-x-auto">
        <svg viewBox={`0 0 ${width} ${height}`} className="h-auto w-full min-w-[460px]">
          {/* Gridlines & Y-ticks */}
          {Array.from({ length: ticks + 1 }, (_, i) => {
            const frac = i / ticks;
            const y = padTop + plotH * (1 - frac);
            const val = yMax * frac;
            return (
              <g key={i}>
                <line x1={padLeft} y1={y} x2={width - padRight} y2={y} stroke="#1e293b" strokeDasharray="3 3" />
                <text x={padLeft - 8} y={y + 4} textAnchor="end" fill="#94a3b8" fontSize="10" fontFamily="monospace">
                  {val >= 1000 ? `${(val / 1000).toFixed(1)}k` : val >= 10 ? val.toFixed(0) : val.toFixed(2)}
                </text>
              </g>
            );
          })}

          {/* Axes */}
          <line x1={padLeft} y1={padTop} x2={padLeft} y2={padTop + plotH} stroke="#475569" />
          <line x1={padLeft} y1={padTop + plotH} x2={width - padRight} y2={padTop + plotH} stroke="#475569" />

          {/* Bars */}
          {categories.map((cat, ci) => {
            const gx = padLeft + ci * groupW + (groupW - (series.length * barW + (series.length - 1) * barGap)) / 2;
            return (
              <g key={cat}>
                {series.map((s, si) => {
                  const val = s.values[ci];
                  const bx = gx + si * (barW + barGap);
                  if (val === null || val === undefined || !Number.isFinite(val)) {
                    return null;
                  }
                  const bh = Math.max(1, (val / yMax) * plotH);
                  const by = padTop + plotH - bh;
                  const isHovered = hover?.catIdx === ci && hover?.seriesIdx === si;
                  return (
                    <rect
                      key={s.name}
                      x={bx}
                      y={by}
                      width={barW}
                      height={bh}
                      rx={2}
                      fill={s.color}
                      opacity={hover && !isHovered ? 0.6 : 0.95}
                      onMouseEnter={() => setHover({ catIdx: ci, seriesIdx: si })}
                      onMouseLeave={() => setHover(null)}
                      className="cursor-pointer"
                    />
                  );
                })}
                <text
                  x={padLeft + ci * groupW + groupW / 2}
                  y={padTop + plotH + 16}
                  textAnchor="middle"
                  fill="#cbd5e1"
                  fontSize="10"
                >
                  {cat}
                </text>
              </g>
            );
          })}
        </svg>

        {hover !== null ? (
          <div className="mt-1 rounded border border-slate-700 bg-slate-950/90 px-2.5 py-1 text-xs text-slate-200">
            <span className="font-semibold">{categories[hover.catIdx]}</span> ·{' '}
            <span>{series[hover.seriesIdx].name}: </span>
            <span className="font-mono text-cyan-300">
              {series[hover.seriesIdx].values[hover.catIdx] !== null
                ? `${valueFormatter(series[hover.seriesIdx].values[hover.catIdx] as number)}${yUnit ? ` ${yUnit}` : ''}`
                : 'N/A'}
            </span>
          </div>
        ) : null}
      </div>
    </div>
  );
}

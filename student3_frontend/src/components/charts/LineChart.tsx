import { useState } from 'react';

export interface LinePoint {
  x: number;
  y: number;
}

export interface LineSeries {
  name: string;
  color: string;
  points: LinePoint[];
  dashed?: boolean;
}

interface LineChartProps {
  series: LineSeries[];
  xLabel: string;
  xUnit?: string;
  yLabel: string;
  yUnit?: string;
  height?: number;
  xFormatter?: (v: number) => string;
  yFormatter?: (v: number) => string;
}

export function LineChart({
  series,
  xLabel,
  xUnit = '',
  yLabel,
  yUnit = '',
  height = 250,
  xFormatter = (v) => String(v),
  yFormatter = (v) => v.toFixed(2),
}: LineChartProps) {
  const [hovered, setHovered] = useState<{ seriesName: string; x: number; y: number } | null>(null);

  const width = 680;
  const padLeft = 64;
  const padRight = 22;
  const padTop = 18;
  const padBottom = 42;
  const plotW = width - padLeft - padRight;
  const plotH = height - padTop - padBottom;

  const allPts = series.flatMap((s) => s.points);
  const xs = allPts.map((p) => p.x);
  const ys = allPts.map((p) => p.y);
  const xMin = xs.length ? Math.min(...xs) : 0;
  const xMax = xs.length ? Math.max(...xs) : 1;
  const yMin = 0;
  const yMax = Math.max(1e-6, (ys.length ? Math.max(...ys) : 1) * 1.12);

  const mapX = (x: number) =>
    xMax === xMin ? padLeft + plotW / 2 : padLeft + ((x - xMin) / (xMax - xMin)) * plotW;
  const mapY = (y: number) => padTop + plotH - ((y - yMin) / (yMax - yMin)) * plotH;

  const uniqueXs = Array.from(new Set(xs)).sort((a, b) => a - b);

  return (
    <div className="w-full">
      <div className="mb-2 flex flex-wrap items-center justify-between gap-2 text-xs text-slate-400">
        <span>
          <strong className="text-slate-200">{yLabel}</strong> ({yUnit || 'value'}) vs{' '}
          <strong className="text-slate-200">{xLabel}</strong> ({xUnit || 'x'})
        </span>
        <div className="flex flex-wrap items-center gap-3">
          {series.map((s) => (
            <span key={s.name} className="inline-flex items-center gap-1.5">
              <span className="h-0.5 w-4" style={{ backgroundColor: s.color }} />
              <span className="text-slate-300">{s.name}</span>
            </span>
          ))}
        </div>
      </div>

      <div className="w-full overflow-x-auto">
        <svg viewBox={`0 0 ${width} ${height}`} className="h-auto w-full min-w-[460px]">
          {[0, 0.25, 0.5, 0.75, 1].map((frac) => {
            const y = padTop + plotH * (1 - frac);
            const val = yMin + (yMax - yMin) * frac;
            return (
              <g key={frac}>
                <line x1={padLeft} y1={y} x2={width - padRight} y2={y} stroke="#1e293b" strokeDasharray="3 3" />
                <text x={padLeft - 8} y={y + 4} textAnchor="end" fill="#94a3b8" fontSize="10" fontFamily="monospace">
                  {val >= 1000 ? `${(val / 1000).toFixed(1)}k` : yFormatter(val)}
                </text>
              </g>
            );
          })}

          {uniqueXs.map((xv) => {
            const x = mapX(xv);
            return (
              <g key={xv}>
                <line x1={x} y1={padTop} x2={x} y2={padTop + plotH} stroke="#0f172a" />
                <text x={x} y={padTop + plotH + 16} textAnchor="middle" fill="#cbd5e1" fontSize="10" fontFamily="monospace">
                  {xFormatter(xv)}
                </text>
              </g>
            );
          })}

          <line x1={padLeft} y1={padTop} x2={padLeft} y2={padTop + plotH} stroke="#475569" />
          <line x1={padLeft} y1={padTop + plotH} x2={width - padRight} y2={padTop + plotH} stroke="#475569" />

          {series.map((s) => {
            const sorted = [...s.points].sort((a, b) => a.x - b.x);
            const pathD = sorted
              .map((p, idx) => `${idx === 0 ? 'M' : 'L'} ${mapX(p.x).toFixed(2)} ${mapY(p.y).toFixed(2)}`)
              .join(' ');
            return (
              <g key={s.name}>
                {sorted.length > 1 ? (
                  <path
                    d={pathD}
                    fill="none"
                    stroke={s.color}
                    strokeWidth={2}
                    strokeDasharray={s.dashed ? '5 4' : undefined}
                  />
                ) : null}
                {sorted.map((p) => (
                  <circle
                    key={`${s.name}-${p.x}`}
                    cx={mapX(p.x)}
                    cy={mapY(p.y)}
                    r={4}
                    fill={s.color}
                    stroke="#020617"
                    strokeWidth={1.5}
                    className="cursor-pointer"
                    onMouseEnter={() => setHovered({ seriesName: s.name, x: p.x, y: p.y })}
                    onMouseLeave={() => setHovered(null)}
                  />
                ))}
              </g>
            );
          })}
        </svg>

        {hovered ? (
          <div className="mt-1 rounded border border-slate-700 bg-slate-950/90 px-2.5 py-1 text-xs text-slate-200">
            <span className="font-semibold">{hovered.seriesName}</span> · {xLabel}:{' '}
            <span className="font-mono text-cyan-300">
              {xFormatter(hovered.x)} {xUnit}
            </span>{' '}
            · {yLabel}:{' '}
            <span className="font-mono text-cyan-300">
              {yFormatter(hovered.y)} {yUnit}
            </span>
          </div>
        ) : null}
      </div>
    </div>
  );
}

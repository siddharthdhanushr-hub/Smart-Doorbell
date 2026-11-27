import { useEffect, useMemo, useRef, useState } from 'react';

interface SpectrogramCanvasProps {
  matrix: number[][]; // [frames][mels]
  title: string;
  unit?: string;
  minDb?: number;
  maxDb?: number;
  height?: number;
}

function colorForFraction(t: number): [number, number, number] {
  const c = Math.max(0, Math.min(1, t));
  // Dark slate -> indigo -> cyan -> amber -> bright yellow
  if (c < 0.25) {
    const k = c / 0.25;
    return [Math.round(12 + k * 28), Math.round(16 + k * 40), Math.round(45 + k * 90)];
  }
  if (c < 0.55) {
    const k = (c - 0.25) / 0.3;
    return [Math.round(40 - k * 20), Math.round(56 + k * 115), Math.round(135 + k * 50)];
  }
  if (c < 0.8) {
    const k = (c - 0.55) / 0.25;
    return [Math.round(20 + k * 215), Math.round(171 + k * 10), Math.round(185 - k * 145)];
  }
  const k = (c - 0.8) / 0.2;
  return [Math.round(235 + k * 20), Math.round(181 + k * 68), Math.round(40 + k * 110)];
}

export function SpectrogramCanvas({
  matrix,
  title,
  unit = 'dB',
  minDb,
  maxDb,
  height = 220,
}: SpectrogramCanvasProps) {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const [cellInfo, setCellInfo] = useState<{ frame: number; band: number; value: number } | null>(null);

  const { lo, hi, nFrames, nMels } = useMemo(() => {
    const f = matrix.length;
    const m = f > 0 ? matrix[0].length : 0;
    let mn = Infinity;
    let mx = -Infinity;
    for (let i = 0; i < f; i++) {
      for (let j = 0; j < m; j++) {
        const v = matrix[i][j];
        if (v < mn) mn = v;
        if (v > mx) mx = v;
      }
    }
    return {
      lo: minDb ?? (Number.isFinite(mn) ? mn : -60),
      hi: maxDb ?? (Number.isFinite(mx) ? mx : 0),
      nFrames: f,
      nMels: m,
    };
  }, [matrix, minDb, maxDb]);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas || nFrames === 0 || nMels === 0) return;

    const dpr = window.devicePixelRatio || 1;
    const width = canvas.clientWidth || 520;
    canvas.width = Math.floor(width * dpr);
    canvas.height = Math.floor(height * dpr);

    const ctx = canvas.getContext('2d');
    if (!ctx) return;
    ctx.scale(dpr, dpr);

    ctx.fillStyle = '#020617';
    ctx.fillRect(0, 0, width, height);

    const padLeft = 36;
    const padRight = 10;
    const padTop = 8;
    const padBottom = 22;
    const plotW = width - padLeft - padRight;
    const plotH = height - padTop - padBottom;

    const cellW = plotW / nFrames;
    const cellH = plotH / nMels;
    const span = Math.max(1e-6, hi - lo);

    for (let f = 0; f < nFrames; f++) {
      for (let m = 0; m < nMels; m++) {
        const frac = (matrix[f][m] - lo) / span;
        const [r, g, b] = colorForFraction(frac);
        ctx.fillStyle = `rgb(${r},${g},${b})`;
        const x = padLeft + f * cellW;
        const y = padTop + (nMels - 1 - m) * cellH;
        ctx.fillRect(x, y, Math.ceil(cellW), Math.ceil(cellH));
      }
    }

    // Axis ticks
    ctx.fillStyle = '#94a3b8';
    ctx.font = '10px monospace';
    ctx.textAlign = 'right';
    [0, 10, 20, 30, nMels - 1].forEach((band) => {
      if (band < nMels) {
        const y = padTop + (nMels - 1 - band) * cellH + cellH / 2 + 3;
        ctx.fillText(String(band), padLeft - 5, y);
      }
    });

    ctx.textAlign = 'center';
    [0, Math.floor(nFrames / 2), nFrames - 1].forEach((fr) => {
      const x = padLeft + (fr + 0.5) * cellW;
      ctx.fillText(`F${fr}`, x, height - 6);
    });
  }, [matrix, nFrames, nMels, lo, hi, height]);

  const handleMouseMove = (e: React.MouseEvent<HTMLCanvasElement>) => {
    const canvas = canvasRef.current;
    if (!canvas || nFrames === 0 || nMels === 0) return;
    const rect = canvas.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    const padLeft = 36;
    const padRight = 10;
    const padTop = 8;
    const padBottom = 22;
    const plotW = rect.width - padLeft - padRight;
    const plotH = rect.height - padTop - padBottom;
    if (x < padLeft || x > rect.width - padRight || y < padTop || y > rect.height - padBottom) {
      setCellInfo(null);
      return;
    }
    const frame = Math.min(nFrames - 1, Math.max(0, Math.floor(((x - padLeft) / plotW) * nFrames)));
    const band = Math.min(nMels - 1, Math.max(0, nMels - 1 - Math.floor(((y - padTop) / plotH) * nMels)));
    setCellInfo({ frame, band, value: matrix[frame][band] });
  };

  return (
    <div className="space-y-1.5">
      <div className="flex flex-wrap items-center justify-between gap-2 text-xs">
        <span className="font-medium text-slate-200">{title}</span>
        <span className="font-mono text-[11px] text-slate-400">
          {nFrames} frames × {nMels} mel bands · range [{lo.toFixed(1)}, {hi.toFixed(1)}] {unit}
        </span>
      </div>
      <div className="overflow-hidden rounded-lg border border-slate-800 bg-slate-950">
        <canvas
          ref={canvasRef}
          style={{ height: `${height}px` }}
          className="block w-full cursor-crosshair"
          onMouseMove={handleMouseMove}
          onMouseLeave={() => setCellInfo(null)}
        />
      </div>
      <div className="flex items-center justify-between text-[11px] text-slate-400">
        <span>Y: Mel band (0..{Math.max(0, nMels - 1)}) · X: Frame index (0..{Math.max(0, nFrames - 1)})</span>
        <span className="font-mono text-cyan-300">
          {cellInfo
            ? `Frame ${cellInfo.frame}, Band ${cellInfo.band}: ${cellInfo.value.toFixed(3)} ${unit}`
            : 'Hover cells to inspect dB value'}
        </span>
      </div>
    </div>
  );
}

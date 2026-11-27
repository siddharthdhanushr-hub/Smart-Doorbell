import { useEffect, useRef } from 'react';

interface WaveformCanvasProps {
  samples: number[];
  fs: number;
  height?: number;
}

export function WaveformCanvas({ samples, fs, height = 190 }: WaveformCanvasProps) {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas || samples.length === 0) return;

    const dpr = window.devicePixelRatio || 1;
    const width = canvas.clientWidth || 720;
    canvas.width = Math.floor(width * dpr);
    canvas.height = Math.floor(height * dpr);

    const ctx = canvas.getContext('2d');
    if (!ctx) return;
    ctx.scale(dpr, dpr);

    // Background
    ctx.fillStyle = '#020617';
    ctx.fillRect(0, 0, width, height);

    const padLeft = 44;
    const padRight = 12;
    const padTop = 12;
    const padBottom = 24;
    const plotW = width - padLeft - padRight;
    const plotH = height - padTop - padBottom;
    const midY = padTop + plotH / 2;

    // Gridlines
    ctx.strokeStyle = '#1e293b';
    ctx.lineWidth = 1;
    [-1, -0.5, 0, 0.5, 1].forEach((amp) => {
      const y = midY - amp * (plotH / 2);
      ctx.beginPath();
      ctx.moveTo(padLeft, y);
      ctx.lineTo(width - padRight, y);
      ctx.stroke();

      ctx.fillStyle = '#94a3b8';
      ctx.font = '10px monospace';
      ctx.textAlign = 'right';
      ctx.fillText(amp.toFixed(1), padLeft - 6, y + 3);
    });

    // Zero axis highlight
    ctx.strokeStyle = '#334155';
    ctx.beginPath();
    ctx.moveTo(padLeft, midY);
    ctx.lineTo(width - padRight, midY);
    ctx.stroke();

    // Waveform min/max envelope per pixel column
    ctx.strokeStyle = '#22d3ee';
    ctx.lineWidth = 1.2;
    const n = samples.length;
    for (let px = 0; px < plotW; px++) {
      const i0 = Math.floor((px / plotW) * n);
      const i1 = Math.max(i0 + 1, Math.floor(((px + 1) / plotW) * n));
      let minV = 1;
      let maxV = -1;
      for (let i = i0; i < i1 && i < n; i++) {
        const v = samples[i];
        if (v < minV) minV = v;
        if (v > maxV) maxV = v;
      }
      const yTop = midY - Math.max(-1, Math.min(1, maxV)) * (plotH / 2);
      const yBot = midY - Math.max(-1, Math.min(1, minV)) * (plotH / 2);
      ctx.beginPath();
      ctx.moveTo(padLeft + px, yTop);
      ctx.lineTo(padLeft + px, Math.max(yTop + 1, yBot));
      ctx.stroke();
    }

    // Time ticks (0..1.0 s)
    const durationS = n / Math.max(1, fs);
    ctx.fillStyle = '#94a3b8';
    ctx.font = '10px monospace';
    ctx.textAlign = 'center';
    [0, 0.25, 0.5, 0.75, 1].forEach((frac) => {
      const x = padLeft + frac * plotW;
      ctx.fillText(`${(durationS * frac).toFixed(2)} s`, x, height - 6);
    });
  }, [samples, fs, height]);

  return (
    <div className="w-full overflow-hidden rounded-lg border border-slate-800 bg-slate-950">
      <canvas ref={canvasRef} style={{ height: `${height}px` }} className="block w-full" />
    </div>
  );
}

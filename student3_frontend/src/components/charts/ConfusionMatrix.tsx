interface ConfusionMatrixProps {
  classes: string[];
  matrix: number[][];
  title?: string;
}

export function ConfusionMatrix({ classes, matrix, title }: ConfusionMatrixProps) {
  const maxCell = Math.max(1, ...matrix.flat());

  return (
    <div className="space-y-2">
      {title ? <h4 className="text-xs font-semibold uppercase tracking-wider text-slate-300">{title}</h4> : null}
      <div className="overflow-x-auto">
        <table className="w-full border-collapse text-center font-mono text-xs">
          <thead>
            <tr>
              <th className="border border-slate-800 bg-slate-950 px-2 py-2 text-left text-[11px] text-slate-400">
                True \ Pred
              </th>
              {classes.map((cls) => (
                <th key={cls} className="border border-slate-800 bg-slate-950 px-2 py-2 text-slate-200">
                  {cls}
                </th>
              ))}
              <th className="border border-slate-800 bg-slate-950 px-2 py-2 text-slate-400">Recall</th>
            </tr>
          </thead>
          <tbody>
            {matrix.map((row, ri) => {
              const rowSum = row.reduce((a, b) => a + b, 0);
              const recall = rowSum > 0 ? (row[ri] / rowSum) * 100 : null;
              return (
                <tr key={classes[ri] ?? ri}>
                  <td className="border border-slate-800 bg-slate-950 px-2 py-2 text-left font-semibold text-slate-200">
                    {classes[ri]}
                  </td>
                  {row.map((val, ci) => {
                    const intensity = val / maxCell;
                    const isDiag = ri === ci;
                    const bg = isDiag
                      ? `rgba(16, 185, 129, ${0.15 + intensity * 0.55})`
                      : val > 0
                        ? `rgba(244, 63, 94, ${0.12 + intensity * 0.5})`
                        : 'rgba(15, 23, 42, 0.7)';
                    return (
                      <td
                        key={`${ri}-${ci}`}
                        style={{ backgroundColor: bg }}
                        className={`border border-slate-800 px-2 py-2 ${
                          isDiag ? 'font-bold text-emerald-100' : val > 0 ? 'text-rose-100' : 'text-slate-500'
                        }`}
                      >
                        {val}
                      </td>
                    );
                  })}
                  <td className="border border-slate-800 bg-slate-950/70 px-2 py-2 text-cyan-300">
                    {recall !== null ? `${recall.toFixed(0)}%` : 'N/A'}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}

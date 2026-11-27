import { AlertTriangle, Clock, FlaskConical } from 'lucide-react';

interface EmptyAwaitingCardProps {
  title: string;
  description: string;
  expectedFiles?: string[];
  variant?: 'awaiting' | 'error' | 'empty';
  actionLabel?: string;
  onAction?: () => void;
}

export function EmptyAwaitingCard({
  title,
  description,
  expectedFiles,
  variant = 'awaiting',
  actionLabel,
  onAction,
}: EmptyAwaitingCardProps) {
  const Icon = variant === 'error' ? AlertTriangle : Clock;
  const borderClass =
    variant === 'error'
      ? 'border-rose-500/40 bg-rose-950/20'
      : 'border-slate-700 bg-slate-900/60';

  return (
    <div className={`rounded-xl border border-dashed p-6 ${borderClass}`}>
      <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
        <div className="flex items-start gap-3">
          <div className="rounded-lg bg-slate-800 p-2 text-slate-300">
            <Icon className="h-5 w-5" />
          </div>
          <div>
            <h3 className="text-sm font-semibold text-slate-100">{title}</h3>
            <p className="mt-1 max-w-2xl text-xs leading-relaxed text-slate-400">{description}</p>
            {expectedFiles && expectedFiles.length > 0 ? (
              <div className="mt-3 flex flex-wrap gap-1.5">
                {expectedFiles.map((f) => (
                  <code
                    key={f}
                    className="rounded border border-slate-700 bg-slate-950 px-2 py-0.5 text-[11px] text-cyan-300"
                  >
                    {f}
                  </code>
                ))}
              </div>
            ) : null}
          </div>
        </div>
        {actionLabel && onAction ? (
          <button
            type="button"
            onClick={onAction}
            className="inline-flex shrink-0 items-center gap-1.5 rounded-lg border border-amber-500/40 bg-amber-500/10 px-3 py-1.5 text-xs font-medium text-amber-200 hover:bg-amber-500/20"
          >
            <FlaskConical className="h-3.5 w-3.5" />
            <span>{actionLabel}</span>
          </button>
        ) : null}
      </div>
    </div>
  );
}

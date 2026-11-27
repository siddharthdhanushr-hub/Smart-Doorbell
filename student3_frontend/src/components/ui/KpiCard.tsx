import type { ReactNode } from 'react';
import type { DataOrigin } from '../../types/dashboard';
import { DataBadge } from './DataBadge';

interface KpiCardProps {
  title: string;
  value: string | number | null | undefined;
  unit?: string;
  subtitle?: string;
  origin?: DataOrigin;
  accent?: 'cyan' | 'emerald' | 'amber' | 'rose' | 'slate';
  icon?: ReactNode;
}

const ACCENT_RING: Record<NonNullable<KpiCardProps['accent']>, string> = {
  cyan: 'border-t-cyan-400',
  emerald: 'border-t-emerald-400',
  amber: 'border-t-amber-400',
  rose: 'border-t-rose-400',
  slate: 'border-t-slate-500',
};

export function KpiCard({
  title,
  value,
  unit,
  subtitle,
  origin,
  accent = 'cyan',
  icon,
}: KpiCardProps) {
  const isMissing = value === null || value === undefined || value === '';

  return (
    <div
      className={`rounded-xl border border-slate-800 border-t-2 ${ACCENT_RING[accent]} bg-slate-900/80 p-4 shadow-sm`}
    >
      <div className="flex items-start justify-between gap-2">
        <span className="text-xs font-medium uppercase tracking-wider text-slate-400">{title}</span>
        {icon ? <span className="text-slate-400">{icon}</span> : null}
      </div>
      <div className="mt-2 flex items-baseline gap-1.5">
        <span className="font-mono text-2xl font-semibold text-slate-100">
          {isMissing ? 'N/A' : value}
        </span>
        {!isMissing && unit ? (
          <span className="font-mono text-xs font-medium text-slate-400">{unit}</span>
        ) : null}
      </div>
      {subtitle ? <p className="mt-1.5 text-xs text-slate-400">{subtitle}</p> : null}
      {origin ? (
        <div className="mt-3">
          <DataBadge origin={origin} />
        </div>
      ) : null}
    </div>
  );
}

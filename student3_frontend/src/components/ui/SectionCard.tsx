import type { ReactNode } from 'react';
import type { DataOrigin } from '../../types/dashboard';
import { DataBadge } from './DataBadge';

interface SectionCardProps {
  title: string;
  subtitle?: string;
  origin?: DataOrigin;
  originLabel?: string;
  headerRight?: ReactNode;
  children: ReactNode;
  className?: string;
}

export function SectionCard({
  title,
  subtitle,
  origin,
  originLabel,
  headerRight,
  children,
  className = '',
}: SectionCardProps) {
  return (
    <section
      className={`rounded-xl border border-slate-800 bg-slate-900/75 p-5 shadow-sm ${className}`}
    >
      <div className="mb-4 flex flex-wrap items-start justify-between gap-3 border-b border-slate-800/80 pb-3">
        <div>
          <div className="flex flex-wrap items-center gap-2.5">
            <h2 className="text-base font-semibold text-slate-100">{title}</h2>
            {origin ? <DataBadge origin={origin} customLabel={originLabel} /> : null}
          </div>
          {subtitle ? <p className="mt-1 text-xs text-slate-400">{subtitle}</p> : null}
        </div>
        {headerRight ? <div className="flex flex-wrap items-center gap-2">{headerRight}</div> : null}
      </div>
      {children}
    </section>
  );
}

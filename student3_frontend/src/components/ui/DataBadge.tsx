import { Activity, Clock, Database, FlaskConical } from 'lucide-react';
import type { DataOrigin } from '../../types/dashboard';

const CONFIG: Record<
  DataOrigin,
  { label: string; classes: string; Icon: typeof Database }
> = {
  live_api: {
    label: 'Live API (Flask)',
    classes: 'border-emerald-500/40 bg-emerald-500/10 text-emerald-300',
    Icon: Activity,
  },
  recorded: {
    label: 'Recorded Hardware / Python Run',
    classes: 'border-cyan-500/40 bg-cyan-500/10 text-cyan-300',
    Icon: Database,
  },
  mock: {
    label: 'Mock / Simulated Data',
    classes: 'border-amber-500/40 bg-amber-500/10 text-amber-300',
    Icon: FlaskConical,
  },
  awaiting: {
    label: 'Awaiting Student 4 Results',
    classes: 'border-slate-600 bg-slate-800/80 text-slate-300',
    Icon: Clock,
  },
};

export function DataBadge({ origin, customLabel }: { origin: DataOrigin; customLabel?: string }) {
  const { label, classes, Icon } = CONFIG[origin];
  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-full border px-2.5 py-0.5 text-xs font-medium tracking-tight ${classes}`}
    >
      <Icon className="h-3.5 w-3.5 shrink-0" />
      <span>{customLabel ?? label}</span>
    </span>
  );
}

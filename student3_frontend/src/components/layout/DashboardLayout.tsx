import { useEffect, useState, type ReactNode } from 'react';
import {
  Activity,
  AudioLines,
  BrainCircuit,
  Cpu,
  Database,
  GitCompare,
  LayoutDashboard,
  Menu,
  Network,
  RefreshCw,
  ShieldCheck,
  Waves,
  X,
} from 'lucide-react';
import type { PageId } from '../../types/dashboard';
import { DataBadge } from '../ui/DataBadge';

export interface NavItem {
  id: PageId;
  label: string;
  shortLabel: string;
  Icon: typeof LayoutDashboard;
}

export const NAV_ITEMS: NavItem[] = [
  { id: 'overview', label: 'Overview', shortLabel: 'Overview', Icon: LayoutDashboard },
  { id: 'architecture', label: 'System Architecture', shortLabel: 'Architecture', Icon: Network },
  { id: 'audio', label: 'Audio Input', shortLabel: 'Audio Input', Icon: AudioLines },
  { id: 'communication', label: 'Communication & Throughput', shortLabel: 'Comms & Pipe', Icon: Activity },
  { id: 'packets', label: 'Packet Integrity', shortLabel: 'Packet Integrity', Icon: ShieldCheck },
  { id: 'logmel', label: 'Log-mel Feature Visualisation', shortLabel: 'Log-Mel', Icon: Waves },
  { id: 'hardware', label: 'Hardware Performance', shortLabel: 'Hardware', Icon: Cpu },
  { id: 'comparison', label: 'Laptop vs ESP32 Comparison', shortLabel: 'Laptop vs Board', Icon: GitCompare },
  { id: 'dataset', label: 'Dataset Information', shortLabel: 'Dataset', Icon: Database },
  { id: 'ml', label: 'ML Evaluation', shortLabel: 'ML Evaluation', Icon: BrainCircuit },
];

interface DashboardLayoutProps {
  activePage: PageId;
  onSelectPage: (page: PageId) => void;
  flaskOnline: boolean;
  modeLabel: string;
  student4Ready: boolean;
  onRefresh: () => void;
  refreshing: boolean;
  children: ReactNode;
}

export function DashboardLayout({
  activePage,
  onSelectPage,
  flaskOnline,
  modeLabel,
  student4Ready,
  onRefresh,
  refreshing,
  children,
}: DashboardLayoutProps) {
  const [mobileOpen, setMobileOpen] = useState(false);

  useEffect(() => {
    if (!mobileOpen) return;
    const onKey = (e: KeyboardEvent) => {
      if (e.key === 'Escape') setMobileOpen(false);
    };
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, [mobileOpen]);

  const navContent = (
    <nav className="flex flex-col gap-1 p-3">
      <div className="mb-3 px-2 pt-1">
        <div className="flex items-center gap-2">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-cyan-500/15 text-cyan-300 ring-1 ring-cyan-500/30">
            <Cpu className="h-4 w-4" />
          </div>
          <div>
            <p className="text-sm font-semibold tracking-tight text-slate-100">Smart Doorbell</p>
            <p className="text-[11px] text-slate-400">Team 1 · Paradise · Edge AI</p>
          </div>
        </div>
      </div>

      {NAV_ITEMS.map((item, idx) => {
        const active = item.id === activePage;
        const Icon = item.Icon;
        return (
          <button
            key={item.id}
            type="button"
            aria-current={active ? 'page' : undefined}
            onClick={() => {
              onSelectPage(item.id);
              setMobileOpen(false);
            }}
            className={`flex items-center gap-2.5 rounded-lg px-2.5 py-2 text-left text-xs font-medium transition-colors ${
              active
                ? 'bg-cyan-500/15 text-cyan-200 ring-1 ring-cyan-500/30'
                : 'text-slate-400 hover:bg-slate-800/70 hover:text-slate-100'
            }`}
          >
            <span className="w-4 text-[10px] font-mono text-slate-500">{String(idx + 1).padStart(2, '0')}</span>
            <Icon className={`h-4 w-4 shrink-0 ${active ? 'text-cyan-300' : 'text-slate-400'}`} />
            <span className="truncate">{item.label}</span>
          </button>
        );
      })}
    </nav>
  );

  const activeItem = NAV_ITEMS.find((n) => n.id === activePage) ?? NAV_ITEMS[0];

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 lg:flex">
      {/* Desktop Sidebar */}
      <aside className="hidden w-64 shrink-0 border-r border-slate-800 bg-slate-900/60 lg:block">
        <div className="sticky top-0 max-h-screen overflow-y-auto">{navContent}</div>
      </aside>

      {/* Mobile Drawer */}
      {mobileOpen ? (
        <div className="fixed inset-0 z-50 flex lg:hidden">
          <div className="fixed inset-0 bg-black/70" onClick={() => setMobileOpen(false)} />
          <aside className="relative z-10 w-72 border-r border-slate-800 bg-slate-900">
            <div className="flex items-center justify-end p-2">
              <button
                type="button"
                onClick={() => setMobileOpen(false)}
                className="rounded-lg p-1.5 text-slate-400 hover:bg-slate-800 hover:text-slate-100"
                aria-label="Close navigation"
              >
                <X className="h-5 w-5" />
              </button>
            </div>
            {navContent}
          </aside>
        </div>
      ) : null}

      {/* Main Content */}
      <div className="flex min-w-0 flex-1 flex-col">
        <header className="sticky top-0 z-30 border-b border-slate-800 bg-slate-950/90 px-4 py-3 backdrop-blur sm:px-6">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <div className="flex items-center gap-3">
              <button
                type="button"
                onClick={() => setMobileOpen(true)}
                className="rounded-lg border border-slate-800 bg-slate-900 p-2 text-slate-300 hover:bg-slate-800 lg:hidden"
                aria-label="Open navigation"
              >
                <Menu className="h-4 w-4" />
              </button>
              <div>
                <h1 className="text-base font-semibold text-slate-100 sm:text-lg">{activeItem.label}</h1>
                <p className="text-xs text-slate-400">
                  ESP32-S3-DevKitC-1 N16R8 · Board-free dashboard ({modeLabel})
                </p>
              </div>
            </div>

            <div className="flex flex-wrap items-center gap-2">
              <DataBadge
                origin={flaskOnline ? 'live_api' : 'recorded'}
                customLabel={
                  flaskOnline ? 'Flask API Online (Recorded Board Data)' : 'Offline Mode (Recorded Repo Data)'
                }
              />
              <DataBadge
                origin={student4Ready ? 'recorded' : 'awaiting'}
                customLabel={student4Ready ? 'Student 4 Outputs Loaded' : 'Awaiting Student 4 ML'}
              />
              <button
                type="button"
                onClick={onRefresh}
                disabled={refreshing}
                className="inline-flex items-center gap-1.5 rounded-lg border border-slate-700 bg-slate-900 px-2.5 py-1 text-xs font-medium text-slate-200 hover:bg-slate-800 disabled:opacity-50"
              >
                <RefreshCw className={`h-3.5 w-3.5 ${refreshing ? 'animate-spin' : ''}`} />
                <span>Reload</span>
              </button>
            </div>
          </div>
        </header>

        <main className="mx-auto w-full max-w-7xl flex-1 space-y-6 p-4 sm:p-6">{children}</main>
      </div>
    </div>
  );
}

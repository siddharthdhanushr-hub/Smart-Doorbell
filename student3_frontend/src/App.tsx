import { useCallback, useEffect, useState } from 'react';
import { DashboardLayout } from './components/layout/DashboardLayout';
import { AudioInputPage } from './pages/AudioInputPage';
import { ArchitecturePage } from './pages/ArchitecturePage';
import { CommunicationPage } from './pages/CommunicationPage';
import { ComparisonPage } from './pages/ComparisonPage';
import { DatasetPage } from './pages/DatasetPage';
import { HardwarePerformancePage } from './pages/HardwarePerformancePage';
import { LogMelPage } from './pages/LogMelPage';
import { MlEvaluationPage } from './pages/MlEvaluationPage';
import { OverviewPage } from './pages/OverviewPage';
import { PacketIntegrityPage } from './pages/PacketIntegrityPage';
import { loadClipDetail, loadDashboardBundle } from './services/api';
import type { ClipDetailPayload, DashboardBundle, PageId } from './types/dashboard';

export function App() {
  const [activePage, setActivePage] = useState<PageId>('overview');
  const [bundle, setBundle] = useState<DashboardBundle | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Shared clip inspection state across Audio Input & Log-Mel pages
  const [clipId, setClipId] = useState(0);
  const [fs, setFs] = useState(16000);
  const [antialias, setAntialias] = useState(true);
  const [clipDetail, setClipDetail] = useState<ClipDetailPayload | null>(null);
  const [clipLoading, setClipLoading] = useState(false);

  const fetchAll = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await loadDashboardBundle();
      setBundle(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load dashboard data');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void fetchAll();
  }, [fetchAll]);

  useEffect(() => {
    if (!bundle) return;
    let cancelled = false;
    setClipLoading(true);
    const manifestRow = bundle.dataset.manifest.find((r) => Number(r.clip_id) === clipId);
    loadClipDetail(clipId, fs, antialias, manifestRow, bundle.backendStatus.flaskOnline)
      .then((res) => {
        if (!cancelled) setClipDetail(res);
      })
      .finally(() => {
        if (!cancelled) setClipLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [bundle, clipId, fs, antialias]);

  if (loading && !bundle) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-slate-950 text-sm text-slate-300">
        Loading Smart Doorbell Edge AI Dashboard...
      </div>
    );
  }

  if (error || !bundle) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-slate-950 p-6">
        <div className="max-w-md rounded-xl border border-rose-500/40 bg-rose-950/20 p-6 text-sm text-rose-200">
          <p className="font-semibold">Dashboard Initialization Error</p>
          <p className="mt-1 text-xs text-rose-300">{error ?? 'Unknown error'}</p>
          <button
            type="button"
            onClick={() => void fetchAll()}
            className="mt-4 rounded-lg border border-rose-500/40 bg-rose-500/20 px-3 py-1.5 text-xs font-medium"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <DashboardLayout
      activePage={activePage}
      onSelectPage={setActivePage}
      flaskOnline={bundle.backendStatus.flaskOnline}
      modeLabel={bundle.backendStatus.modeLabel}
      student4Ready={bundle.student4.origin !== 'awaiting'}
      onRefresh={() => void fetchAll()}
      refreshing={loading}
    >
      {activePage === 'overview' && <OverviewPage bundle={bundle} onNavigate={setActivePage} />}
      {activePage === 'architecture' && <ArchitecturePage bundle={bundle} />}
      {activePage === 'audio' && (
        <AudioInputPage
          bundle={bundle}
          clipId={clipId}
          fs={fs}
          antialias={antialias}
          onChangeClip={setClipId}
          onChangeFs={setFs}
          onChangeAntialias={setAntialias}
          clipDetail={clipDetail}
          clipLoading={clipLoading}
        />
      )}
      {activePage === 'communication' && <CommunicationPage bundle={bundle} />}
      {activePage === 'packets' && <PacketIntegrityPage bundle={bundle} />}
      {activePage === 'logmel' && (
        <LogMelPage
          bundle={bundle}
          clipId={clipId}
          fs={fs}
          antialias={antialias}
          onChangeClip={setClipId}
          clipDetail={clipDetail}
          clipLoading={clipLoading}
        />
      )}
      {activePage === 'hardware' && <HardwarePerformancePage bundle={bundle} />}
      {activePage === 'comparison' && <ComparisonPage bundle={bundle} />}
      {activePage === 'dataset' && <DatasetPage bundle={bundle} />}
      {activePage === 'ml' && <MlEvaluationPage bundle={bundle} />}
    </DashboardLayout>
  );
}

export default App;

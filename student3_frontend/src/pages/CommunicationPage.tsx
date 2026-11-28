import { useMemo } from 'react';
import type { DashboardBundle } from '../types/dashboard';
import { BarChart } from '../components/charts/BarChart';
import { LineChart } from '../components/charts/LineChart';
import { KpiCard } from '../components/ui/KpiCard';
import { SectionCard } from '../components/ui/SectionCard';

function avgNullable(nums: number[]): number | null {
  if (nums.length === 0) return null;
  return nums.reduce((a, b) => a + b, 0) / nums.length;
}

export function CommunicationPage({ bundle }: { bundle: DashboardBundle }) {
  const runs = bundle.mission1.results.runs;
  const primaryRun = bundle.mission45.all_144_runs.runs[0];
  const hw = bundle.configs.hardware;

  // 1. Baud throughput aggregation
  const baudStats = useMemo(() => {
    const bauds = [115200, 921600, 2000000];
    return bauds.map((baud) => {
      const comRuns = runs.filter((r) => r.test_group === 'baud_throughput' && r.port_label === 'COM' && r.baud === baud);
      const usbRuns = runs.filter((r) => r.test_group === 'baud_throughput' && r.port_label === 'USB' && r.baud === baud);
      return {
        label: baud === 2000000 ? '2M' : `${(baud / 1000).toFixed(1)}k`,
        comKbps: avgNullable(comRuns.map((r) => r.throughput_board_bps / 1000)),
        usbBoardKbps: avgNullable(usbRuns.map((r) => r.throughput_board_bps / 1000)),
        usbLaptopKbps: avgNullable(usbRuns.map((r) => r.throughput_laptop_bps / 1000)),
      };
    });
  }, [runs]);

  // 2. Data type comparison (COM12 @ 921.6k vs USB)
  const dtypeStats = useMemo(() => {
    const fmts = ['f32', 'i16', 'i8'];
    return fmts.map((fmt) => {
      const com = runs.filter((r) => r.test_group === 'datatype_speed0' && r.port_label === 'COM' && r.fmt === fmt);
      const usb = runs.filter((r) => r.test_group === 'datatype_speed0' && r.port_label === 'USB' && r.fmt === fmt);
      return {
        fmt,
        comKbps: avgNullable(com.map((r) => r.throughput_board_bps / 1000)),
        usbKbps: avgNullable(usb.map((r) => r.throughput_board_bps / 1000)),
        comSamplesS: avgNullable(com.map((r) => r.effective_samples_per_s)),
        usbSamplesS: avgNullable(usb.map((r) => r.effective_samples_per_s)),
      };
    });
  }, [runs]);

  // 3. Packet size overhead (samples_per_packet)
  const pktSizeStats = useMemo(() => {
    const sizes = [8, 64, 320, 1024];
    const comPts = sizes
      .map((sz) => {
        const subset = runs.filter((r) => r.test_group === 'packet_size' && r.port_label === 'COM' && r.samples_per_packet === sz);
        const y = avgNullable(subset.map((r) => r.throughput_board_bps / 1000));
        return y !== null ? { x: sz, y } : null;
      })
      .filter((p): p is { x: number; y: number } => p !== null);

    const usbPts = sizes
      .map((sz) => {
        const subset = runs.filter((r) => r.test_group === 'packet_size' && r.port_label === 'USB' && r.samples_per_packet === sz);
        const y = avgNullable(subset.map((r) => r.throughput_board_bps / 1000));
        return y !== null ? { x: sz, y } : null;
      })
      .filter((p): p is { x: number; y: number } => p !== null);

    return { comPts, usbPts };
  }, [runs]);

  // 4. Real-time matrix (speed=1.0)
  const rtRows = useMemo(() => {
    const configs = [
      { fs: 16000, fmt: 'f32', reqBps: 64000 },
      { fs: 16000, fmt: 'i16', reqBps: 32000 },
      { fs: 16000, fmt: 'i8', reqBps: 16000 },
      { fs: 8000, fmt: 'i16', reqBps: 16000 },
      { fs: 8000, fmt: 'i8', reqBps: 8000 },
    ];
    return configs.map((cfg) => {
      const findRun = (portLabel: string, baud?: number) =>
        runs.find(
          (r) =>
            r.test_group === 'realtime_speed1' &&
            r.port_label === portLabel &&
            r.fs === cfg.fs &&
            r.fmt === cfg.fmt &&
            (baud === undefined || r.baud === baud),
        );
      const r115 = findRun('COM', 115200);
      const r921 = findRun('COM', 921600);
      const rUsb = findRun('USB');
      const pass = (r: typeof r115) => {
        if (!r) return null;
        const expectedSec = r.samples_rx / r.fs;
        return r.send_seconds <= expectedSec * 1.1 && r.bad_crc === 0 && r.seq_gaps === 0;
      };
      return {
        label: `${cfg.fs / 1000} kHz ${cfg.fmt}`,
        reqKbps: cfg.reqBps / 1000,
        com115: pass(r115),
        com921: pass(r921),
        usb: pass(rUsb),
      };
    });
  }, [runs]);

  return (
    <div className="space-y-6">
      {/* Connection & Stream Status */}
      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <KpiCard
          title="ESP32 Connection Status"
          value="Offline (Recorded)"
          subtitle="No physical board required · Showing verified COM11/COM12 logs"
          origin="recorded"
          accent="amber"
        />
        <KpiCard
          title="Active Stream Profile"
          value={`${primaryRun.fs / 1000} kHz · ${primaryRun.fmt}`}
          unit={`S=${primaryRun.scale}`}
          subtitle="Shipping configuration · 144 clips streamed at speed=1.0×"
          origin="recorded"
          accent="cyan"
        />
        <KpiCard
          title="USB Throughput (COM11)"
          value={baudStats[1]?.usbBoardKbps !== null && baudStats[1]?.usbBoardKbps !== undefined ? baudStats[1].usbBoardKbps.toFixed(1) : null}
          unit="kB/s"
          subtitle={`Laptop side ~${baudStats[1]?.usbLaptopKbps !== null && baudStats[1]?.usbLaptopKbps !== undefined ? baudStats[1].usbLaptopKbps.toFixed(1) : 'N/A'} kB/s · ignores baud`}
          origin="recorded"
          accent="emerald"
        />
        <KpiCard
          title="UART Bridge (COM12 @ 2M)"
          value={baudStats[2]?.comKbps !== null && baudStats[2]?.comKbps !== undefined ? baudStats[2].comKbps.toFixed(1) : null}
          unit="kB/s"
          subtitle={`921.6k baud: ${baudStats[1]?.comKbps !== null && baudStats[1]?.comKbps !== undefined ? baudStats[1].comKbps.toFixed(1) : 'N/A'} kB/s · 0 UART errors`}
          origin="recorded"
          accent="cyan"
        />
      </div>

      {/* Port comparison cards */}
      <div className="grid gap-6 md:grid-cols-2">
        <SectionCard
          title={`Native USB CDC (${hw.usb_ports.usb_native_cdc.port})`}
          subtitle={hw.usb_ports.usb_native_cdc.pnp_device_id}
          origin="recorded"
        >
          <ul className="space-y-1.5 text-xs text-slate-300">
            <li>Baud behavior: <span className="text-cyan-300">{hw.usb_ports.usb_native_cdc.baud_note}</span></li>
            <li>Board-side sustained rate: <span className="font-mono text-emerald-300">~332 kB/s</span></li>
            <li>Max zero-loss speed (16 kHz i16): <span className="font-mono text-emerald-300">6.0× (192 kB/s)</span></li>
            <li>Overflow threshold: <span className="font-mono text-rose-300">&ge; 8.0× (32 KB RX buffer)</span></li>
          </ul>
        </SectionCard>

        <SectionCard
          title={`WCH UART Bridge (${hw.usb_ports.com_uart_bridge.port})`}
          subtitle={hw.usb_ports.com_uart_bridge.pnp_device_id}
          origin="recorded"
        >
          <ul className="space-y-1.5 text-xs text-slate-300">
            <li>Tested baud rates: <span className="font-mono text-cyan-300">115.2k / 921.6k / 2,000,000</span></li>
            <li>Measured throughput: <span className="font-mono text-emerald-300">11.4 / 90.9 / 194.7 kB/s</span></li>
            <li>Flow behavior: <span className="text-emerald-300">Wire-paced TX backpressure (0 dropped bytes)</span></li>
            <li>RX buffer size: <span className="font-mono text-slate-200">{hw.usb_ports.com_uart_bridge.rx_buffer_bytes.toLocaleString()} bytes</span></li>
          </ul>
        </SectionCard>
      </div>

      {/* Charts Row */}
      <div className="grid gap-6 lg:grid-cols-2">
        <SectionCard
          title="Throughput vs Baud Rate"
          subtitle="COM12 scales linearly with baud; COM11 USB CDC stays flat (~332 kB/s)"
          origin="recorded"
        >
          <BarChart
            categories={baudStats.map((b) => `${b.label} baud`)}
            series={[
              { name: 'COM12 UART (Board)', color: '#22d3ee', values: baudStats.map((b) => b.comKbps) },
              { name: 'COM11 USB (Board)', color: '#34d399', values: baudStats.map((b) => b.usbBoardKbps) },
            ]}
            yLabel="Throughput"
            yUnit="kB/s"
            valueFormatter={(v) => v.toFixed(1)}
          />
        </SectionCard>

        <SectionCard
          title="Data-Type Effective Sample Rate"
          subtitle="COM12 @ 921,600 baud (samples/s doubles as byte width halves: f32 → i16 → i8)"
          origin="recorded"
        >
          <BarChart
            categories={dtypeStats.map((d) => d.fmt)}
            series={[
              { name: 'COM12 (921.6k baud)', color: '#a78bfa', values: dtypeStats.map((d) => d.comSamplesS) },
              {
                name: 'COM11 USB',
                color: '#34d399',
                values: dtypeStats.map((d) => d.usbSamplesS),
              },
            ]}
            yLabel="Effective Sample Rate"
            yUnit="samples/s"
            valueFormatter={(v) => Math.round(v).toLocaleString()}
          />
        </SectionCard>
      </div>

      {/* Packet Size + Real-Time Matrix */}
      <div className="grid gap-6 lg:grid-cols-2">
        <SectionCard
          title="Packet Size Overhead (COM12 @ 921.6k)"
          subtitle="Larger payloads amortize the 13-byte header + CRC-32 framing overhead"
          origin="recorded"
        >
          <LineChart
            series={[
              { name: 'COM12 Board Throughput', color: '#22d3ee', points: pktSizeStats.comPts },
              ...(pktSizeStats.usbPts.length
                ? [{ name: 'COM11 USB Throughput', color: '#34d399', points: pktSizeStats.usbPts }]
                : []),
            ]}
            xLabel="Samples per Packet"
            xUnit="samples"
            yLabel="Throughput"
            yUnit="kB/s"
            xFormatter={(v) => String(v)}
            yFormatter={(v) => v.toFixed(1)}
          />
        </SectionCard>

        <SectionCard
          title="Real-Time Capability Matrix (speed = 1.0×)"
          subtitle="Pass requires send_seconds <= 1.1 s/s with 0 CRC errors and 0 sequence gaps"
          origin="recorded"
        >
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead>
                <tr className="border-b border-slate-800 text-slate-400">
                  <th className="py-2 pr-3">Config</th>
                  <th className="py-2 pr-3 font-mono">Required</th>
                  <th className="py-2 pr-3">COM 115.2k</th>
                  <th className="py-2 pr-3">COM 921.6k</th>
                  <th className="py-2">USB COM11</th>
                </tr>
              </thead>
              <tbody>
                {rtRows.map((row) => {
                  const badge = (ok: boolean | null) =>
                    ok === null ? (
                      <span className="text-slate-500">N/A</span>
                    ) : ok ? (
                      <span className="rounded bg-emerald-500/15 px-2 py-0.5 font-medium text-emerald-300">PASS</span>
                    ) : (
                      <span className="rounded bg-rose-500/15 px-2 py-0.5 font-medium text-rose-300">FAIL</span>
                    );
                  return (
                    <tr key={row.label} className="border-b border-slate-800/60">
                      <td className="py-2.5 pr-3 font-medium text-slate-200">{row.label}</td>
                      <td className="py-2.5 pr-3 font-mono text-slate-300">{row.reqKbps.toFixed(0)} kB/s</td>
                      <td className="py-2.5 pr-3">{badge(row.com115)}</td>
                      <td className="py-2.5 pr-3">{badge(row.com921)}</td>
                      <td className="py-2.5">{badge(row.usb)}</td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </SectionCard>
      </div>
    </div>
  );
}

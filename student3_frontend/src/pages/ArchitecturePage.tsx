import type { DashboardBundle } from '../types/dashboard';
import { SectionCard } from '../components/ui/SectionCard';

export function ArchitecturePage({ bundle }: { bundle: DashboardBundle }) {
  const hw = bundle.configs.hardware;
  const proto = bundle.configs.protocol;

  return (
    <div className="space-y-6">
      <SectionCard
        title="End-to-End Hardware & Software Architecture"
        subtitle="Laptop Python host → Binary CRC-32 serial link → ESP32-S3 N16R8 → Offline Validation & Dashboard"
        origin="recorded"
      >
        <div className="overflow-x-auto rounded-lg border border-slate-800 bg-slate-950 p-4">
          <svg viewBox="0 0 920 270" className="h-auto w-full min-w-[740px]">
            <defs>
              <marker id="arrow" markerWidth="8" markerHeight="8" refX="7" refY="3.5" orient="auto">
                <polygon points="0 0, 8 3.5, 0 7" fill="#22d3ee" />
              </marker>
              <marker id="arrowAmber" markerWidth="8" markerHeight="8" refX="7" refY="3.5" orient="auto">
                <polygon points="0 0, 8 3.5, 0 7" fill="#fbbf24" />
              </marker>
            </defs>

            {/* Box 1: Laptop Audio + Codec */}
            <rect x="16" y="34" width="195" height="190" rx="10" fill="#0f172a" stroke="#334155" />
            <text x="113" y="58" textAnchor="middle" fill="#22d3ee" fontSize="12" fontWeight="bold">
              Laptop Host (Student 2)
            </text>
            <text x="28" y="82" fill="#e2e8f0" fontSize="10" fontFamily="monospace">1. team_audio.py</text>
            <text x="28" y="97" fill="#94a3b8" fontSize="9.5">144 clips · 6 classes · 16/8 kHz</text>
            <text x="28" y="122" fill="#e2e8f0" fontSize="10" fontFamily="monospace">2. audio_codec.py</text>
            <text x="28" y="137" fill="#94a3b8" fontSize="9.5">f32 / i16 / i8 + scale S</text>
            <text x="28" y="162" fill="#e2e8f0" fontSize="10" fontFamily="monospace">3. reference_logmel.py</text>
            <text x="28" y="177" fill="#94a3b8" fontSize="9.5">NumPy HTK 40-mel baseline</text>
            <text x="28" y="202" fill="#e2e8f0" fontSize="10" fontFamily="monospace">4. serial_sender.py</text>

            {/* Uplink arrow */}
            <line x1="211" y1="95" x2="292" y2="95" stroke="#22d3ee" strokeWidth="2" markerEnd="url(#arrow)" />
            <text x="251" y="76" textAnchor="middle" fill="#22d3ee" fontSize="9.5" fontFamily="monospace">
              0xA5 0x5A
            </text>
            <text x="251" y="88" textAnchor="middle" fill="#94a3b8" fontSize="8.5">
              COM11 / COM12
            </text>

            {/* Downlink arrow */}
            <line x1="292" y1="168" x2="211" y2="168" stroke="#fbbf24" strokeWidth="2" markerEnd="url(#arrowAmber)" />
            <text x="251" y="158" textAnchor="middle" fill="#fbbf24" fontSize="9.5" fontFamily="monospace">
              0xB5 0x5B
            </text>
            <text x="251" y="182" textAnchor="middle" fill="#94a3b8" fontSize="8.5">
              &apos;F&apos; feats + &apos;S&apos; stats
            </text>

            {/* Box 2: ESP32-S3 */}
            <rect x="296" y="22" width="295" height="218" rx="10" fill="#0f172a" stroke="#0891b2" strokeWidth="1.5" />
            <text x="443" y="46" textAnchor="middle" fill="#22d3ee" fontSize="12" fontWeight="bold">
              ESP32-S3-DevKitC-1 N16R8 (Student 1)
            </text>
            <text x="443" y="62" textAnchor="middle" fill="#94a3b8" fontSize="9.5">
              Dual-core LX7 @ 240 MHz · 32 KB RX Ring Buffer
            </text>

            <rect x="312" y="76" width="126" height="62" rx="6" fill="#020617" stroke="#1e293b" />
            <text x="375" y="95" textAnchor="middle" fill="#34d399" fontSize="10" fontWeight="bold">
              OPI PSRAM (8 MiB)
            </text>
            <text x="375" y="111" textAnchor="middle" fill="#cbd5e1" fontSize="9">
              4,608,000 B stream
            </text>
            <text x="375" y="125" textAnchor="middle" fill="#94a3b8" fontSize="8.5">
              CRC 55c3d431 match
            </text>

            <rect x="448" y="76" width="128" height="62" rx="6" fill="#020617" stroke="#1e293b" />
            <text x="512" y="95" textAnchor="middle" fill="#34d399" fontSize="10" fontWeight="bold">
              LittleFS (6.88 MiB)
            </text>
            <text x="512" y="111" textAnchor="middle" fill="#cbd5e1" fontSize="9">
              /rec.bin persistent
            </text>
            <text x="512" y="125" textAnchor="middle" fill="#94a3b8" fontSize="8.5">
              Survives power cut
            </text>

            <rect x="312" y="150" width="264" height="74" rx="6" fill="#020617" stroke="#1e293b" />
            <text x="444" y="169" textAnchor="middle" fill="#22d3ee" fontSize="10" fontWeight="bold">
              features.h — Radix-2 FFT + Sparse Mel Filterbank
            </text>
            <text x="444" y="186" textAnchor="middle" fill="#cbd5e1" fontSize="9" fontFamily="monospace">
              480-sample Hann → 512-pt FFT → 40 HTK bands → 10·log10
            </text>
            <text x="444" y="203" textAnchor="middle" fill="#94a3b8" fontSize="8.5">
              685 us/frame (3.4% of 20 ms hop) · 53.6 KB internal SRAM
            </text>

            {/* Arrow to Validation & Dashboard */}
            <line x1="591" y1="130" x2="652" y2="130" stroke="#22d3ee" strokeWidth="2" markerEnd="url(#arrow)" />
            <text x="621" y="120" textAnchor="middle" fill="#94a3b8" fontSize="8.5">
              JSON / NPZ
            </text>

            {/* Box 3: Student 4 */}
            <rect x="656" y="26" width="246" height="94" rx="10" fill="#0f172a" stroke="#334155" />
            <text x="779" y="50" textAnchor="middle" fill="#c084fc" fontSize="11.5" fontWeight="bold">
              Offline Validation & ML (Student 4)
            </text>
            <text x="670" y="72" fill="#cbd5e1" fontSize="9.5">• MAE / MSE / RMSE vs Python Ref</text>
            <text x="670" y="88" fill="#cbd5e1" fontSize="9.5">• 8 kHz AA vs No-AA error breakdown</text>
            <text x="670" y="104" fill="#cbd5e1" fontSize="9.5">• Clip-split Nearest-Centroid Classifier</text>

            {/* Box 4: Student 3 */}
            <rect x="656" y="138" width="246" height="100" rx="10" fill="#0f172a" stroke="#22d3ee" strokeWidth="1.5" />
            <text x="779" y="162" textAnchor="middle" fill="#22d3ee" fontSize="11.5" fontWeight="bold">
              Web Dashboard (Student 3)
            </text>
            <text x="670" y="184" fill="#cbd5e1" fontSize="9.5">• Student 2 Flask API (/api/*)</text>
            <text x="670" y="200" fill="#cbd5e1" fontSize="9.5">• Recorded Repo JSON/CSV Logs</text>
            <text x="670" y="216" fill="#cbd5e1" fontSize="9.5">• Board-free Mock & Pending States</text>
          </svg>
        </div>
      </SectionCard>

      {/* Binary Frame Format + Text Commands */}
      <div className="grid gap-6 lg:grid-cols-2">
        <SectionCard
          title="Serial Framing & Integrity Protocol"
          subtitle={`${proto.protocol_name} · ${proto.endianness} · ${proto.crc_algorithm}`}
          origin="recorded"
        >
          <div className="space-y-4 text-xs">
            <div className="rounded-lg border border-slate-800 bg-slate-950/70 p-3">
              <p className="font-semibold text-cyan-300">Uplink Frame (Laptop → ESP32-S3)</p>
              <p className="mt-1 font-mono text-[11px] text-slate-200">{proto.binary_frames.uplink_laptop_to_board.layout}</p>
              <div className="mt-2 grid grid-cols-2 gap-2 text-[11px] text-slate-400">
                <span>Magic: <code className="text-slate-200">{proto.binary_frames.uplink_laptop_to_board.magic}</code></span>
                <span>Max payload: <code className="text-slate-200">{proto.max_payload_bytes} B</code></span>
                <span>Type D: Audio bytes</span>
                <span>Type E: End of stream</span>
              </div>
            </div>

            <div className="rounded-lg border border-slate-800 bg-slate-950/70 p-3">
              <p className="font-semibold text-amber-300">Downlink Frame (ESP32-S3 → Laptop)</p>
              <p className="mt-1 font-mono text-[11px] text-slate-200">{proto.binary_frames.downlink_board_to_laptop.layout}</p>
              <div className="mt-2 space-y-1 text-[11px] text-slate-400">
                <p>Magic: <code className="text-slate-200">{proto.binary_frames.downlink_board_to_laptop.magic}</code></p>
                <p>Type F: <code className="text-slate-200">{proto.binary_frames.downlink_board_to_laptop.types.F}</code></p>
                <p>Type S: <code className="text-slate-200">{proto.binary_frames.downlink_board_to_laptop.types.S}</code></p>
              </div>
            </div>
          </div>
        </SectionCard>

        <SectionCard
          title="Hardware Build Settings & Known Limitations"
          subtitle={`${hw.target_board} · ${hw.chip_detected.chip_type}`}
          origin="recorded"
        >
          <div className="space-y-3 text-xs">
            <div className="rounded-lg border border-slate-800 bg-slate-950/70 p-3">
              <p className="font-semibold text-slate-100">Verified Arduino IDE / FQBN Configuration</p>
              <p className="mt-1 break-all font-mono text-[11px] text-cyan-300">{hw.arduino_ide.fqbn_mission2}</p>
              <div className="mt-2 grid grid-cols-2 gap-2 text-[11px] text-slate-300">
                <span>Board: {hw.arduino_ide.board_menu}</span>
                <span>Core: {hw.arduino_ide.esp32_core_version_installed}</span>
                <span>Flash: {hw.arduino_ide.mission2_settings_verified.Flash_Size}</span>
                <span>PSRAM: {hw.arduino_ide.mission2_settings_verified.PSRAM}</span>
              </div>
            </div>

            <div className="rounded-lg border border-amber-500/30 bg-amber-950/15 p-3">
              <p className="font-semibold text-amber-300">Observed Hardware Constraints</p>
              <ul className="mt-1.5 list-disc space-y-1 pl-4 text-[11px] text-slate-300">
                <li>Native USB CDC (<code className="text-amber-200">COM11</code>) overflows its 32 KB RX buffer at unthrottled bursts (&ge;8&times; real-time / &ge;256 KB/s).</li>
                <li>WCH UART bridge (<code className="text-amber-200">COM12</code>) caps at ~194.7 kB/s (2M baud); 115,200 baud cannot carry 16 kHz audio in real time.</li>
                <li>Audio clips are synthesized in Python (<code className="text-amber-200">team_audio.py</code>) with simulated room hum/whine rather than a live MEMS mic.</li>
              </ul>
            </div>
          </div>
        </SectionCard>
      </div>
    </div>
  );
}

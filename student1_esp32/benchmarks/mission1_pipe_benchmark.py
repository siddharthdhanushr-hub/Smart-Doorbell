"""
Student 1 - Phase 2 / Mission 1 Hardware Benchmark Runner
Runs repeatable throughput, baud-rate, data-type, real-time, and packet-size
experiments on the physical ESP32-S3 via edge_ai_assignment2/board_link.py.
Never fabricates results: only records runs on connected ports.
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

REPO_ROOT = Path(__file__).resolve().parents[2]
ASSIGNMENT_DIR = REPO_ROOT.parent / "edge_ai_assignment2"
sys.path.insert(0, str(ASSIGNMENT_DIR))
sys.path.insert(0, str(REPO_ROOT))

import team_audio as ta  # type: ignore
from board_link import Board  # type: ignore
from student2_python.preprocessing.audio_codec import pack  # type: ignore


def run_single(
    board: Board,
    port_label: str,
    port_name: str,
    baud: int,
    test_group: str,
    clip_x: np.ndarray,
    fs: int,
    fmt: str,
    speed: float,
    samples_per_packet: int,
    repeat_idx: int,
) -> Dict[str, Any]:
    payload = pack(clip_x, fmt=fmt, scale=1.0)
    r = board.stream(
        payload,
        fs=fs,
        fmt=fmt,
        scale=1.0,
        feat=False,
        store="none",
        speed=speed,
        samples_per_packet=samples_per_packet,
    )
    b = r["board"] or {}
    board_ms = b.get("ms", 0) or 0
    laptop_s = r["send_seconds"]
    board_s = board_ms / 1000.0 if board_ms > 0 else laptop_s
    bps_laptop = r["bytes_sent"] / laptop_s if laptop_s > 0 else 0.0
    bps_board = r["bytes_sent"] / board_s if board_s > 0 else 0.0
    n_samples = len(clip_x)
    sps_board = n_samples / board_s if board_s > 0 else 0.0

    return {
        "test_group": test_group,
        "port_label": port_label,
        "port": port_name,
        "baud": baud,
        "repeat": repeat_idx,
        "fs": fs,
        "fmt": fmt,
        "speed": speed,
        "samples_per_packet": samples_per_packet,
        "bytes_sent": r["bytes_sent"],
        "packets_sent": r["packets_sent"],
        "send_seconds": round(laptop_s, 6),
        "board_ms": board_ms,
        "throughput_laptop_bps": round(bps_laptop, 2),
        "throughput_board_bps": round(bps_board, 2),
        "effective_samples_per_s": round(sps_board, 2),
        "frames_ok": b.get("frames_ok"),
        "bad_crc": b.get("bad_crc"),
        "bad_len": b.get("bad_len"),
        "seq_gaps": b.get("seq_gaps"),
        "dup": b.get("dup"),
        "samples_rx": b.get("samples"),
        "uart_errors": b.get("uart_errors"),
        "why": b.get("why"),
    }


def benchmark_port(
    port_label: str,
    port_name: str,
    bauds: List[int],
    repeats: int,
    rows: List[Dict[str, Any]],
) -> None:
    clip_16k = ta.get_clip(1, 0, fs=16000, antialias=True)
    clip_8k = ta.get_clip(1, 0, fs=8000, antialias=True)

    # 1. Speed=0 throughput vs baud (i16, 16 kHz, 320 samples/packet, 2 seconds payload for steady timing)
    clip_2s = np.concatenate([clip_16k, clip_16k])
    b = Board(port_name, baud=921600)
    try:
        assert b.ping(), f"PING failed on {port_name}"
        for baud in bauds:
            if port_label == "COM":
                b.set_baud(baud)
            for rep in range(1, repeats + 1):
                row = run_single(
                    b, port_label, port_name, baud, "baud_throughput",
                    clip_2s, 16000, "i16", speed=0.0, samples_per_packet=320, repeat_idx=rep,
                )
                rows.append(row)
                print(f"[{port_label}] baud={baud} rep={rep}: laptop={row['throughput_laptop_bps']:.0f} B/s, board={row['throughput_board_bps']:.0f} B/s, gaps={row['seq_gaps']}, crc={row['bad_crc']}")
        if port_label == "COM" and bauds[-1] != 921600:
            b.set_baud(921600)

        # 2. Data-type throughput at speed=0 (at 921600 for COM, native for USB)
        for fmt in ("f32", "i16", "i8"):
            for rep in range(1, repeats + 1):
                row = run_single(
                    b, port_label, port_name, 921600, "datatype_speed0",
                    clip_2s, 16000, fmt, speed=0.0, samples_per_packet=320, repeat_idx=rep,
                )
                rows.append(row)
                print(f"[{port_label}] dtype={fmt} speed=0 rep={rep}: board={row['throughput_board_bps']:.0f} B/s, sps={row['effective_samples_per_s']:.0f}")

        # 3. Real-time table at speed=1.0
        rt_cases = [
            (16000, clip_16k, "f32"),
            (16000, clip_16k, "i16"),
            (16000, clip_16k, "i8"),
            (8000, clip_8k, "i16"),
            (8000, clip_8k, "i8"),
        ]
        # Test at 115200 and 921600 on COM, or native on USB
        rt_bauds = [115200, 921600] if port_label == "COM" else [921600]
        for baud in rt_bauds:
            if port_label == "COM":
                b.set_baud(baud)
            for fs, x, fmt in rt_cases:
                row = run_single(
                    b, port_label, port_name, baud, "realtime_speed1",
                    x, fs, fmt, speed=1.0, samples_per_packet=320, repeat_idx=1,
                )
                rows.append(row)
                print(f"[{port_label}] RT baud={baud} fs={fs} fmt={fmt}: rx={row['samples_rx']}/{len(x)}, ms={row['board_ms']}, gaps={row['seq_gaps']}, uart_err={row['uart_errors']}")
        if port_label == "COM":
            b.set_baud(921600)

        # 4. samples_per_packet experiment (8, 64, 320, 1024)
        for spp in (8, 64, 320, 1024):
            for rep in range(1, repeats + 1):
                row = run_single(
                    b, port_label, port_name, 921600, "packet_size",
                    clip_16k, 16000, "i16", speed=0.0, samples_per_packet=spp, repeat_idx=rep,
                )
                rows.append(row)
                print(f"[{port_label}] spp={spp} rep={rep}: pkts={row['packets_sent']}, board={row['throughput_board_bps']:.0f} B/s, gaps={row['seq_gaps']}")
    finally:
        b.close()


def generate_plots(rows: List[Dict[str, Any]], out_dir: Path) -> None:
    # Plot 1: Speed vs Baud (COM & USB)
    baud_rows = [r for r in rows if r["test_group"] == "baud_throughput"]
    if baud_rows:
        fig, ax = plt.subplots(figsize=(7.5, 4.5))
        for label in sorted(set(r["port_label"] for r in baud_rows)):
            sub = [r for r in baud_rows if r["port_label"] == label]
            bauds = sorted(set(r["baud"] for r in sub))
            means = [np.mean([r["throughput_board_bps"] for r in sub if r["baud"] == bd]) / 1000.0 for bd in bauds]
            stds = [np.std([r["throughput_board_bps"] for r in sub if r["baud"] == bd]) / 1000.0 for bd in bauds]
            ax.errorbar([str(bd) for bd in bauds], means, yerr=stds, marker="o", capsize=4, label=f"{label} port (board-measured)")
        ax.set_xlabel("Configured Baud Rate (bps)")
        ax.set_ylabel("Throughput (kB/s)")
        ax.set_title("Mission 1: ESP32-S3 Uplink Throughput vs Baud Rate")
        ax.grid(True, alpha=0.3)
        ax.legend()
        fig.tight_layout()
        fig.savefig(out_dir / "mission1_speed_vs_baud.png", dpi=150)
        plt.close(fig)

    # Plot 2: samples_per_packet effect
    pkt_rows = [r for r in rows if r["test_group"] == "packet_size"]
    if pkt_rows:
        fig, ax = plt.subplots(figsize=(7.5, 4.5))
        for label in sorted(set(r["port_label"] for r in pkt_rows)):
            sub = [r for r in pkt_rows if r["port_label"] == label]
            spps = sorted(set(r["samples_per_packet"] for r in sub))
            means = [np.mean([r["throughput_board_bps"] for r in sub if r["samples_per_packet"] == s]) / 1000.0 for s in spps]
            ax.plot([str(s) for s in spps], means, marker="s", label=f"{label} port")
        ax.set_xlabel("samples_per_packet (int16)")
        ax.set_ylabel("Effective Audio Throughput (kB/s)")
        ax.set_title("Mission 1: Effect of Packet Payload Size (13 B Header+CRC Overhead)")
        ax.grid(True, alpha=0.3)
        ax.legend()
        fig.tight_layout()
        fig.savefig(out_dir / "mission1_packet_size.png", dpi=150)
        plt.close(fig)


def main() -> None:
    ap = argparse.ArgumentParser(description="Run Mission 1 ESP32-S3 benchmarks.")
    ap.add_argument("--com-port", default=None, help="UART bridge COM port (e.g. COM12)")
    ap.add_argument("--usb-port", default=None, help="Native USB CDC COM port (e.g. COM11)")
    ap.add_argument("--repeats", type=int, default=3)
    ap.add_argument("--merge-existing", action="store_true", help="Keep prior rows for ports not run in this invocation")
    args = ap.parse_args()

    if not args.com_port and not args.usb_port:
        ap.error("Provide at least --com-port and/or --usb-port")

    bench_dir = REPO_ROOT / "student1_esp32" / "benchmarks"
    logs_dir = REPO_ROOT / "student1_esp32" / "logs"
    bench_dir.mkdir(parents=True, exist_ok=True)
    logs_dir.mkdir(parents=True, exist_ok=True)
    csv_path = bench_dir / "mission1_throughput.csv"

    rows: List[Dict[str, Any]] = []
    run_labels = set()
    if args.com_port:
        run_labels.add("COM")
    if args.usb_port:
        run_labels.add("USB")

    if args.merge_existing and csv_path.exists():
        with csv_path.open("r", newline="", encoding="utf-8") as f:
            for r in csv.DictReader(f):
                if r["port_label"] not in run_labels:
                    for int_k in ("baud", "repeat", "fs", "samples_per_packet", "bytes_sent", "packets_sent", "board_ms", "frames_ok", "bad_crc", "bad_len", "seq_gaps", "dup", "samples_rx", "uart_errors"):
                        r[int_k] = int(r[int_k]) if r[int_k] not in ("", "None") else 0
                    for flt_k in ("speed", "send_seconds", "throughput_laptop_bps", "throughput_board_bps", "effective_samples_per_s"):
                        r[flt_k] = float(r[flt_k])
                    rows.append(r)

    if args.com_port:
        benchmark_port("COM", args.com_port, [115200, 921600, 2000000], args.repeats, rows)
    if args.usb_port:
        benchmark_port("USB", args.usb_port, [115200, 921600, 2000000], args.repeats, rows)

    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    json_path = logs_dir / "mission1_pipe_results.json"
    json_path.write_text(
        json.dumps(
            {
                "timestamp": datetime.now().isoformat(),
                "com_port": args.com_port or next((r["port"] for r in rows if r["port_label"] == "COM"), None),
                "usb_port": args.usb_port or next((r["port"] for r in rows if r["port_label"] == "USB"), None),
                "repeats": args.repeats,
                "runs": rows,
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    generate_plots(rows, bench_dir)
    print(f"Saved {len(rows)} benchmark rows to {csv_path}")


if __name__ == "__main__":
    main()

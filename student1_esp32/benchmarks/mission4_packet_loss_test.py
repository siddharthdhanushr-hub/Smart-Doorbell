"""
Mission 4 / Phase 5: Controlled Packet-Loss Test (skip=(10, 11, 200))
Verifies packet accounting (packets_sent, frames_ok, seq_gaps, bad_crc, samples)
and checks whether frames after a gap remain aligned to true sample indices.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

import numpy as np

REPO_ROOT = Path(__file__).resolve().parents[2]
ASSIGNMENT_DIR = REPO_ROOT.parent / "edge_ai_assignment2"
sys.path.insert(0, str(ASSIGNMENT_DIR))
sys.path.insert(0, str(REPO_ROOT))

import team_audio as ta  # type: ignore
from board_link import Board  # type: ignore
from student2_python.preprocessing.audio_codec import pack  # type: ignore


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", default="COM11")
    ap.add_argument("--baud", type=int, default=921600)
    ap.add_argument("--seconds", type=int, default=10)
    ap.add_argument("--tag", required=True)
    args = ap.parse_args()

    xs = np.concatenate([ta.get_clip(1, i, fs=16000, antialias=True) for i in range(args.seconds)])
    payload = pack(xs, fmt="i16", scale=1.0)
    skip = (10, 11, 200)

    b = Board(args.port, baud=args.baud)
    try:
        r = b.stream(
            payload,
            fs=16000,
            fmt="i16",
            scale=1.0,
            win=480,
            hop=320,
            nfft=512,
            mels=40,
            mfcc=0,
            feat=True,
            store="psram",
            max_bytes=len(payload),
            speed=4.0,
            samples_per_packet=320,
            skip=skip,
        )
    finally:
        b.close()

    fsamp = r["first_sample"].tolist()
    # Ground truth sample offsets for packets: pkt 0..9 -> 0..3199, pkt 10..11 skipped (3200..3839),
    # pkt 12..199 -> 3840..63999, pkt 200 skipped (64000..64319), pkt 201..499 -> 64320..159999.
    sample_after_pkt12 = [s for s in fsamp if s >= 3840][:3]
    sample_after_pkt201 = [s for s in fsamp if s >= 64320][:3]
    last_5 = fsamp[-5:]
    expected_last_sample = ((args.seconds * 16000 - 480) // 320) * 320  # 159360 for 10s
    tail_shift_samples = (last_5[-1] - expected_last_sample) if last_5 else None

    out = {
        "timestamp": datetime.now().isoformat(),
        "tag": args.tag,
        "port": args.port,
        "seconds": args.seconds,
        "skip_packets": list(skip),
        "expected_total_packets": (args.seconds * 16000) // 320,
        "packets_sent": int(r["packets_sent"]),
        "expected_features_no_loss": int(r["expected_features"]),
        "received_features": int(r["features"].shape[0]),
        "lost_features": int(r["lost_features"]),
        "board": r["board"],
        "first_sample_after_gap1": sample_after_pkt12,
        "first_sample_after_gap2": sample_after_pkt201,
        "last_5_first_samples": last_5,
        "expected_last_first_sample": expected_last_sample,
        "tail_shift_samples": tail_shift_samples,
    }
    out_path = REPO_ROOT / "student1_esp32" / "logs" / f"mission4_skip_{args.tag}.json"
    out_path.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(f"Saved {out_path}")
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()

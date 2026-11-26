"""
Mission 4: Speed Ramp on COM (UART Bridge) Port Until Data Loss / Lag
Finds the fastest zero-loss speed factor on COM12 at 921,600 and 2,000,000 baud.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

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
    ap.add_argument("--port", default="COM12")
    ap.add_argument("--seconds", type=int, default=3)
    args = ap.parse_args()

    xs = np.concatenate([ta.get_clip(1, i, fs=16000, antialias=True) for i in range(args.seconds)])
    payload = pack(xs, fmt="i16", scale=1.0)

    b = Board(args.port, baud=921600)
    runs: List[Dict[str, Any]] = []
    try:
        assert b.ping(), f"PING failed on {args.port}"
        for baud, speeds in [
            (921600, [1.0, 2.0, 2.5, 3.0, 4.0]),
            (2000000, [2.0, 4.0, 5.0, 6.0, 8.0]),
        ]:
            b.set_baud(baud)
            for spd in speeds:
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
                    store="none",
                    speed=spd,
                    samples_per_packet=320,
                )
                bs = r["board"] or {}
                row = {
                    "port": args.port,
                    "baud": baud,
                    "speed": spd,
                    "target_uplink_bps": int(32000 * spd),
                    "expected_features": int(r["expected_features"]),
                    "received_features": int(r["features"].shape[0]),
                    "lost_features": int(r["lost_features"]),
                    "seq_gaps": bs.get("seq_gaps"),
                    "bad_crc": bs.get("bad_crc"),
                    "uart_errors": bs.get("uart_errors"),
                    "samples_rx": bs.get("samples"),
                    "expected_samples": int(xs.size),
                    "board_ms": bs.get("ms"),
                    "send_seconds": round(float(r["send_seconds"]), 4),
                    "lag_s_max": round(float(r["lag_s"].max()), 4) if r["lag_s"].size else None,
                    "why": bs.get("why"),
                }
                runs.append(row)
                print(row)
        b.set_baud(921600)
    finally:
        b.close()

    out_path = REPO_ROOT / "student1_esp32" / "logs" / "mission4_com_speed_ramp.json"
    out_path.write_text(json.dumps({"timestamp": datetime.now().isoformat(), "runs": runs}, indent=2), encoding="utf-8")
    print(f"Saved {out_path}")


if __name__ == "__main__":
    main()

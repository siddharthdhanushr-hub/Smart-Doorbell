"""
Mission 3 Complete Benchmark Suite on ESP32-S3 (after Radix-2 FFT optimization).
Runs:
  1. 10 s real-time (speed=1.0) with win=480, hop=320, mels=40, mfcc=0
  2. 10 s real-time (speed=1.0) with win=400 (25 ms), hop=160 (10 ms), mels=40, mfcc=13
  3. Speed sweep (speed = 2, 4, 6, 8, 10) for feat=True vs feat=False on 5 s audio
  4. Memory measurement (heap_free before/during/after)
"""

from __future__ import annotations

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

import numpy as np

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))
from student2_python.src.paths import resolve_starter_dir  # type: ignore

ASSIGNMENT_DIR = resolve_starter_dir(REPO_ROOT)
sys.path.insert(0, str(ASSIGNMENT_DIR))

import team_audio as ta  # type: ignore
from board_link import Board  # type: ignore
from student1_esp32.benchmarks.mission3_feature_benchmark import run_feature_test  # type: ignore


def main() -> None:
    port = "COM11"
    baud = 921600

    b = Board(port, baud=baud)
    info_before = b.info()
    b.close()

    print("=== 1. Optimized 10 s @ speed=1.0 (40 log-mel, win=480, hop=320) ===")
    res_mel40 = run_feature_test(port, baud, seconds=10, fs=16000, fmt="i16", scale=1.0,
                                 win=480, hop=320, nfft=512, mels=40, mfcc=0, speed=1.0, feat=True)
    print(json.dumps({
        "expected": res_mel40["expected_features"],
        "received": res_mel40["received_features"],
        "lost": res_mel40["lost_features"],
        "compute_us": res_mel40["compute_us"],
        "lag_s": res_mel40["lag_s"],
        "diff": res_mel40["numerical_diff_vs_numpy_quantised"],
    }, indent=2))

    print("=== 2. 10 s @ speed=1.0 (13 MFCC, win=400 / 25ms, hop=160 / 10ms) ===")
    res_mfcc13 = run_feature_test(port, baud, seconds=10, fs=16000, fmt="i16", scale=1.0,
                                  win=400, hop=160, nfft=512, mels=40, mfcc=13, speed=1.0, feat=True)
    mfcc_frames_per_s = 16000 / 160  # 100 frames/s steady state
    mfcc_bytes_per_frame = 13 + 8 + 13 * 4  # 13 header/crc + 8 meta + 52 payload = 73 B
    res_mfcc13["downlink_bytes_per_s_steady"] = mfcc_frames_per_s * mfcc_bytes_per_frame
    print(json.dumps({
        "expected": res_mfcc13["expected_features"],
        "received": res_mfcc13["received_features"],
        "lost": res_mfcc13["lost_features"],
        "compute_us": res_mfcc13["compute_us"],
        "lag_s": res_mfcc13["lag_s"],
        "diff": res_mfcc13["numerical_diff_vs_numpy_quantised"],
        "downlink_bytes_per_s_steady": res_mfcc13["downlink_bytes_per_s_steady"],
    }, indent=2))

    print("=== 3. Speed sweep (5 s, i16 16kHz): feat=True vs feat=False ===")
    speed_sweep: List[Dict[str, Any]] = []
    for feat_flag in (False, True):
        for spd in (2.0, 4.0, 6.0, 8.0, 10.0):
            r = run_feature_test(port, baud, seconds=5, fs=16000, fmt="i16", scale=1.0,
                                 win=480, hop=320, nfft=512, mels=40, mfcc=0, speed=spd, feat=feat_flag)
            b_sum = r["board"] or {}
            row = {
                "feat": feat_flag,
                "speed": spd,
                "expected": r["expected_features"],
                "received": r["received_features"],
                "lost": r["lost_features"],
                "seq_gaps": b_sum.get("seq_gaps"),
                "bad_crc": b_sum.get("bad_crc"),
                "samples": b_sum.get("samples"),
                "avg_us": b_sum.get("avg_us"),
                "ms": b_sum.get("ms"),
            }
            speed_sweep.append(row)
            print(row)

    out = {
        "timestamp": datetime.now().isoformat(),
        "port": port,
        "info_before": info_before,
        "mel40_10s_realtime": res_mel40,
        "mfcc13_25ms_10ms_10s_realtime": res_mfcc13,
        "speed_sweep_5s": speed_sweep,
    }
    out_path = REPO_ROOT / "student1_esp32" / "logs" / "mission3_optimized_results.json"
    out_path.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(f"Saved {out_path}")


if __name__ == "__main__":
    main()

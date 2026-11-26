"""
Mission 3 / Phase 4 ESP32-S3 Feature Extraction Benchmark Runner.
Measures compute_us, lag_s, dropped frames, numerical difference vs NumPy
on the exact same quantised samples, and max real-time speed factor.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

import numpy as np

REPO_ROOT = Path(__file__).resolve().parents[2]
ASSIGNMENT_DIR = REPO_ROOT.parent / "edge_ai_assignment2"
sys.path.insert(0, str(ASSIGNMENT_DIR))
sys.path.insert(0, str(REPO_ROOT))

import team_audio as ta  # type: ignore
from board_link import Board  # type: ignore
from student2_python.logmel.reference_logmel import features  # type: ignore
from student2_python.preprocessing.audio_codec import pack, unpack  # type: ignore


def run_feature_test(
    port: str,
    baud: int,
    seconds: int,
    fs: int,
    fmt: str,
    scale: float,
    win: int,
    hop: int,
    nfft: int,
    mels: int,
    mfcc: int,
    speed: float,
    feat: bool = True,
) -> Dict[str, Any]:
    clips = [ta.get_clip(1, i % 144, fs=fs, antialias=True) for i in range(seconds)]
    xs = np.concatenate(clips)
    payload = pack(xs, fmt=fmt, scale=scale)
    xhat = unpack(payload, fmt=fmt, scale=scale)
    ref_feats, ref_first = features(xhat, fs=fs, win=win, hop=hop, nfft=nfft, mels=mels, mfcc=mfcc)

    b = Board(port, baud=baud)
    try:
        r = b.stream(
            payload,
            fs=fs,
            fmt=fmt,
            scale=scale,
            win=win,
            hop=hop,
            nfft=nfft,
            mels=mels,
            mfcc=mfcc,
            feat=feat,
            store="none",
            speed=speed,
            samples_per_packet=320,
        )
    finally:
        b.close()

    esp_feats = r["features"]
    esp_first = r["first_sample"]
    diff_summary: Dict[str, Any] = {}
    if feat and esp_feats.shape[0] > 0:
        # Match by first_sample in case frames were lost
        ref_map = {int(s): idx for idx, s in enumerate(ref_first)}
        matched_esp = []
        matched_ref = []
        for i, s in enumerate(esp_first):
            if int(s) in ref_map:
                matched_esp.append(esp_feats[i])
                matched_ref.append(ref_feats[ref_map[int(s)]])
        if matched_esp:
            a = np.array(matched_esp, dtype=np.float64)
            ref_a = np.array(matched_ref, dtype=np.float64)
            abs_err = np.abs(a - ref_a)
            diff_summary = {
                "matched_frames": len(matched_esp),
                "max_abs_diff_db": round(float(abs_err.max()), 6),
                "mean_abs_diff_db": round(float(abs_err.mean()), 6),
                "rmse_db": round(float(np.sqrt(np.mean((a - ref_a) ** 2))), 6),
                "within_0_05_db": bool(abs_err.max() <= 0.05),
            }

    cu = r["compute_us"]
    lg = r["lag_s"]
    return {
        "timestamp": datetime.now().isoformat(),
        "port": port,
        "seconds": seconds,
        "fs": fs,
        "fmt": fmt,
        "scale": scale,
        "win": win,
        "hop": hop,
        "nfft": nfft,
        "mels": mels,
        "mfcc": mfcc,
        "feat": feat,
        "speed": speed,
        "expected_features": int(r["expected_features"]),
        "received_features": int(esp_feats.shape[0]),
        "lost_features": int(r["lost_features"]),
        "bad_crc_back": int(r["bad_crc_back"]),
        "send_seconds": round(float(r["send_seconds"]), 4),
        "compute_us": {
            "min": int(cu.min()) if cu.size else None,
            "mean": round(float(cu.mean()), 2) if cu.size else None,
            "max": int(cu.max()) if cu.size else None,
        },
        "lag_s": {
            "min": round(float(lg.min()), 4) if lg.size else None,
            "mean": round(float(lg.mean()), 4) if lg.size else None,
            "max": round(float(lg.max()), 4) if lg.size else None,
        },
        "numerical_diff_vs_numpy_quantised": diff_summary,
        "board": r["board"],
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", required=True)
    ap.add_argument("--baud", type=int, default=921600)
    ap.add_argument("--seconds", type=int, default=10)
    ap.add_argument("--fs", type=int, default=16000)
    ap.add_argument("--fmt", default="i16")
    ap.add_argument("--scale", type=float, default=1.0)
    ap.add_argument("--win", type=int, default=480)
    ap.add_argument("--hop", type=int, default=320)
    ap.add_argument("--nfft", type=int, default=512)
    ap.add_argument("--mels", type=int, default=40)
    ap.add_argument("--mfcc", type=int, default=0)
    ap.add_argument("--speed", type=float, default=1.0)
    ap.add_argument("--no-feat", action="store_true")
    ap.add_argument("--tag", default="run")
    args = ap.parse_args()

    res = run_feature_test(
        port=args.port,
        baud=args.baud,
        seconds=args.seconds,
        fs=args.fs,
        fmt=args.fmt,
        scale=args.scale,
        win=args.win,
        hop=args.hop,
        nfft=args.nfft,
        mels=args.mels,
        mfcc=args.mfcc,
        speed=args.speed,
        feat=not args.no_feat,
    )
    logs_dir = REPO_ROOT / "student1_esp32" / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)
    out_path = logs_dir / f"mission3_{args.tag}.json"
    out_path.write_text(json.dumps(res, indent=2), encoding="utf-8")
    print(f"Saved {out_path}")
    print(json.dumps(res, indent=2))


if __name__ == "__main__":
    main()

"""
Student 2 - Phase 1: Dataset Inspection & Manifest Generator
Team 1 (Paradise) - AI255TBD Edge AI Module 2 ("The Doorbell's Ears")

Inspects all 144 clips generated deterministically by edge_ai_assignment2/team_audio.py
without modifying team_audio.py or speech_pool.npz.
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

import numpy as np


def _load_team_audio(assignment_dir: Path):
    if not assignment_dir.exists():
        raise FileNotFoundError(f"Assignment directory not found: {assignment_dir}")
    if str(assignment_dir) not in sys.path:
        sys.path.insert(0, str(assignment_dir))
    import team_audio as ta  # type: ignore
    return ta


def inspect_dataset(team: int, fs: int, antialias: bool, assignment_dir: Path) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    ta = _load_team_audio(assignment_dir)
    clips = ta.clip_list(team)
    pool = ta._pool()
    team_room = ta._team(team)

    rows: list[dict[str, Any]] = []
    label_counts: Counter[str] = Counter()
    pool_indices: list[int] = []
    invalid_clips: list[int] = []

    for clip_id, label in clips:
        x = ta.get_clip(team, clip_id, fs=fs, antialias=antialias)
        finite = bool(np.all(np.isfinite(x)))
        expected_len = fs
        length_ok = int(x.size) == expected_len
        peak = float(np.max(np.abs(x))) if x.size else 0.0
        rms = float(np.sqrt(np.mean(np.square(x.astype(np.float64))))) if x.size else 0.0
        clipped = bool(peak >= 1.0)
        valid = finite and length_ok

        if not valid:
            invalid_clips.append(clip_id)

        if label != "_silence":
            pool_idx = int(ta._recording(team, clip_id))
            pool_indices.append(pool_idx)
            pool_word = str(pool["word"][pool_idx])
            pool_voice = str(pool["voice"][pool_idx])
        else:
            pool_idx = -1
            pool_word = "_silence"
            pool_voice = "none"

        label_counts[label] += 1
        rows.append(
            {
                "clip_id": clip_id,
                "source": "edge_ai_assignment2/team_audio.py",
                "label": label,
                "sample_rate": fs,
                "num_channels": 1,
                "duration_s": round(x.size / fs, 6),
                "sample_count": int(x.size),
                "format": str(x.dtype),
                "antialias": antialias,
                "pool_index": pool_idx,
                "pool_word": pool_word,
                "pool_voice": pool_voice,
                "peak_abs": round(peak, 6),
                "rms": round(rms, 6),
                "clipped": clipped,
                "valid": valid,
            }
        )

    duplicate_pool_indices = len(pool_indices) - len(set(pool_indices))
    summary = {
        "team": team,
        "fs": fs,
        "antialias": antialias,
        "total_clips": len(rows),
        "expected_clips": 144,
        "valid_clips": len(rows) - len(invalid_clips),
        "invalid_clip_ids": invalid_clips,
        "class_distribution": dict(label_counts),
        "duplicate_non_silence_pool_recordings": duplicate_pool_indices,
        "team_room_parameters": team_room,
        "speech_pool_total_recordings": int(len(pool["word"])),
        "speech_pool_sample_rate": int(pool["sr"]),
        "speech_pool_dtype": str(pool["audio"].dtype),
    }
    return rows, summary


def main() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    if str(repo_root) not in sys.path:
        sys.path.insert(0, str(repo_root))
    from student2_python.src.paths import resolve_starter_dir  # type: ignore
    default_assignment_dir = resolve_starter_dir(repo_root)

    ap = argparse.ArgumentParser(description="Inspect Team 1 audio dataset and generate manifest.")
    ap.add_argument("--team", type=int, default=1)
    ap.add_argument("--fs", type=int, default=16000)
    ap.add_argument("--no-antialias", action="store_true")
    ap.add_argument("--assignment-dir", type=Path, default=default_assignment_dir)
    args = ap.parse_args()

    antialias = not args.no_antialias
    rows, summary = inspect_dataset(args.team, args.fs, antialias, args.assignment_dir)

    dataset_dir = repo_root / "dataset"
    dataset_dir.mkdir(parents=True, exist_ok=True)

    manifest_path = dataset_dir / "dataset_manifest.csv"
    if not rows:
        raise RuntimeError("No clips returned by inspect_dataset()")
    with manifest_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    summary_path = dataset_dir / "dataset_validation.json"
    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    print(f"Wrote manifest: {manifest_path} ({len(rows)} clips)")
    print(f"Wrote validation summary: {summary_path}")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()

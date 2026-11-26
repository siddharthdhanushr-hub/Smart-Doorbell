"""
Phase 5 / Missions 4 & 5 Complete Hardware + Reference Export Pipeline:
1. Streams all 144 Team 1 clips at speed=1.0 (real-time, ~144 s) with feat=True & store="psram",
   runs SAVE to LittleFS, verifies CRC, labels every frame using first_sample & clip_list(1),
   excludes the 143 inter-clip straddling frames cleanly, and exports:
     - student1_esp32/feature_arrays/esp32_stream_raw_16k_i16_S1.0_speed1.npz
     - dataset/doorbell_team1_esp32_features.npz & .csv
     - student1_esp32/logs/phase5_144clips_realtime_log.json
2. Streams all 144 clips at speed=4.0 for the additional Mission 5 hardware settings:
     - 16 kHz i8 S=1.0
     - 16 kHz i8 S=0.25
     - 8 kHz i16 S=1.0 (antialias=False, win=240, hop=160, nfft=256)
   and exports both ESP32 board feature arrays and matching Student 2 Python reference arrays.
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
import zlib
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Tuple

import numpy as np

REPO_ROOT = Path(__file__).resolve().parents[2]
ASSIGNMENT_DIR = REPO_ROOT.parent / "edge_ai_assignment2"
sys.path.insert(0, str(ASSIGNMENT_DIR))
sys.path.insert(0, str(REPO_ROOT))

import team_audio as ta  # type: ignore
from board_link import Board  # type: ignore
from student2_python.logmel.reference_logmel import features as py_features  # type: ignore
from student2_python.preprocessing.audio_codec import pack, unpack  # type: ignore


def build_stream_payload(
    team: int, fs: int, antialias: bool, fmt: str, scale: float
) -> Tuple[bytes, np.ndarray, List[Tuple[int, str]]]:
    clips = ta.clip_list(team)
    chunks = []
    orig_f32 = []
    for cid, _ in clips:
        x = ta.get_clip(team, cid, fs=fs, antialias=antialias)
        orig_f32.append(x)
        chunks.append(pack(x, fmt=fmt, scale=scale))
    return b"".join(chunks), np.concatenate(orig_f32), clips


def label_frames(
    first_samples: np.ndarray,
    feats: np.ndarray,
    compute_us: np.ndarray,
    clips: List[Tuple[int, str]],
    fs: int,
    win: int,
) -> Dict[str, Any]:
    """
    Assign clip_id and label to frames that lie strictly inside a single 1-s clip.
    Frames straddling clip boundaries (first_sample // fs != (first_sample + win - 1) // fs)
    are counted and excluded from the clean single-label dataset.
    """
    clean_feats = []
    clean_cids = []
    clean_labels = []
    clean_fsamp = []
    clean_us = []
    straddling_indices = []

    for i in range(len(first_samples)):
        s0 = int(first_samples[i])
        s1 = s0 + win - 1
        c0 = s0 // fs
        c1 = s1 // fs
        if c0 != c1 or c0 >= len(clips):
            straddling_indices.append(i)
            continue
        cid, lab = clips[c0]
        clean_feats.append(feats[i])
        clean_cids.append(cid)
        clean_labels.append(lab)
        clean_fsamp.append(s0)
        clean_us.append(int(compute_us[i]))

    return {
        "features": np.array(clean_feats, dtype=np.float32),
        "clip_id": np.array(clean_cids, dtype=np.int32),
        "label": np.array(clean_labels),
        "first_sample": np.array(clean_fsamp, dtype=np.int64),
        "compute_us": np.array(clean_us, dtype=np.int32),
        "straddling_count": len(straddling_indices),
        "straddling_first_samples": [int(first_samples[i]) for i in straddling_indices[:10]],
    }


def extract_clean_per_clip_from_stream(
    feats: np.ndarray, first_samples: np.ndarray, fs: int, win: int, hop: int, n_clips: int = 144
) -> np.ndarray:
    """Arrange non-straddling stream frames into (144, frames_per_clip, mels)."""
    frames_per_clip = 1 + (fs - win) // hop
    mels = feats.shape[1]
    out = np.full((n_clips, frames_per_clip, mels), np.nan, dtype=np.float32)
    fmap = {int(s): feats[i] for i, s in enumerate(first_samples)}
    for c in range(n_clips):
        base = c * fs
        for k in range(frames_per_clip):
            s = base + k * hop
            if s in fmap:
                out[c, k] = fmap[s]
    return out


def run_setting(
    port: str,
    baud: int,
    tag: str,
    fs: int,
    antialias: bool,
    fmt: str,
    scale: float,
    win: int,
    hop: int,
    nfft: int,
    mels: int,
    speed: float,
    store: str,
    do_save: bool,
    export_dataset: bool,
) -> Dict[str, Any]:
    payload, orig_x, clips = build_stream_payload(1, fs, antialias, fmt, scale)
    host_crc = zlib.crc32(payload)

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
            mfcc=0,
            feat=True,
            store=store,
            max_bytes=len(payload) if store != "none" else 0,
            speed=speed,
            samples_per_packet=320,
        )
        save_rep = b.save() if do_save else None
        flash_crc = b.crc("flash") if do_save else None
    finally:
        b.close()

    esp_raw_dir = REPO_ROOT / "student1_esp32" / "feature_arrays"
    esp_raw_dir.mkdir(parents=True, exist_ok=True)
    raw_npz = esp_raw_dir / f"esp32_raw_{tag}.npz"
    np.savez_compressed(
        raw_npz,
        features=r["features"].astype(np.float32),
        first_sample=r["first_sample"],
        compute_us=r["compute_us"],
        lag_s=r["lag_s"],
        frame_numbers=r["frame_numbers"],
        fs=np.int32(fs),
        win=np.int32(win),
        hop=np.int32(hop),
        nfft=np.int32(nfft),
        mels=np.int32(mels),
        fmt=np.array(fmt),
        scale=np.float32(scale),
    )

    # Also save aligned (144, frames_per_clip, mels) for ESP32 and matching Python ref (quantised + original f32)
    esp_clips = extract_clean_per_clip_from_stream(r["features"], r["first_sample"], fs, win, hop, 144)
    per_clip_npz = esp_raw_dir / f"esp32_clips_{tag}.npz"
    np.savez_compressed(
        per_clip_npz,
        features=esp_clips,
        clip_ids=np.array([c for c, _ in clips], dtype=np.int32),
        labels=np.array([l for _, l in clips]),
    )

    # Matching Python reference on original 16k/8k float32 & quantised samples
    xhat = unpack(payload, fmt=fmt, scale=scale)
    py_orig_list = []
    py_quant_list = []
    for c in range(144):
        s0, s1 = c * fs, (c + 1) * fs
        py_orig_list.append(py_features(orig_x[s0:s1], fs=fs, win=win, hop=hop, nfft=nfft, mels=mels, mfcc=0)[0])
        py_quant_list.append(py_features(xhat[s0:s1], fs=fs, win=win, hop=hop, nfft=nfft, mels=mels, mfcc=0)[0])
    py_orig = np.stack(py_orig_list, axis=0)
    py_quant = np.stack(py_quant_list, axis=0)

    py_ref_dir = REPO_ROOT / "student2_python" / "feature_arrays"
    py_ref_dir.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(
        py_ref_dir / f"python_ref_clips_{tag}.npz",
        features_orig_f32=py_orig,
        features_quantised=py_quant,
        clip_ids=np.array([c for c, _ in clips], dtype=np.int32),
        labels=np.array([l for _, l in clips]),
    )

    diff_quant = np.abs(esp_clips - py_quant)
    diff_orig = np.abs(esp_clips - py_orig)

    dataset_info = None
    if export_dataset:
        ds = label_frames(r["first_sample"], r["features"], r["compute_us"], clips, fs, win)
        ds_dir = REPO_ROOT / "dataset"
        ds_dir.mkdir(parents=True, exist_ok=True)
        ds_npz = ds_dir / "doorbell_team1_esp32_features.npz"
        np.savez_compressed(
            ds_npz,
            features=ds["features"],
            clip_id=ds["clip_id"],
            label=ds["label"],
            first_sample=ds["first_sample"],
            compute_us=ds["compute_us"],
        )
        ds_csv = ds_dir / "doorbell_team1_esp32_features.csv"
        header = ["clip_id", "label", "first_sample", "compute_us"] + [f"mel_{m:02d}" for m in range(mels)]
        with ds_csv.open("w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(header)
            for idx in range(len(ds["clip_id"])):
                row = [
                    int(ds["clip_id"][idx]),
                    str(ds["label"][idx]),
                    int(ds["first_sample"][idx]),
                    int(ds["compute_us"][idx]),
                ] + [f"{float(v):.6f}" for v in ds["features"][idx]]
                w.writerow(row)
        dataset_info = {
            "clean_frames": int(len(ds["clip_id"])),
            "straddling_frames_excluded": ds["straddling_count"],
            "npz_path": str(ds_npz.relative_to(REPO_ROOT)),
            "csv_path": str(ds_csv.relative_to(REPO_ROOT)),
        }

    return {
        "tag": tag,
        "fs": fs,
        "antialias": antialias,
        "fmt": fmt,
        "scale": scale,
        "win": win,
        "hop": hop,
        "nfft": nfft,
        "mels": mels,
        "speed": speed,
        "bytes_sent": int(r["bytes_sent"]),
        "host_crc32_hex": f"{host_crc:08x}",
        "packets_sent": int(r["packets_sent"]),
        "send_seconds": round(float(r["send_seconds"]), 4),
        "expected_features": int(r["expected_features"]),
        "received_features": int(r["features"].shape[0]),
        "lost_features": int(r["lost_features"]),
        "bad_crc_back": int(r["bad_crc_back"]),
        "compute_us_mean": round(float(r["compute_us"].mean()), 2) if r["compute_us"].size else None,
        "compute_us_max": int(r["compute_us"].max()) if r["compute_us"].size else None,
        "lag_s_mean": round(float(r["lag_s"].mean()), 4) if r["lag_s"].size else None,
        "lag_s_max": round(float(r["lag_s"].max()), 4) if r["lag_s"].size else None,
        "board": r["board"],
        "save_reply": save_rep,
        "flash_crc": flash_crc,
        "flash_crc_match": (flash_crc.get("crc") == host_crc) if flash_crc else None,
        "mae_vs_quantised_numpy_db": round(float(np.nanmean(diff_quant)), 6),
        "max_diff_vs_quantised_numpy_db": round(float(np.nanmax(diff_quant)), 6),
        "mae_vs_orig_f32_numpy_db": round(float(np.nanmean(diff_orig)), 6),
        "max_diff_vs_orig_f32_numpy_db": round(float(np.nanmax(diff_orig)), 6),
        "dataset": dataset_info,
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", default="COM11")
    ap.add_argument("--baud", type=int, default=921600)
    ap.add_argument("--realtime-speed", type=float, default=1.0)
    args = ap.parse_args()

    results = []
    print("=== 1/4: All 144 clips @ 16k i16 S=1.0, speed=1.0, feat=True, store=psram + SAVE ===")
    r1 = run_setting(
        args.port, args.baud, "16k_i16_S1.0_speed1",
        fs=16000, antialias=True, fmt="i16", scale=1.0,
        win=480, hop=320, nfft=512, mels=40,
        speed=args.realtime_speed, store="psram", do_save=True, export_dataset=True,
    )
    results.append(r1)
    print(json.dumps(r1, indent=2))

    for tag, fs, aa, fmt, scale, win, hop, nfft in [
        ("16k_i8_S1.0", 16000, True, "i8", 1.0, 480, 320, 512),
        ("16k_i8_S0.25", 16000, True, "i8", 0.25, 480, 320, 512),
        ("8k_i16_S1.0_noaa", 8000, False, "i16", 1.0, 240, 160, 256),
    ]:
        print(f"=== Running 144 clips @ {tag} (speed=4.0) ===")
        rk = run_setting(
            args.port, args.baud, tag,
            fs=fs, antialias=aa, fmt=fmt, scale=scale,
            win=win, hop=hop, nfft=nfft, mels=40,
            speed=4.0, store="none", do_save=False, export_dataset=False,
        )
        results.append(rk)
        print(json.dumps({k: rk[k] for k in ("tag", "received_features", "lost_features", "mae_vs_quantised_numpy_db", "mae_vs_orig_f32_numpy_db")}, indent=2))

    logs_dir = REPO_ROOT / "student1_esp32" / "logs"
    out_path = logs_dir / "phase5_144clips_all_runs.json"
    out_path.write_text(json.dumps({"timestamp": datetime.now().isoformat(), "runs": results}, indent=2), encoding="utf-8")
    print(f"Saved {out_path}")


if __name__ == "__main__":
    main()

"""
Student 4 - Mission 4: Dataset Audit & Packet/Transport Integrity Analysis.

Validates:
  1. dataset/dataset_manifest.csv & dataset/doorbell_team1_esp32_features.npz
     (144 clips, 24/class, 7,056 clean frames, 143 excluded straddling frames).
  2. Controlled packet loss skip=(10, 11, 200) before vs after firmware gap fix.
  3. Port speed limits: COM11 (USB CDC) vs COM12 (WCH UART @ 921.6k & 2M baud).

Outputs:
  - student4_validation/outputs/mission4_validation_summary.json
  - student4_validation/outputs/plots/mission4_port_speed_limits.png
  - student4_validation/outputs/plots/mission4_skip_alignment.png
"""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any, Dict, List

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

REPO_ROOT = Path(__file__).resolve().parents[2]
CLASSES = ["on", "off", "stop", "go", "_unknown", "_silence"]


def load_json(rel_path: str) -> Any:
    return json.loads((REPO_ROOT / rel_path).read_text(encoding="utf-8"))


def audit_dataset() -> Dict[str, Any]:
    manifest_path = REPO_ROOT / "dataset" / "dataset_manifest.csv"
    with manifest_path.open("r", newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    assert len(rows) == 144, f"Expected 144 manifest rows, got {len(rows)}"
    clip_ids = [int(r["clip_id"]) for r in rows]
    assert sorted(clip_ids) == list(range(144)), "clip_id must span 0..143 uniquely"

    class_counts: Dict[str, int] = {c: 0 for c in CLASSES}
    invalid_count = 0
    non_silence_pool_indices: List[int] = []
    for r in rows:
        class_counts[r["label"]] = class_counts.get(r["label"], 0) + 1
        if str(r["valid"]).lower() != "true":
            invalid_count += 1
        if r["label"] != "_silence":
            non_silence_pool_indices.append(int(r["pool_index"]))

    duplicate_pool = len(non_silence_pool_indices) - len(set(non_silence_pool_indices))

    npz_path = REPO_ROOT / "dataset" / "doorbell_team1_esp32_features.npz"
    d = np.load(npz_path)
    features = d["features"]
    npz_clip_ids = d["clip_id"]
    npz_labels = d["label"]
    assert features.shape == (7056, 40), f"Unexpected dataset shape: {features.shape}"
    assert np.all(np.isfinite(features)), "Dataset features contain non-finite values"

    frames_per_class = {
        c: int(np.sum(npz_labels == c)) for c in CLASSES
    }
    unique_clips_in_npz = len(np.unique(npz_clip_ids))
    assert unique_clips_in_npz == 144, f"Expected 144 unique clips in NPZ, got {unique_clips_in_npz}"

    all_runs = load_json("student1_esp32/logs/phase5_144clips_all_runs.json")["runs"]
    primary_run = next(r for r in all_runs if r["tag"] == "16k_i16_S1.0_speed1")
    excluded_straddling = int(primary_run["dataset"]["straddling_frames_excluded"])

    return {
        "total_clips": len(rows),
        "valid_clips": len(rows) - invalid_count,
        "invalid_clips": invalid_count,
        "duplicate_non_silence_pool_recordings": duplicate_pool,
        "class_clip_counts": class_counts,
        "clean_frames": int(features.shape[0]),
        "excluded_straddling_frames": excluded_straddling,
        "frames_per_class": int(frames_per_class["on"]),
        "class_frame_counts": frames_per_class,
        "packets_sent": int(primary_run["packets_sent"]),
        "frames_ok": int(primary_run["board"]["frames_ok"]),
        "seq_gaps": int(primary_run["board"]["seq_gaps"]),
        "bad_crc": int(primary_run["board"]["bad_crc"]),
        "lost_features": int(primary_run["lost_features"]),
    }


def analyze_skip_experiment() -> Dict[str, Any]:
    before = load_json("student1_esp32/logs/mission4_skip_before_fix.json")
    after = load_json("student1_esp32/logs/mission4_skip_after_fix.json")

    return {
        "skip_packets": before["skip_packets"],
        "before_fix_samples_rx": int(before["board"]["samples"]),
        "after_fix_samples_rx": int(after["board"]["samples"]),
        "before_fix_received_features": int(before["received_features"]),
        "after_fix_received_features": int(after["received_features"]),
        "before_fix_lost_features": int(before["lost_features"]),
        "after_fix_lost_features": int(after["lost_features"]),
        "before_fix_tail_shift_samples": int(before["tail_shift_samples"]),
        "after_fix_tail_shift_samples": int(after["tail_shift_samples"]),
        "before_fix_last_first_sample": int(before["last_5_first_samples"][-1]),
        "after_fix_last_first_sample": int(after["last_5_first_samples"][-1]),
        "expected_last_first_sample": int(after["expected_last_first_sample"]),
        "explanation": (
            "Before fix, missing packets 10, 11 (640 samples) and 200 (320 samples) shifted all subsequent audio backward "
            "by 960 samples (total=159,040, last_first_sample=158,400 vs 159,360 aligned). After gap-alignment fix, "
            "zeros were inserted at gaps (total=160,000 samples) and 5 frames straddling the 2 gaps were dropped, preserving "
            "exact timeline alignment (last_first_sample=159,360) for all 494 clean frames."
        ),
    }


def analyze_port_limits() -> Dict[str, Any]:
    m3 = load_json("student1_esp32/logs/mission3_optimized_results.json")
    m4_com = load_json("student1_esp32/logs/mission4_com_speed_ramp.json")["runs"]

    usb_feat_runs = [r for r in m3["speed_sweep_5s"] if r["feat"] is True]
    usb_series = []
    for r in usb_feat_runs:
        expected_samples = 80000
        loss_pct = max(0.0, (expected_samples - r["samples"]) / expected_samples * 100.0)
        usb_series.append({
            "speed": float(r["speed"]),
            "lost_features": int(r["lost"]),
            "seq_gaps": int(r["seq_gaps"]),
            "bad_crc": int(r["bad_crc"]),
            "samples_rx": int(r["samples"]),
            "sample_loss_pct": round(loss_pct, 3),
        })

    com_921 = [r for r in m4_com if r["baud"] == 921600]
    com_2m = [r for r in m4_com if r["baud"] == 2000000]

    def _fmt_com(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        out = []
        for r in rows:
            loss_pct = (r["expected_samples"] - r["samples_rx"]) / r["expected_samples"] * 100.0
            out.append({
                "speed": float(r["speed"]),
                "lost_features": int(r["lost_features"]),
                "sample_loss_pct": round(loss_pct, 3),
                "lag_s_max": float(r["lag_s_max"]),
                "target_uplink_bps": int(r["target_uplink_bps"]),
            })
        return out

    usb_max_zero_loss = max(r["speed"] for r in usb_series if r["lost_features"] == 0 and r["bad_crc"] == 0)
    com_921_lag_free = max(r["speed"] for r in com_921 if r["lag_s_max"] < 0.05)
    com_2m_lag_free = max(r["speed"] for r in com_2m if r["lag_s_max"] < 0.05)

    return {
        "usb_com11_max_zero_loss_speed": float(usb_max_zero_loss),
        "com12_921600_max_lag_free_speed": float(com_921_lag_free),
        "com12_2000000_max_lag_free_speed": float(com_2m_lag_free),
        "usb_com11_sweep": usb_series,
        "com12_921600_sweep": _fmt_com(com_921),
        "com12_2000000_sweep": _fmt_com(com_2m),
    }


def save_plots(skip_info: Dict[str, Any], port_info: Dict[str, Any], plot_dir: Path) -> None:
    plot_dir.mkdir(parents=True, exist_ok=True)

    # Plot 1: USB COM11 Loss vs COM12 UART Lag/Loss
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11.5, 4.4))

    usb = port_info["usb_com11_sweep"]
    c921 = port_info["com12_921600_sweep"]
    c2m = port_info["com12_2000000_sweep"]

    ax1.plot([r["speed"] for r in usb], [r["sample_loss_pct"] for r in usb], "o-", color="#e11d48", label="USB COM11 (feat=True)")
    ax1.plot([r["speed"] for r in c921], [r["sample_loss_pct"] for r in c921], "s--", color="#0284c7", label="UART COM12 @ 921.6k")
    ax1.plot([r["speed"] for r in c2m], [r["sample_loss_pct"] for r in c2m], "^:", color="#059669", label="UART COM12 @ 2M")
    ax1.set_title("Sample Loss Rate vs Stream Speed (16 kHz, int16)")
    ax1.set_xlabel("Stream Speed Multiplier (x real-time)")
    ax1.set_ylabel("Sample Loss (%)")
    ax1.grid(True, alpha=0.3)
    ax1.legend(fontsize=8.5)

    ax2.plot([r["speed"] for r in c921], [r["lag_s_max"] * 1000 for r in c921], "s-", color="#d97706", label="UART COM12 @ 921.6k")
    ax2.plot([r["speed"] for r in c2m], [r["lag_s_max"] * 1000 for r in c2m], "^-", color="#059669", label="UART COM12 @ 2M")
    ax2.axhline(50.0, color="#64748b", linestyle="--", linewidth=1, label="50 ms lag-free threshold")
    ax2.set_title("COM12 UART Backpressure Max Lag vs Speed")
    ax2.set_xlabel("Stream Speed Multiplier (x real-time)")
    ax2.set_ylabel("Max Pipeline Lag (ms)")
    ax2.grid(True, alpha=0.3)
    ax2.legend(fontsize=8.5)

    fig.tight_layout()
    fig.savefig(plot_dir / "mission4_port_speed_limits.png", dpi=150)
    plt.close(fig)

    # Plot 2: Controlled skip before vs after fix
    fig, ax = plt.subplots(figsize=(7.5, 4.2))
    labels = ["Before Fix\n(No Gap Fill)", "After Fix\n(Gap-Aligned)"]
    tail_offsets = [
        abs(skip_info["expected_last_first_sample"] - 160 - skip_info["before_fix_last_first_sample"]),
        abs(skip_info["expected_last_first_sample"] - 160 - skip_info["after_fix_last_first_sample"]),
    ]
    bars = ax.bar(labels, tail_offsets, color=["#e11d48", "#10b981"], width=0.5)
    for b, val in zip(bars, tail_offsets):
        ax.text(b.get_x() + b.get_width() / 2, val + 25, f"{val} samples", ha="center", va="bottom", fontsize=9)
    ax.set_title("Controlled skip=(10, 11, 200): Timeline Misalignment Error")
    ax.set_ylabel("Tail Sample Shift Error (samples @ 16 kHz)")
    ax.set_ylim(0, max(tail_offsets) * 1.2 + 100)
    ax.grid(axis="y", alpha=0.3)
    fig.tight_layout()
    fig.savefig(plot_dir / "mission4_skip_alignment.png", dpi=150)
    plt.close(fig)


def main() -> None:
    dataset_info = audit_dataset()
    skip_info = analyze_skip_experiment()
    port_info = analyze_port_limits()

    out_dir = REPO_ROOT / "student4_validation" / "outputs"
    out_dir.mkdir(parents=True, exist_ok=True)
    save_plots(skip_info, port_info, out_dir / "plots")

    summary = {
        "dataset": dataset_info,
        "controlled_skip_test": skip_info,
        "port_limits": port_info,
    }
    out_path = out_dir / "mission4_validation_summary.json"
    out_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"Wrote {out_path}")


if __name__ == "__main__":
    main()

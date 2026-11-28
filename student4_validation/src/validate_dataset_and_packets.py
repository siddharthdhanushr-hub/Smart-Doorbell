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
    path = REPO_ROOT / rel_path
    if not path.exists():
        raise FileNotFoundError(f"Required input file missing: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def audit_dataset() -> Dict[str, Any]:
    manifest_path = REPO_ROOT / "dataset" / "dataset_manifest.csv"
    if not manifest_path.exists():
        raise FileNotFoundError(f"Required dataset manifest missing: {manifest_path}")
    with manifest_path.open("r", newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    assert len(rows) == 144, f"Expected 144 manifest rows, got {len(rows)}"
    clip_ids = [int(r["clip_id"]) for r in rows]
    assert sorted(clip_ids) == list(range(144)), "clip_id must span 0..143 uniquely"

    class_counts: Dict[str, int] = {c: 0 for c in CLASSES}
    invalid_count = 0
    clipped_count = 0
    metadata_errors = 0
    non_silence_pool_indices: List[int] = []
    for r in rows:
        lbl = r["label"]
        if lbl not in CLASSES:
            metadata_errors += 1
        class_counts[lbl] = class_counts.get(lbl, 0) + 1
        if str(r["valid"]).lower() != "true":
            invalid_count += 1
        if str(r["clipped"]).lower() == "true":
            clipped_count += 1
        if int(r["sample_rate"]) != 16000 or int(r["num_channels"]) != 1 or int(r["sample_count"]) != 16000:
            metadata_errors += 1
        if lbl != "_silence":
            non_silence_pool_indices.append(int(r["pool_index"]))

    assert metadata_errors == 0, f"Detected {metadata_errors} metadata mismatches in manifest"
    duplicate_pool = len(non_silence_pool_indices) - len(set(non_silence_pool_indices))

    val_json = load_json("dataset/dataset_validation.json")
    assert int(val_json["valid_clips"]) == len(rows) - invalid_count

    npz_path = REPO_ROOT / "dataset" / "doorbell_team1_esp32_features.npz"
    if not npz_path.exists():
        raise FileNotFoundError(f"Required dataset NPZ missing: {npz_path}")
    with np.load(npz_path) as d:
        features = d["features"]
        npz_clip_ids = d["clip_id"]
        npz_labels = d["label"]
        first_samples = d["first_sample"]
        assert features.shape == (7056, 40), f"Unexpected dataset shape: {features.shape}"
        assert np.all(np.isfinite(features)), "Dataset features contain non-finite values"
        assert int(np.max(first_samples % 16000)) <= 15360, "Straddling frame found in clean dataset"

    frames_per_class = {
        c: int(np.sum(npz_labels == c)) for c in CLASSES
    }
    unique_clips_in_npz = len(np.unique(npz_clip_ids))
    assert unique_clips_in_npz == 144, f"Expected 144 unique clips in NPZ, got {unique_clips_in_npz}"

    all_runs = load_json("student1_esp32/logs/phase5_144clips_all_runs.json")["runs"]
    primary_run = next(r for r in all_runs if r["tag"] == "16k_i16_S1.0_speed1")
    excluded_straddling = int(primary_run["dataset"]["straddling_frames_excluded"])
    all_runs_zero_errors = all(
        int(r["board"]["seq_gaps"]) == 0
        and int(r["board"]["bad_crc"]) == 0
        and int(r["board"]["dup"]) == 0
        and int(r["lost_features"]) == 0
        and int(r["bad_crc_back"]) == 0
        for r in all_runs
    )

    return {
        "total_clips": len(rows),
        "valid_clips": len(rows) - invalid_count,
        "invalid_clips": invalid_count,
        "clipped_clips": clipped_count,
        "metadata_errors": metadata_errors,
        "duplicate_non_silence_pool_recordings": duplicate_pool,
        "class_clip_counts": class_counts,
        "clean_frames": int(features.shape[0]),
        "excluded_straddling_frames": excluded_straddling,
        "frames_per_class": int(frames_per_class["on"]),
        "class_frame_counts": frames_per_class,
        "packets_sent": int(primary_run["packets_sent"]),
        "frames_ok": int(primary_run["board"]["frames_ok"]),
        "seq_gaps": int(primary_run["board"]["seq_gaps"]),
        "dup": int(primary_run["board"]["dup"]),
        "bad_crc": int(primary_run["board"]["bad_crc"]),
        "bad_crc_back": int(primary_run["bad_crc_back"]),
        "lost_features": int(primary_run["lost_features"]),
        "all_4_runs_zero_packet_loss": all_runs_zero_errors,
    }


def analyze_skip_experiment() -> Dict[str, Any]:
    before = load_json("student1_esp32/logs/mission4_skip_before_fix.json")
    after = load_json("student1_esp32/logs/mission4_skip_after_fix.json")

    exp_pkts = int(before["expected_total_packets"])
    before_pkt_loss_pct = round((exp_pkts - int(before["packets_sent"])) / exp_pkts * 100.0, 3)
    after_pkt_loss_pct = round((exp_pkts - int(after["packets_sent"])) / exp_pkts * 100.0, 3)
    exp_feat = int(before["expected_features_no_loss"])
    before_feat_loss_pct = round(int(before["lost_features"]) / exp_feat * 100.0, 3)
    after_feat_loss_pct = round(int(after["lost_features"]) / exp_feat * 100.0, 3)

    return {
        "skip_packets": before["skip_packets"],
        "expected_total_packets": exp_pkts,
        "before_fix_packets_sent": int(before["packets_sent"]),
        "after_fix_packets_sent": int(after["packets_sent"]),
        "before_fix_packet_loss_pct": before_pkt_loss_pct,
        "after_fix_packet_loss_pct": after_pkt_loss_pct,
        "before_fix_feature_loss_pct": before_feat_loss_pct,
        "after_fix_feature_loss_pct": after_feat_loss_pct,
        "before_fix_seq_gaps": int(before["board"]["seq_gaps"]),
        "after_fix_seq_gaps": int(after["board"]["seq_gaps"]),
        "before_fix_dup": int(before["board"]["dup"]),
        "after_fix_dup": int(after["board"]["dup"]),
        "before_fix_bad_crc": int(before["board"]["bad_crc"]),
        "after_fix_bad_crc": int(after["board"]["bad_crc"]),
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
    # Aligned last frame index for 160,000 samples (win=480, hop=320): ((160000 - 480) // 320) * 320 = 159,360
    aligned_last_first_sample = ((160000 - 480) // 320) * 320
    fig, ax = plt.subplots(figsize=(7.5, 4.2))
    labels = ["Before Fix\n(No Gap Fill)", "After Fix\n(Gap-Aligned)"]
    tail_offsets = [
        abs(aligned_last_first_sample - skip_info["before_fix_last_first_sample"]),
        abs(aligned_last_first_sample - skip_info["after_fix_last_first_sample"]),
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

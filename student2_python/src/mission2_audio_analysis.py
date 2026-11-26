"""
Mission 2 (Python / Student 2 Phase 3):
1. Aliasing experiment: 48 kHz vs 8 kHz (antialias=False vs True) on Team 1 _silence clip.
2. Quantisation SQNR experiment: int16 (S=1.0) vs int8 (S=1.0, 0.5, 0.25, 0.125) on word & silence clips.
3. All-144-clip peak/RMS/SQNR statistics to justify chosen fs, fmt, and scale S.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Dict, List

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

REPO_ROOT = Path(__file__).resolve().parents[2]
ASSIGNMENT_DIR = REPO_ROOT.parent / "edge_ai_assignment2"
sys.path.insert(0, str(ASSIGNMENT_DIR))
sys.path.insert(0, str(REPO_ROOT))

import team_audio as ta  # type: ignore
from student2_python.preprocessing.audio_codec import pack_and_reconstruct, sqnr_db  # type: ignore


def spectrum_db(x: np.ndarray, fs: int) -> tuple[np.ndarray, np.ndarray]:
    freqs = np.fft.rfftfreq(x.size, d=1.0 / fs)
    mag = np.abs(np.fft.rfft(x * np.hanning(x.size))) / (x.size / 2.0)
    db = 20.0 * np.log10(np.maximum(mag, 1e-12))
    return freqs, db


def run_aliasing_experiment(out_dir: Path) -> Dict[str, Any]:
    silence_id = next(cid for cid, lab in ta.clip_list(1) if lab == "_silence")
    x48 = ta.get_clip(1, silence_id, fs=48000, antialias=False)
    x8_raw = ta.get_clip(1, silence_id, fs=8000, antialias=False)
    x8_aa = ta.get_clip(1, silence_id, fs=8000, antialias=True)

    f48, db48 = spectrum_db(x48, 48000)
    f8r, db8r = spectrum_db(x8_raw, 8000)
    f8a, db8a = spectrum_db(x8_aa, 8000)

    # Find dominant peaks above 200 Hz (ignoring 100 Hz mains hum)
    mask48 = f48 >= 200
    peak48_hz = float(f48[mask48][np.argmax(db48[mask48])])
    peak48_db = float(np.max(db48[mask48]))

    mask8 = f8r >= 200
    peak8_raw_hz = float(f8r[mask8][np.argmax(db8r[mask8])])
    peak8_raw_db = float(np.max(db8r[mask8]))

    # True frequency recovered from nearest integer multiple of fs=8000: 1*8000 - peak8_raw_hz
    reconstructed_true_hz = 8000.0 - peak8_raw_hz
    peak8_aa_at_alias_db = float(db8a[np.argmin(np.abs(f8a - peak8_raw_hz))])

    fig, axes = plt.subplots(3, 1, figsize=(9, 8.5), sharex=False)
    axes[0].plot(f48, db48, linewidth=0.8)
    axes[0].set_title(f"Silence Clip (id={silence_id}) at 48 kHz — True Tone Peak @ {peak48_hz:.1f} Hz ({peak48_db:.1f} dB)")
    axes[0].set_ylabel("Magnitude (dB)")
    axes[0].set_xlim(0, 12000)
    axes[0].set_ylim(-110, -15)
    axes[0].grid(True, alpha=0.3)

    axes[1].plot(f8r, db8r, color="tab:red", linewidth=0.9)
    axes[1].set_title(f"8 kHz (antialias=False) — Aliased Peak @ {peak8_raw_hz:.1f} Hz ({peak8_raw_db:.1f} dB), |8000 - {peak8_raw_hz:.1f}| = {reconstructed_true_hz:.1f} Hz")
    axes[1].set_ylabel("Magnitude (dB)")
    axes[1].set_xlim(0, 4000)
    axes[1].set_ylim(-110, -15)
    axes[1].grid(True, alpha=0.3)

    axes[2].plot(f8a, db8a, color="tab:green", linewidth=0.9)
    axes[2].set_title(f"8 kHz (antialias=True) — Alias Suppressed ({peak8_aa_at_alias_db:.1f} dB @ {peak8_raw_hz:.1f} Hz)")
    axes[2].set_xlabel("Frequency (Hz)")
    axes[2].set_ylabel("Magnitude (dB)")
    axes[2].set_xlim(0, 4000)
    axes[2].set_ylim(-110, -15)
    axes[2].grid(True, alpha=0.3)

    fig.tight_layout()
    fig.savefig(out_dir / "mission2_aliasing_spectra.png", dpi=150)
    plt.close(fig)

    return {
        "silence_clip_id": silence_id,
        "peak_48khz_hz": round(peak48_hz, 2),
        "peak_48khz_db": round(peak48_db, 2),
        "peak_8khz_no_aa_hz": round(peak8_raw_hz, 2),
        "peak_8khz_no_aa_db": round(peak8_raw_db, 2),
        "reconstructed_true_freq_hz": round(reconstructed_true_hz, 2),
        "level_8khz_with_aa_at_alias_db": round(peak8_aa_at_alias_db, 2),
        "attenuation_db": round(peak8_raw_db - peak8_aa_at_alias_db, 2),
    }


def run_sqnr_experiment(out_dir: Path) -> Dict[str, Any]:
    word_id = 0  # "on"
    silence_id = next(cid for cid, lab in ta.clip_list(1) if lab == "_silence")
    x_word = ta.get_clip(1, word_id, fs=16000, antialias=True)
    x_sil = ta.get_clip(1, silence_id, fs=16000, antialias=True)

    configs = [
        ("i16", 1.0),
        ("i8", 1.0),
        ("i8", 0.5),
        ("i8", 0.25),
        ("i8", 0.125),
    ]
    single_results: List[Dict[str, Any]] = []
    for fmt, scale in configs:
        _, xhat_w = pack_and_reconstruct(x_word, fmt=fmt, scale=scale)
        _, xhat_s = pack_and_reconstruct(x_sil, fmt=fmt, scale=scale)
        clipped_w = float(np.mean(np.abs(x_word) > scale) * 100.0)
        clipped_s = float(np.mean(np.abs(x_sil) > scale) * 100.0)
        single_results.append({
            "fmt": fmt,
            "scale": scale,
            "word_sqnr_db": round(sqnr_db(x_word, xhat_w), 2),
            "word_clipped_pct": round(clipped_w, 3),
            "silence_sqnr_db": round(sqnr_db(x_sil, xhat_s), 2),
            "silence_clipped_pct": round(clipped_s, 3),
        })

    # Across all 144 clips at 16 kHz antialias=True
    all_clips = [ta.get_clip(1, cid, fs=16000, antialias=True) for cid, _ in ta.clip_list(1)]
    global_max = float(max(np.max(np.abs(x)) for x in all_clips))
    dataset_sqnr: Dict[str, Any] = {}
    for fmt, scale in [("i16", 1.0), ("i8", 1.0), ("i8", 0.5), ("i8", 0.25)]:
        sqnrs = [sqnr_db(x, pack_and_reconstruct(x, fmt=fmt, scale=scale)[1]) for x in all_clips]
        dataset_sqnr[f"{fmt}_S{scale}"] = {
            "mean_sqnr_db": round(float(np.mean(sqnrs)), 2),
            "min_sqnr_db": round(float(np.min(sqnrs)), 2),
            "max_sqnr_db": round(float(np.max(sqnrs)), 2),
        }

    # Plot SQNR bar chart
    labels = [f"{r['fmt']}\nS={r['scale']}" for r in single_results]
    x_pos = np.arange(len(labels))
    w = 0.36
    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.bar(x_pos - w / 2, [r["word_sqnr_db"] for r in single_results], width=w, label=f"Word clip (id={word_id})")
    ax.bar(x_pos + w / 2, [r["silence_sqnr_db"] for r in single_results], width=w, label=f"Silence clip (id={silence_id})")
    ax.set_xticks(x_pos)
    ax.set_xticklabels(labels)
    ax.set_ylabel("SQNR (dB)")
    ax.set_title("Mission 2: Quantisation SQNR (16 kHz, antialias=True)")
    ax.grid(True, axis="y", alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(out_dir / "mission2_sqnr_comparison.png", dpi=150)
    plt.close(fig)

    return {
        "word_clip_id": word_id,
        "word_peak_abs": round(float(np.max(np.abs(x_word))), 5),
        "silence_clip_id": silence_id,
        "silence_peak_abs": round(float(np.max(np.abs(x_sil))), 5),
        "dataset_global_peak_abs": round(global_max, 5),
        "single_clip_table": single_results,
        "all_144_clips_summary": dataset_sqnr,
    }


def main() -> None:
    out_dir = REPO_ROOT / "student2_python" / "documentation"
    out_dir.mkdir(parents=True, exist_ok=True)
    alias_res = run_aliasing_experiment(out_dir)
    sqnr_res = run_sqnr_experiment(out_dir)
    report = {
        "team": 1,
        "aliasing": alias_res,
        "sqnr": sqnr_res,
        "recommended_config": {
            "fs": 16000,
            "antialias": True,
            "fmt": "i16",
            "scale": 1.0,
            "rationale": (
                "16 kHz preserves full speech band up to 8 kHz (above Team 1's 7348 Hz whine, "
                "avoiding aliasing into speech bands), antialias=True suppresses out-of-band energy, "
                "and int16 with S=1.0 prevents any clipping (max amplitude 0.6705 < 1.0) while achieving "
                ">69 dB mean SQNR across all 144 clips at 32,000 B/s (easily real-time on both COM 921600 and USB). "
                "Total 144-clip size = 4,608,000 bytes (~4.39 MiB), which fits cleanly in 8 MB OPI PSRAM and 16 MB Flash LittleFS."
            ),
        },
    }
    json_path = out_dir / "mission2_audio_analysis.json"
    json_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()

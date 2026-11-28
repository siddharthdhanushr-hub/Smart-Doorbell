"""
Student 2 - Phase 4: Python Reference Log-Mel / MFCC Extraction
Follows edge_ai_assignment2/README.md (Section 5) and features.h:
  frame -> np.hanning(win) -> zero-pad to nfft -> |rfft|^2 / nfft
  -> HTK mel triangles (20 Hz .. fs/2) -> 10*log10(max(band, 1e-10))
  -> optional orthonormal DCT-II keeping first `mfcc` values.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Tuple

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
from student2_python.src.paths import resolve_starter_dir  # type: ignore

ASSIGNMENT_DIR = resolve_starter_dir(REPO_ROOT)
if str(ASSIGNMENT_DIR) not in sys.path:
    sys.path.insert(0, str(ASSIGNMENT_DIR))

import team_audio as ta  # type: ignore
from student2_python.preprocessing.audio_codec import pack_and_reconstruct  # type: ignore


def hz_to_mel_htk(f: np.ndarray | float) -> np.ndarray | float:
    return 2595.0 * np.log10(1.0 + np.asarray(f, dtype=np.float64) / 700.0)


def mel_to_hz_htk(m: np.ndarray | float) -> np.ndarray | float:
    return 700.0 * (np.power(10.0, np.asarray(m, dtype=np.float64) / 2595.0) - 1.0)


def build_mel_filterbank(fs: int, nfft: int, mels: int, fmin: float = 20.0) -> np.ndarray:
    nb = nfft // 2 + 1
    m0 = float(hz_to_mel_htk(fmin))
    m1 = float(hz_to_mel_htk(fs / 2.0))
    edges = np.asarray(mel_to_hz_htk(np.linspace(m0, m1, mels + 2)), dtype=np.float64)
    freqs = np.arange(nb, dtype=np.float64) * (float(fs) / float(nfft))
    fb = np.zeros((mels, nb), dtype=np.float64)
    for m in range(mels):
        lo, ce, hi = edges[m], edges[m + 1], edges[m + 2]
        up = (freqs > lo) & (freqs <= ce)
        dn = (freqs > ce) & (freqs < hi)
        fb[m, up] = (freqs[up] - lo) / (ce - lo)
        fb[m, dn] = (hi - freqs[dn]) / (hi - ce)
    return fb


def build_dct_matrix(mels: int, mfcc: int) -> np.ndarray:
    q = np.arange(mfcc, dtype=np.float64)[:, None]
    m = np.arange(mels, dtype=np.float64)[None, :]
    scale = np.where(q == 0, np.sqrt(1.0 / mels), np.sqrt(2.0 / mels))
    return scale * np.cos(np.pi * q * (2.0 * m + 1.0) / (2.0 * mels))


def features(
    x: np.ndarray,
    fs: int = 16000,
    win: int = 480,
    hop: int = 320,
    nfft: int = 512,
    mels: int = 40,
    mfcc: int = 0,
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Compute log-mel (or MFCC) features matching README Section 5 and features.h.
    Returns (feats [n_frames, out_dim] float32, first_sample [n_frames] int64).
    """
    if fs <= 40:
        raise ValueError(f"fs must be > 40 Hz, got {fs}")
    if win < 2 or hop < 1:
        raise ValueError(f"Invalid frame parameters: win={win}, hop={hop}")
    if nfft < win or (nfft & (nfft - 1)) != 0:
        raise ValueError(f"nfft ({nfft}) must be a power of 2 >= win ({win})")
    if mels < 1 or not (0 <= mfcc <= mels):
        raise ValueError(f"Invalid mel/mfcc parameters: mels={mels}, mfcc={mfcc}")

    x_arr = np.asarray(x, dtype=np.float64)
    if x_arr.size < win:
        dim = mfcc if mfcc > 0 else mels
        return np.zeros((0, dim), dtype=np.float32), np.zeros((0,), dtype=np.int64)

    n_frames = 1 + (x_arr.size - win) // hop
    first_samples = np.arange(n_frames, dtype=np.int64) * hop
    idx = first_samples[:, None] + np.arange(win, dtype=np.int64)[None, :]
    frames = x_arr[idx] * np.hanning(win)[None, :]

    spec = np.fft.rfft(frames, n=nfft, axis=1)
    power = (spec.real ** 2 + spec.imag ** 2) / float(nfft)
    fb = build_mel_filterbank(fs=fs, nfft=nfft, mels=mels)
    mel_energy = power @ fb.T
    log_mel = 10.0 * np.log10(np.maximum(mel_energy, 1e-10))

    if mfcc > 0:
        dct = build_dct_matrix(mels=mels, mfcc=mfcc)
        out = log_mel @ dct.T
    else:
        out = log_mel
    return out.astype(np.float32), first_samples


def export_dataset_reference(
    team: int = 1,
    fs: int = 16000,
    antialias: bool = True,
    win: int = 480,
    hop: int = 320,
    nfft: int = 512,
    mels: int = 40,
    mfcc: int = 0,
    fmt: str = "f32",
    scale: float = 1.0,
) -> Path:
    clips = ta.clip_list(team)
    feat_list = []
    clip_ids = []
    labels = []
    first_samples = None

    for cid, lab in clips:
        x = ta.get_clip(team, cid, fs=fs, antialias=antialias)
        if fmt != "f32":
            _, x = pack_and_reconstruct(x, fmt=fmt, scale=scale)
        f, fsamp = features(x, fs=fs, win=win, hop=hop, nfft=nfft, mels=mels, mfcc=mfcc)
        feat_list.append(f)
        clip_ids.append(cid)
        labels.append(lab)
        if first_samples is None:
            first_samples = fsamp

    arr = np.stack(feat_list, axis=0)  # (144, frames, dim)
    if first_samples is None:
        first_samples = np.zeros((0,), dtype=np.int64)
    out_dir = REPO_ROOT / "student2_python" / "feature_arrays"
    out_dir.mkdir(parents=True, exist_ok=True)
    tag = f"team{team}_{fs}hz_{fmt}_S{scale}_win{win}_hop{hop}_mels{mels}_mfcc{mfcc}"
    out_path = out_dir / f"python_ref_{tag}.npz"
    np.savez_compressed(
        out_path,
        features=arr,
        clip_ids=np.array(clip_ids, dtype=np.int32),
        labels=np.array(labels),
        first_sample=first_samples,
        fs=np.int32(fs),
        win=np.int32(win),
        hop=np.int32(hop),
        nfft=np.int32(nfft),
        mels=np.int32(mels),
        mfcc=np.int32(mfcc),
        fmt=np.array(fmt),
        scale=np.float32(scale),
    )
    return out_path


def plot_one_per_class(team: int = 1, fs: int = 16000) -> Path:
    clips = ta.clip_list(team)
    picks = [next((cid, lab) for cid, lab in clips if lab == cls) for cls in ta.CLASSES]
    fig, axes = plt.subplots(2, 3, figsize=(12, 6.5), sharex=True, sharey=True)
    im = None
    for ax, (cid, lab) in zip(axes.flat, picks):
        x = ta.get_clip(team, cid, fs=fs, antialias=True)
        f, _ = features(x, fs=fs, win=480, hop=320, nfft=512, mels=40, mfcc=0)
        im = ax.imshow(f.T, origin="lower", aspect="auto", cmap="viridis", vmin=-95, vmax=-5)
        ax.set_title(f"{lab} (clip_id={cid})")
        ax.set_xlabel("Frame (hop=20 ms)")
        ax.set_ylabel("Mel band (0..39)")
    if im is not None:
        fig.colorbar(im, ax=axes.ravel().tolist(), label="Log-mel power (dB)")
    fig.suptitle("Team 1 Log-Mel Spectrograms (16 kHz, win=480, hop=320, nfft=512, 40 mels)")
    out_dir = REPO_ROOT / "student2_python" / "documentation"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "mission3_class_spectrograms.png"
    fig.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return out_path


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--team", type=int, default=1)
    args = ap.parse_args()
    p_f32 = export_dataset_reference(team=args.team, fmt="f32", scale=1.0)
    p_i16 = export_dataset_reference(team=args.team, fmt="i16", scale=1.0)
    p_img = plot_one_per_class(team=args.team)
    print(f"Exported f32 ref: {p_f32}")
    print(f"Exported i16 ref: {p_i16}")
    print(f"Saved plot: {p_img}")


if __name__ == "__main__":
    main()

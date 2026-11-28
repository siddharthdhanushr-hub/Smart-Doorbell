"""
Student 2 - Phase 3: Complete Reusable & Batch Audio Transmission Pipeline
Connects ClipLoader + audio_codec + Board/MockBoard with full logging.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Protocol, Tuple

import numpy as np

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
from student2_python.src.paths import resolve_starter_dir  # type: ignore

ASSIGNMENT_DIR = resolve_starter_dir(REPO_ROOT)
if str(ASSIGNMENT_DIR) not in sys.path:
    sys.path.insert(0, str(ASSIGNMENT_DIR))


class ClipLoaderProtocol(Protocol):
    def clip_list(self) -> List[Tuple[int, str]]: ...

    def prepare_payload(
        self, clip_id: int, fs: int = 16000, antialias: bool = True, fmt: str = "i16", scale: float = 1.0
    ) -> Tuple[bytes, np.ndarray]: ...


def transmit_clip(
    board: Any,
    loader: ClipLoaderProtocol,
    clip_id: int,
    fs: int = 16000,
    antialias: bool = True,
    fmt: str = "i16",
    scale: float = 1.0,
    win: int = 480,
    hop: int = 320,
    nfft: int = 512,
    mels: int = 40,
    mfcc: int = 0,
    feat: bool = False,
    store: str = "none",
    max_bytes: int = 0,
    speed: float = 1.0,
    samples_per_packet: int = 320,
    skip: tuple = (),
) -> Dict[str, Any]:
    payload, x = loader.prepare_payload(clip_id, fs=fs, antialias=antialias, fmt=fmt, scale=scale)
    res = board.stream(
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
        store=store,
        max_bytes=max_bytes or len(payload),
        speed=speed,
        samples_per_packet=samples_per_packet,
        skip=skip,
    )
    return {
        "clip_id": clip_id,
        "samples": int(x.size),
        "payload_bytes": len(payload),
        "result": res,
    }


def transmit_batch(
    board: Any,
    loader: ClipLoaderProtocol,
    clip_ids: Optional[Iterable[int]] = None,
    fs: int = 16000,
    antialias: bool = True,
    fmt: str = "i16",
    scale: float = 1.0,
    win: int = 480,
    hop: int = 320,
    nfft: int = 512,
    mels: int = 40,
    mfcc: int = 0,
    feat: bool = False,
    store: str = "psram",
    speed: float = 1.0,
    samples_per_packet: int = 320,
    skip: tuple = (),
) -> Dict[str, Any]:
    clips_map = dict(loader.clip_list())
    ids = list(clip_ids) if clip_ids is not None else list(clips_map.keys())
    if not ids:
        raise ValueError("clip_ids must not be empty")
    chunks: List[bytes] = []
    meta: List[Dict[str, Any]] = []
    offset_samples = 0

    for cid in ids:
        payload, x = loader.prepare_payload(cid, fs=fs, antialias=antialias, fmt=fmt, scale=scale)
        chunks.append(payload)
        meta.append({
            "clip_id": cid,
            "label": clips_map[cid],
            "start_sample": offset_samples,
            "sample_count": int(x.size),
        })
        offset_samples += int(x.size)

    full_payload = b"".join(chunks)
    res = board.stream(
        full_payload,
        fs=fs,
        fmt=fmt,
        scale=scale,
        win=win,
        hop=hop,
        nfft=nfft,
        mels=mels,
        mfcc=mfcc,
        feat=feat,
        store=store,
        max_bytes=len(full_payload),
        speed=speed,
        samples_per_packet=samples_per_packet,
        skip=skip,
    )
    return {
        "num_clips": len(ids),
        "total_samples": offset_samples,
        "total_bytes": len(full_payload),
        "clip_index": meta,
        "stream_result": res,
    }

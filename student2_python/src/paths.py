"""Shared path resolution for Smart-Doorbell scripts."""

from __future__ import annotations

from pathlib import Path


def resolve_starter_dir(repo_root: Path | None = None) -> Path:
    """
    Prefer Smart-Doorbell/starter_files if speech_pool.npz is placed there,
    otherwise fall back to ../edge_ai_assignment2 if present, else starter_files.
    """
    root = repo_root or Path(__file__).resolve().parents[2]
    local_starter = root / "starter_files"
    sibling_starter = root.parent / "edge_ai_assignment2"
    if (local_starter / "speech_pool.npz").exists():
        return local_starter
    if (sibling_starter / "speech_pool.npz").exists():
        return sibling_starter
    return local_starter if local_starter.exists() else sibling_starter

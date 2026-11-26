"""
Student 2 - Phase 2: Audio Quantisation, Packing, Unpacking, and SQNR Utilities
Matches edge_ai_assignment2/README.md (Section 5) and doorbell_board_starter.ino.
"""

from __future__ import annotations

from typing import Tuple

import numpy as np

FMT_BITS = {"f32": 32, "i16": 16, "i8": 8}
FMT_DTYPE = {"f32": "<f4", "i16": "<i2", "i8": "i1"}


def validate_fmt(fmt: str) -> None:
    if fmt not in FMT_BITS:
        raise ValueError(f"Unsupported format {fmt!r}; expected one of {tuple(FMT_BITS)}")


def quantise(x: np.ndarray, fmt: str, scale: float = 1.0) -> np.ndarray:
    """
    Quantise float audio x (nominally in -1..1) into f32, i16, or i8 using scale S:
      q = clip(round(x / S * (2**(b-1) - 1)), -2**(b-1), 2**(b-1) - 1)
    For fmt='f32', returns float32 array directly (scale is ignored, matching starter firmware).
    """
    validate_fmt(fmt)
    if scale <= 0:
        raise ValueError("scale must be > 0")
    x_arr = np.asarray(x, dtype=np.float64)
    if fmt == "f32":
        return x_arr.astype("<f4")
    b = FMT_BITS[fmt]
    qmax = (1 << (b - 1)) - 1
    qmin = -(1 << (b - 1))
    q = np.clip(np.round(x_arr / float(scale) * qmax), qmin, qmax)
    return q.astype(FMT_DTYPE[fmt])


def dequantise(q: np.ndarray, fmt: str, scale: float = 1.0) -> np.ndarray:
    """
    Reconstruct float32 samples from quantised array q:
      xhat = q * S / (2**(b-1) - 1)
    Matches pushSamples() in doorbell_board_starter.ino.
    """
    validate_fmt(fmt)
    if scale <= 0:
        raise ValueError("scale must be > 0")
    if fmt == "f32":
        return np.asarray(q, dtype=np.float32)
    b = FMT_BITS[fmt]
    qmax = (1 << (b - 1)) - 1
    return (np.asarray(q, dtype=np.float64) * (float(scale) / qmax)).astype(np.float32)


def pack(x: np.ndarray, fmt: str = "i16", scale: float = 1.0) -> bytes:
    """Quantise float samples x and pack as little-endian raw bytes."""
    q = quantise(x, fmt=fmt, scale=scale)
    return np.ascontiguousarray(q, dtype=FMT_DTYPE[fmt]).tobytes()


def unpack(payload: bytes, fmt: str = "i16", scale: float = 1.0) -> np.ndarray:
    """Unpack little-endian raw bytes back into reconstructed float32 samples."""
    validate_fmt(fmt)
    dt = np.dtype(FMT_DTYPE[fmt])
    if len(payload) % dt.itemsize != 0:
        raise ValueError(f"Payload length {len(payload)} is not a multiple of {dt.itemsize} bytes for {fmt}")
    q = np.frombuffer(payload, dtype=dt)
    return dequantise(q, fmt=fmt, scale=scale)


def pack_and_reconstruct(x: np.ndarray, fmt: str = "i16", scale: float = 1.0) -> Tuple[bytes, np.ndarray]:
    """Convenience helper returning (packed_bytes, reconstructed_float32_samples)."""
    payload = pack(x, fmt=fmt, scale=scale)
    xhat = unpack(payload, fmt=fmt, scale=scale)
    return payload, xhat


def sqnr_db(x_ref: np.ndarray, x_hat: np.ndarray) -> float:
    """Signal-to-Quantisation-Noise Ratio in dB: 10*log10(signal_power / error_power)."""
    ref = np.asarray(x_ref, dtype=np.float64)
    err = ref - np.asarray(x_hat, dtype=np.float64)
    sig_pow = float(np.mean(ref * ref))
    err_pow = float(np.mean(err * err))
    if err_pow == 0.0:
        return float("inf")
    if sig_pow == 0.0:
        return float("-inf")
    return 10.0 * float(np.log10(sig_pow / err_pow))

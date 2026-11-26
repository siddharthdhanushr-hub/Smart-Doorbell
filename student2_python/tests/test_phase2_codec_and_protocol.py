"""Unit tests for Student 2 Phase 2 audio codec, framing, and MockBoard."""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from student2_python.preprocessing.audio_codec import (
    dequantise,
    pack,
    pack_and_reconstruct,
    quantise,
    sqnr_db,
    unpack,
)
from student2_python.transmission.serial_sender import (
    ClipLoader,
    MockBoard,
    build_frame,
    parse_uplink_frames,
)


def test_quantise_pack_unpack_i16_and_i8():
    t = np.linspace(-0.8, 0.8, 1000, dtype=np.float32)
    for fmt, min_sqnr in [("i16", 85.0), ("i8", 35.0)]:
        payload, xhat = pack_and_reconstruct(t, fmt=fmt, scale=1.0)
        assert xhat.shape == t.shape
        assert xhat.dtype == np.float32
        assert sqnr_db(t, xhat) > min_sqnr
        assert unpack(payload, fmt=fmt, scale=1.0).shape == t.shape


def test_quantise_f32_exact():
    x = np.array([-0.5, 0.0, 0.25, 0.99], dtype=np.float32)
    q = quantise(x, fmt="f32")
    assert q.dtype == np.dtype("<f4")
    payload = pack(x, fmt="f32")
    assert len(payload) == 4 * x.size
    np.testing.assert_allclose(unpack(payload, fmt="f32"), x, atol=0.0)


def test_quantise_clipping_with_smaller_scale():
    x = np.array([-0.8, 0.1, 0.8], dtype=np.float32)
    q = quantise(x, fmt="i8", scale=0.25)
    assert q[0] == -128
    assert q[2] == 127
    xhat = dequantise(q, fmt="i8", scale=0.25)
    assert np.isclose(xhat[1], round(0.1 / 0.25 * 127) * 0.25 / 127, atol=1e-6)


def test_frame_crc_and_mock_board_skip():
    f0 = build_frame(b"D", 0, b"\x01\x02\x03\x04")
    f1 = build_frame(b"D", 1, b"\x05\x06\x07\x08")
    # Corrupt one byte in f1 payload
    f1_bad = bytearray(f1)
    f1_bad[10] ^= 0xFF
    frames, bad_crc, bad_len = parse_uplink_frames(f0 + bytes(f1_bad))
    assert len(frames) == 1
    assert bad_crc == 1
    assert bad_len == 0

    mb = MockBoard()
    payload = np.zeros(320 * 10, dtype="<i2").tobytes()
    res = mb.stream(payload, fs=16000, fmt="i16", samples_per_packet=320, store="psram", skip=(2, 5))
    assert res["packets_sent"] == 8
    assert res["board"]["frames_ok"] == 9  # 8 data + 1 END
    assert res["board"]["seq_gaps"] == 2
    assert res["board"]["samples"] == 320 * 8


def test_clip_loader_team1():
    assignment_dir = REPO_ROOT.parent / "edge_ai_assignment2"
    loader = ClipLoader(assignment_dir=assignment_dir, team=1)
    clips = loader.clip_list()
    assert len(clips) == 144
    payload, x = loader.prepare_payload(0, fs=16000, antialias=True, fmt="i16", scale=1.0)
    assert x.shape == (16000,)
    assert len(payload) == 32000

"""
Student 2 - Phase 2 & 3: Audio Loader, Packet Builder, and Serial Transmitter
Supports both physical ESP32-S3 via edge_ai_assignment2/board_link.py and a
board-free MockBoard for offline verification.
"""

from __future__ import annotations

import struct
import sys
import zlib
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Tuple

import numpy as np

from student2_python.preprocessing.audio_codec import pack

UP_MAGIC = b"\xA5\x5A"
DOWN_MAGIC = b"\xB5\x5B"
MAX_PAYLOAD_BYTES = 4096
FMT_BYTES = {"f32": 4, "i16": 2, "i8": 1}


def build_frame(ftype: bytes, seq: int, payload: bytes) -> bytes:
    """Build one uplink frame: A5 5A | type(1B) | seq(u32) | len(u16) | payload | crc32(u32)."""
    if len(ftype) != 1:
        raise ValueError("ftype must be 1 byte")
    if len(payload) > MAX_PAYLOAD_BYTES:
        raise ValueError(f"payload length {len(payload)} exceeds {MAX_PAYLOAD_BYTES} bytes")
    body = ftype + struct.pack("<IH", seq, len(payload)) + payload
    return UP_MAGIC + body + struct.pack("<I", zlib.crc32(body))


def parse_uplink_frames(raw_stream: bytes) -> Tuple[List[Tuple[str, int, bytes]], int, int]:
    """
    Parse concatenated uplink frames (used by mock receiver & protocol tests).
    Returns (valid_frames [(ftype, seq, payload), ...], bad_crc_count, bad_len_count).
    """
    buf = memoryview(raw_stream)
    idx = 0
    n = len(buf)
    frames: List[Tuple[str, int, bytes]] = []
    bad_crc = 0
    bad_len = 0

    while idx + 2 <= n:
        if bytes(buf[idx:idx + 2]) != UP_MAGIC:
            idx += 1
            continue
        if idx + 9 > n:
            break
        ftype = bytes(buf[idx + 2:idx + 3]).decode("ascii", errors="replace")
        seq, ln = struct.unpack_from("<IH", buf, idx + 3)
        if ln > MAX_PAYLOAD_BYTES:
            bad_len += 1
            idx += 2
            continue
        end = idx + 9 + ln + 4
        if end > n:
            break
        body = bytes(buf[idx + 2:idx + 9 + ln])
        (crc,) = struct.unpack_from("<I", buf, idx + 9 + ln)
        if zlib.crc32(body) != crc:
            bad_crc += 1
            idx = end
            continue
        frames.append((ftype, seq, bytes(buf[idx + 9:idx + 9 + ln])))
        idx = end

    return frames, bad_crc, bad_len


class MockBoard:
    """
    Board-free mock matching Board.stream() return structure for Student 2 offline tests.
    Simulates uplink packet parsing, sequence gap/duplicate detection, CRC checks, and storage.
    """

    def __init__(self):
        self.stored = b""
        self.where = "none"

    def info(self) -> Dict[str, Any]:
        return {
            "cpu_mhz": 240,
            "heap_free": 256208,
            "psram_size": 0,
            "flash_chip": 16777216,
            "stored": len(self.stored),
            "where": self.where,
            "mock": True,
        }

    def stream(
        self,
        payload: bytes,
        fs: int,
        fmt: str = "i16",
        scale: float = 1.0,
        win: int = 480,
        hop: int = 320,
        nfft: int = 512,
        mels: int = 40,
        mfcc: int = 0,
        feat: bool = True,
        store: str = "none",
        max_bytes: int = 0,
        speed: float = 1.0,
        samples_per_packet: int = 320,
        skip: tuple = (),
    ) -> Dict[str, Any]:
        bps = FMT_BYTES[fmt]
        if len(payload) % bps != 0:
            raise ValueError("payload length is not a whole number of samples")
        if samples_per_packet * bps > MAX_PAYLOAD_BYTES:
            raise ValueError("a frame can carry at most 4096 bytes")

        step = samples_per_packet * bps
        wire = bytearray()
        seq = 0
        sent = 0
        for off in range(0, len(payload), step):
            if seq not in skip:
                wire += build_frame(b"D", seq, payload[off:off + step])
                sent += 1
            seq += 1
        wire += build_frame(b"E", seq, b"")

        parsed, bad_crc, bad_len = parse_uplink_frames(bytes(wire))
        last_seq = -1
        seq_gaps = 0
        dup = 0
        frames_ok = 0
        rx_buf = bytearray()
        for ftype, rseq, rpay in parsed:
            if rseq <= last_seq:
                dup += 1
                continue
            if last_seq >= 0 and rseq != last_seq + 1:
                seq_gaps += rseq - last_seq - 1
            last_seq = rseq
            frames_ok += 1
            if ftype == "D":
                rx_buf += rpay

        if store in ("sram", "psram"):
            cap = max_bytes or len(payload)
            self.stored = bytes(rx_buf[:cap])
            self.where = store
        else:
            self.stored = b""
            self.where = "none"

        n_samples = len(rx_buf) // bps
        expected = 0 if (len(payload) // bps) < win or not feat else 1 + ((len(payload) // bps) - win) // hop
        return {
            "mock": True,
            "features": np.zeros((0, mfcc or mels), dtype=np.float32),
            "expected_features": expected,
            "packets_sent": sent,
            "bytes_sent": len(payload),
            "audio_seconds": (len(payload) // bps) / fs,
            "board": {
                "why": "end",
                "frames_ok": frames_ok,
                "bad_crc": bad_crc,
                "bad_len": bad_len,
                "seq_gaps": seq_gaps,
                "dup": dup,
                "samples": n_samples,
                "stored": len(self.stored),
                "where": self.where,
            },
        }

    def dump(self, where: str) -> bytes:
        if where == self.where:
            return self.stored
        return b""


@dataclass
class ClipLoader:
    assignment_dir: Path
    team: int = 1

    def __post_init__(self) -> None:
        if str(self.assignment_dir) not in sys.path:
            sys.path.insert(0, str(self.assignment_dir))
        import team_audio as ta  # type: ignore
        self._ta = ta

    def clip_list(self) -> List[Tuple[int, str]]:
        return self._ta.clip_list(self.team)

    def load_clip(self, clip_id: int, fs: int = 16000, antialias: bool = True) -> np.ndarray:
        return self._ta.get_clip(self.team, clip_id, fs=fs, antialias=antialias)

    def prepare_payload(
        self, clip_id: int, fs: int = 16000, antialias: bool = True, fmt: str = "i16", scale: float = 1.0
    ) -> Tuple[bytes, np.ndarray]:
        x = self.load_clip(clip_id, fs=fs, antialias=antialias)
        payload = pack(x, fmt=fmt, scale=scale)
        return payload, x

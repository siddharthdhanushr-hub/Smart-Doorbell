"""
Mission 2 / Phase 3 Storage & Persistence Test Runner for ESP32-S3.
Modes:
  --phase probe    : tests PSRAM status + binary-searches max SRAM allocation (before/after OPI PSRAM).
  --phase save144  : streams all 144 Team 1 clips (16 kHz i16 = 4,608,000 B) to PSRAM, runs SAVE,
                     compares host CRC vs PSRAM CRC vs Flash CRC, and saves clip_index metadata.
  --phase verify   : after physical unplug + replug, verifies PSRAM is wiped (0) and Flash dump/CRC
                     matches the exact 4,608,000 bytes transmitted before power loss.
"""

from __future__ import annotations

import argparse
import json
import sys
import zlib
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

import numpy as np

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))
from student2_python.src.paths import resolve_starter_dir  # type: ignore

ASSIGNMENT_DIR = resolve_starter_dir(REPO_ROOT)
sys.path.insert(0, str(ASSIGNMENT_DIR))

from board_link import Board  # type: ignore
from student2_python.transmission.batch_pipeline import transmit_batch  # type: ignore
from student2_python.transmission.serial_sender import ClipLoader  # type: ignore


def run_probe(port: str, baud: int) -> Dict[str, Any]:
    b = Board(port, baud=baud)
    try:
        info = b.info()
        psram_err = None
        psram_res = None
        try:
            r = b.stream(b"\x00" * 32000, fs=16000, fmt="i16", feat=False, store="psram", max_bytes=32000, speed=4.0)
            psram_res = r["board"]
            b.free()
        except Exception as e:
            psram_err = str(e)

        # Binary search largest SRAM buffer allocatable cleanly (in 1024 B steps, aligned to 2 B samples)
        lo, hi = 1024, max(2048, info.get("heap_largest", 262144))
        best_bytes = 0
        attempts: List[Dict[str, Any]] = []
        while lo <= hi:
            mid = ((lo + hi) // 2) & ~1
            try:
                r = b.stream(b"\x00" * min(mid, 16000), fs=16000, fmt="i16", feat=False, store="sram", max_bytes=mid, speed=8.0)
                b.free()
                best_bytes = mid
                attempts.append({"bytes": mid, "ok": True, "stored": r["board"]["stored"]})
                lo = mid + 1024
            except Exception as e:
                attempts.append({"bytes": mid, "ok": False, "err": str(e)})
                hi = mid - 1024

        # Verify actual full-size stream at best_bytes (at 16 kHz i16), backing off if heap fragmented slightly
        full_verify = None
        verified_bytes = best_bytes
        while verified_bytes >= 1024:
            payload = np.zeros(verified_bytes // 2, dtype="<i2").tobytes()
            try:
                r = b.stream(payload, fs=16000, fmt="i16", feat=False, store="sram", max_bytes=verified_bytes, speed=4.0)
                full_verify = r["board"]
                b.free()
                break
            except Exception:
                verified_bytes = (verified_bytes - 4096) & ~1
        best_bytes = verified_bytes if full_verify else best_bytes

        out = {
            "timestamp": datetime.now().isoformat(),
            "port": port,
            "info": info,
            "psram_test_ok": psram_err is None,
            "psram_error": psram_err,
            "psram_result": psram_res,
            "sram_max_bytes": best_bytes,
            "sram_max_seconds_16khz_i16": round(best_bytes / 32000.0, 3),
            "sram_full_verify": full_verify,
            "sram_probe_attempts": attempts,
        }
        return out
    finally:
        b.close()


def run_save144(port: str, baud: int, fs: int, fmt: str, scale: float, speed: float) -> Dict[str, Any]:
    loader = ClipLoader(ASSIGNMENT_DIR, team=1)
    clips = loader.clip_list()
    chunks = []
    index = []
    off = 0
    for cid, lab in clips:
        pay, x = loader.prepare_payload(cid, fs=fs, antialias=True, fmt=fmt, scale=scale)
        chunks.append(pay)
        index.append({"clip_id": cid, "label": lab, "start_sample": off, "samples": int(x.size), "bytes": len(pay)})
        off += int(x.size)
    full_payload = b"".join(chunks)
    host_crc = zlib.crc32(full_payload)

    b = Board(port, baud=baud)
    try:
        info_before = b.info()
        r = b.stream(
            full_payload,
            fs=fs,
            fmt=fmt,
            scale=scale,
            feat=False,
            store="psram",
            max_bytes=len(full_payload),
            speed=speed,
            samples_per_packet=320,
        )
        psram_crc = b.crc("psram")
        save_rep = b.save()
        flash_crc = b.crc("flash")
        info_after = b.info()

        # Verify PSRAM dump byte-for-byte
        psram_dump = b.dump("psram")
        psram_exact_match = psram_dump == full_payload

        return {
            "timestamp": datetime.now().isoformat(),
            "phase": "save144",
            "port": port,
            "fs": fs,
            "fmt": fmt,
            "scale": scale,
            "speed": speed,
            "num_clips": len(clips),
            "expected_bytes": len(full_payload),
            "host_crc32_hex": f"{host_crc:08x}",
            "info_before": info_before,
            "stream_board": r["board"],
            "send_seconds": round(r["send_seconds"], 4),
            "psram_crc": psram_crc,
            "psram_exact_match": psram_exact_match,
            "save_reply": save_rep,
            "flash_crc": flash_crc,
            "flash_crc_match": flash_crc.get("crc") == host_crc,
            "info_after": info_after,
        }
    finally:
        b.close()


def run_verify(port: str, baud: int, fs: int, fmt: str, scale: float) -> Dict[str, Any]:
    loader = ClipLoader(ASSIGNMENT_DIR, team=1)
    chunks = [loader.prepare_payload(cid, fs=fs, antialias=True, fmt=fmt, scale=scale)[0] for cid, _ in loader.clip_list()]
    full_payload = b"".join(chunks)
    host_crc = zlib.crc32(full_payload)

    b = Board(port, baud=baud)
    try:
        info = b.info()
        psram_crc = b.crc("psram")
        flash_crc = b.crc("flash")
        flash_dump = b.dump("flash")
        return {
            "timestamp": datetime.now().isoformat(),
            "phase": "post_power_cycle_verify",
            "port": port,
            "info_after_replug": info,
            "psram_crc_after_replug": psram_crc,
            "flash_crc_after_replug": flash_crc,
            "flash_dump_bytes": len(flash_dump),
            "expected_bytes": len(full_payload),
            "host_crc32_hex": f"{host_crc:08x}",
            "flash_crc_hex": f"{flash_crc.get('crc', 0):08x}",
            "flash_exact_byte_match": flash_dump == full_payload,
            "psram_survived_power_cut": psram_crc.get("n", 0) > 0,
        }
    finally:
        b.close()


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", required=True)
    ap.add_argument("--baud", type=int, default=921600)
    ap.add_argument("--phase", choices=["probe", "save144", "verify"], required=True)
    ap.add_argument("--tag", default="default")
    ap.add_argument("--fs", type=int, default=16000)
    ap.add_argument("--fmt", default="i16")
    ap.add_argument("--scale", type=float, default=1.0)
    ap.add_argument("--speed", type=float, default=4.0)
    args = ap.parse_args()

    logs_dir = REPO_ROOT / "student1_esp32" / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)

    if args.phase == "probe":
        res = run_probe(args.port, args.baud)
        out_path = logs_dir / f"mission2_probe_{args.tag}.json"
    elif args.phase == "save144":
        res = run_save144(args.port, args.baud, args.fs, args.fmt, args.scale, args.speed)
        out_path = logs_dir / f"mission2_save144_{args.tag}.json"
    else:
        res = run_verify(args.port, args.baud, args.fs, args.fmt, args.scale)
        out_path = logs_dir / f"mission2_verify_{args.tag}.json"

    out_path.write_text(json.dumps(res, indent=2), encoding="utf-8")
    print(f"Saved {out_path}")
    print(json.dumps(res, indent=2))


if __name__ == "__main__":
    main()

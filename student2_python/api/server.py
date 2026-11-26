"""
Student 2 - Backend JSON API Server for Student 3's Dashboard
Serves verified hardware, audio, dataset, and benchmark data without requiring
a live ESP32-S3 connection.
Run: py student2_python/api/server.py --port 5000
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path
from typing import Any, Dict, List

from flask import Flask, jsonify, request

REPO_ROOT = Path(__file__).resolve().parents[2]
ASSIGNMENT_DIR = REPO_ROOT.parent / "edge_ai_assignment2"
if str(ASSIGNMENT_DIR) not in sys.path:
    sys.path.insert(0, str(ASSIGNMENT_DIR))
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import numpy as np
import team_audio as ta  # type: ignore
from student2_python.logmel.reference_logmel import features as py_features  # type: ignore


def _read_json(rel_path: str) -> Any:
    p = REPO_ROOT / rel_path
    if not p.exists():
        return None
    return json.loads(p.read_text(encoding="utf-8"))


def _read_csv_rows(rel_path: str) -> List[Dict[str, Any]]:
    p = REPO_ROOT / rel_path
    if not p.exists():
        return []
    with p.open("r", newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def create_app() -> Flask:
    app = Flask(__name__)

    @app.get("/api/health")
    def health():
        return jsonify({
            "status": "ok",
            "team": 1,
            "team_name": "Paradise",
            "live_board_required": False,
            "data_mode": "recorded_hardware_and_python_reference",
        })

    @app.get("/api/configs")
    def configs():
        return jsonify({
            "hardware": _read_json("shared/hardware_config.json"),
            "audio": _read_json("shared/audio_config.json"),
            "logmel": _read_json("shared/logmel_config.json"),
            "protocol": _read_json("shared/communication_protocol.json"),
            "contract": _read_json("shared/frontend_api_contract.json"),
        })

    @app.get("/api/dataset")
    def dataset():
        data_card_path = REPO_ROOT / "dataset" / "data_card.md"
        return jsonify({
            "validation": _read_json("dataset/dataset_validation.json"),
            "manifest": _read_csv_rows("dataset/dataset_manifest.csv"),
            "data_card_md": data_card_path.read_text(encoding="utf-8") if data_card_path.exists() else None,
        })

    @app.get("/api/clips/<int:clip_id>")
    def clip_detail(clip_id: int):
        if not (0 <= clip_id < 144):
            return jsonify({"error": "clip_id must be in 0..143"}), 404
        fs = int(request.args.get("fs", 16000))
        antialias = request.args.get("antialias", "true").lower() != "false"
        if fs not in ta.ALLOWED_FS:
            return jsonify({"error": f"fs must be one of {ta.ALLOWED_FS}"}), 400

        clips = dict(ta.clip_list(1))
        x = ta.get_clip(1, clip_id, fs=fs, antialias=antialias)
        win = 480 if fs == 16000 else int(round(0.030 * fs))
        hop = 320 if fs == 16000 else int(round(0.020 * fs))
        nfft = 512 if fs == 16000 else 256
        py_feat, first_samp = py_features(x, fs=fs, win=win, hop=hop, nfft=nfft, mels=40, mfcc=0)

        esp_feat = None
        esp_npz = REPO_ROOT / "student1_esp32" / "feature_arrays" / "esp32_clips_16k_i16_S1.0_speed1.npz"
        if fs == 16000 and antialias and esp_npz.exists():
            d = np.load(esp_npz)
            esp_feat = d["features"][clip_id].tolist()

        return jsonify({
            "clip_id": clip_id,
            "label": clips[clip_id],
            "fs": fs,
            "antialias": antialias,
            "waveform": x.tolist(),
            "first_sample": first_samp.tolist(),
            "python_logmel": py_feat.tolist(),
            "esp32_logmel": esp_feat,
            "esp32_source": "recorded_16k_i16_S1.0_speed1" if esp_feat is not None else None,
        })

    @app.get("/api/benchmarks/mission1")
    def mission1():
        return jsonify({
            "csv_rows": _read_csv_rows("student1_esp32/benchmarks/mission1_throughput.csv"),
            "results": _read_json("student1_esp32/logs/mission1_pipe_results.json"),
        })

    @app.get("/api/benchmarks/mission2")
    def mission2():
        return jsonify({
            "probe_baseline": _read_json("student1_esp32/logs/mission2_probe_baseline.json"),
            "save144": _read_json("student1_esp32/logs/mission2_save144_opi_16m.json"),
            "verify_power_cut": _read_json("student1_esp32/logs/mission2_verify_opi_16m.json"),
            "python_audio_analysis": _read_json("student2_python/documentation/mission2_audio_analysis.json"),
        })

    @app.get("/api/benchmarks/mission3")
    def mission3():
        return jsonify({
            "starter_10s": _read_json("student1_esp32/logs/mission3_starter_10s.json"),
            "optimized": _read_json("student1_esp32/logs/mission3_optimized_results.json"),
        })

    @app.get("/api/benchmarks/mission4_5")
    def mission4_5():
        return jsonify({
            "skip_before_fix": _read_json("student1_esp32/logs/mission4_skip_before_fix.json"),
            "skip_after_fix": _read_json("student1_esp32/logs/mission4_skip_after_fix.json"),
            "com_speed_ramp": _read_json("student1_esp32/logs/mission4_com_speed_ramp.json"),
            "all_144_runs": _read_json("student1_esp32/logs/phase5_144clips_all_runs.json"),
        })

    return app


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=5000)
    args = ap.parse_args()
    app = create_app()
    app.run(host=args.host, port=args.port, debug=False)


if __name__ == "__main__":
    main()

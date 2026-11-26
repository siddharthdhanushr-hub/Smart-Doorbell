"""Unit tests for Student 2 Flask backend API server."""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from student2_python.api.server import create_app


def test_api_endpoints_without_board():
    app = create_app()
    client = app.test_client()

    r = client.get("/api/health")
    assert r.status_code == 200
    assert r.get_json()["live_board_required"] is False

    r = client.get("/api/configs")
    assert r.status_code == 200
    cfg = r.get_json()
    assert cfg["audio"]["total_clips"] == 144
    assert cfg["logmel"]["mels"] == 40

    r = client.get("/api/dataset")
    assert r.status_code == 200
    ds = r.get_json()
    assert len(ds["manifest"]) == 144

    r = client.get("/api/clips/0")
    assert r.status_code == 200
    clip = r.get_json()
    assert clip["clip_id"] == 0
    assert clip["label"] == "on"
    assert len(clip["waveform"]) == 16000
    assert len(clip["python_logmel"]) == 49
    assert len(clip["esp32_logmel"]) == 49

    for ep in ("/api/benchmarks/mission1", "/api/benchmarks/mission2", "/api/benchmarks/mission3", "/api/benchmarks/mission4_5"):
        resp = client.get(ep)
        assert resp.status_code == 200

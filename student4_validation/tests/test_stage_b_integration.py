"""Stage B cross-module integration tests verifying shared contracts and generated outputs."""

from __future__ import annotations

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


def test_frontend_api_contract_all_paths_exist() -> None:
    contract_path = REPO_ROOT / "shared" / "frontend_api_contract.json"
    contract = json.loads(contract_path.read_text(encoding="utf-8"))

    for key, rel_or_list in contract["data_sources"].items():
        paths = rel_or_list if isinstance(rel_or_list, list) else [rel_or_list]
        for rel in paths:
            assert (REPO_ROOT / rel).exists(), f"Missing data_sources[{key}] file: {rel}"

    for setting, group in contract["feature_arrays_for_student4"].items():
        for role, rel in group.items():
            assert (REPO_ROOT / rel).exists(), f"Missing feature_arrays[{setting}][{role}]: {rel}"


def test_student4_outputs_match_stage_b_expectations() -> None:
    feat_cmp = json.loads(
        (REPO_ROOT / "student4_validation" / "outputs" / "mission5_feature_comparison.json").read_text(
            encoding="utf-8"
        )
    )
    assert set(feat_cmp.keys()) == {
        "16k_i16_S1.0_speed1",
        "16k_i8_S1.0",
        "16k_i8_S0.25",
        "8k_i16_S1.0_noaa",
    }
    assert feat_cmp["8k_i16_S1.0_noaa"]["reference_baseline"] == (
        "8 kHz filtered (antialias=True) Python float32 reference"
    )
    assert feat_cmp["8k_i16_S1.0_noaa"]["mae_db"] > 5.0

    clf = json.loads(
        (REPO_ROOT / "student4_validation" / "outputs" / "mission5_classifier_results.json").read_text(
            encoding="utf-8"
        )
    )
    assert clf["split"]["train_clips"] == 96
    assert clf["split"]["test_clips"] == 48
    assert len(clf["classes"]) == 6
    assert len(clf["evaluations"]) == 5

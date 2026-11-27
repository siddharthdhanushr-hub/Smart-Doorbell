"""Unit tests for Student 4's Mission 4 & 5 metrics and clip-level split."""

from __future__ import annotations

import numpy as np
import pytest

from student4_validation.src.compare_features import CLASSES, compute_error_metrics
from student4_validation.src.nearest_centroid_eval import (
    clip_embeddings,
    evaluate_nearest_centroid,
    fit_nearest_centroid,
    make_clip_split,
)


def test_compute_error_metrics_exact_known_arrays() -> None:
    # 6 clips (1 per class), 2 frames, 40 bands
    labels = np.array(CLASSES)
    ref = np.zeros((6, 2, 40), dtype=np.float32)
    esp = np.zeros((6, 2, 40), dtype=np.float32)

    # Constant +2.0 offset on clip 0 ('on'), -4.0 offset on band 5 of clip 1 ('off')
    esp[0, :, :] = 2.0
    esp[1, :, 5] = -4.0

    m = compute_error_metrics(esp, ref, labels)

    # Total elements = 6 * 2 * 40 = 480
    # Sum |diff| = 80 * 2.0 + 2 * 4.0 = 168.0 => MAE = 168 / 480 = 0.35
    # Sum diff^2 = 80 * 4.0 + 2 * 16.0 = 352.0 => MSE = 352 / 480
    assert m["mae_db"] == pytest.approx(168.0 / 480.0, abs=1e-6)
    assert m["mse_db2"] == pytest.approx(352.0 / 480.0, abs=1e-6)
    assert m["rmse_db"] == pytest.approx(np.sqrt(352.0 / 480.0), abs=1e-6)
    assert m["max_abs_db"] == pytest.approx(4.0, abs=1e-6)
    assert m["per_class_mae_db"]["on"] == pytest.approx(2.0, abs=1e-6)
    assert m["per_class_mae_db"]["off"] == pytest.approx(8.0 / 80.0, abs=1e-6)
    assert m["per_class_mae_db"]["_silence"] == pytest.approx(0.0, abs=1e-6)
    assert len(m["per_band_mae_db"]) == 40
    assert m["per_band_mae_db"][5] == pytest.approx((2 * 2.0 + 2 * 4.0) / 12.0, abs=1e-6)


def test_compute_error_metrics_rejects_nan_and_mismatch() -> None:
    labels = np.array(CLASSES)
    a = np.zeros((6, 2, 40), dtype=np.float32)
    b = np.zeros((6, 3, 40), dtype=np.float32)
    with pytest.raises(ValueError):
        compute_error_metrics(a, b, labels)

    c = np.zeros((6, 2, 40), dtype=np.float32)
    c[0, 0, 0] = np.nan
    with pytest.raises(ValueError):
        compute_error_metrics(a, c, labels)


def test_stratified_clip_split_zero_leakage() -> None:
    labels = np.array([cls for cls in CLASSES for _ in range(24)])
    train_idx, test_idx = make_clip_split(labels, test_size=1.0 / 3.0, seed=42)

    assert len(train_idx) == 96
    assert len(test_idx) == 48
    assert len(set(train_idx.tolist()) & set(test_idx.tolist())) == 0
    assert sorted(train_idx.tolist() + test_idx.tolist()) == list(range(144))

    for cls in CLASSES:
        assert int(np.sum(labels[train_idx] == cls)) == 16
        assert int(np.sum(labels[test_idx] == cls)) == 8


def test_nearest_centroid_separable_clusters() -> None:
    rng = np.random.default_rng(7)
    labels = np.array([cls for cls in CLASSES for _ in range(24)])
    feats = np.zeros((144, 49, 40), dtype=np.float32)
    for c_idx, cls in enumerate(CLASSES):
        mask = labels == cls
        feats[mask] = (c_idx * 10.0) + rng.normal(0.0, 0.2, size=(24, 49, 40)).astype(np.float32)

    X = clip_embeddings(feats)
    assert X.shape == (144, 80)

    train_idx, test_idx = make_clip_split(labels, test_size=1.0 / 3.0, seed=42)
    mu, sd, centroids = fit_nearest_centroid(X[train_idx], labels[train_idx], CLASSES)
    ev = evaluate_nearest_centroid("synthetic", X[test_idx], labels[test_idx], mu, sd, centroids, CLASSES)
    assert ev["accuracy"] == pytest.approx(1.0)
    assert ev["f1_macro"] == pytest.approx(1.0)
    assert np.sum(ev["confusion_matrix"]) == 48

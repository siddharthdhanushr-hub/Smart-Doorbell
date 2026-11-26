"""Unit tests for Student 2 Phase 4 Python reference log-mel & MFCC pipeline."""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from student2_python.logmel.reference_logmel import build_dct_matrix, build_mel_filterbank, features


def test_logmel_shape_and_first_sample():
    x = np.random.default_rng(42).normal(0, 0.1, size=16000).astype(np.float32)
    f, fsamp = features(x, fs=16000, win=480, hop=320, nfft=512, mels=40, mfcc=0)
    assert f.shape == (49, 40)
    assert f.dtype == np.float32
    assert fsamp[0] == 0
    assert fsamp[-1] == 48 * 320
    assert np.all(np.isfinite(f))


def test_mfcc_dct_orthonormal():
    dct = build_dct_matrix(mels=40, mfcc=13)
    gram = dct @ dct.T
    np.testing.assert_allclose(gram, np.eye(13), atol=1e-12)
    x = np.sin(2 * np.pi * 440 * np.arange(16000) / 16000).astype(np.float32)
    m, _ = features(x, fs=16000, win=400, hop=160, nfft=512, mels=40, mfcc=13)
    assert m.shape == (98, 13)


def test_mel_filterbank_htk_bounds():
    fb = build_mel_filterbank(fs=16000, nfft=512, mels=40)
    assert fb.shape == (40, 257)
    assert np.all(fb >= 0.0)
    assert np.all(fb <= 1.0)
    assert np.all(fb.sum(axis=1) > 0.0)

import shutil
from pathlib import Path

import pytest

from lib.audio import get_duration, normalize_peak, trim_silence

FIXTURE = Path(__file__).parent / "fixtures" / "sample.mp3"


@pytest.fixture
def tmp_mp3(tmp_path):
    dst = tmp_path / "audio.mp3"
    shutil.copy(FIXTURE, dst)
    return dst


def test_get_duration_returns_positive_float(tmp_mp3):
    d = get_duration(tmp_mp3)
    assert isinstance(d, float)
    assert d > 0


def test_trim_silence_keeps_valid_mp3(tmp_mp3):
    trim_silence(tmp_mp3)
    assert get_duration(tmp_mp3) > 0


def test_normalize_peak_preserves_duration(tmp_mp3):
    d_before = get_duration(tmp_mp3)
    normalize_peak(tmp_mp3)
    d_after = get_duration(tmp_mp3)
    assert abs(d_after - d_before) < 0.2  # mp3 re-encode can shift by ~50ms

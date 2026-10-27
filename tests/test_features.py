import numpy as np
import pytest

from eegpipe.config import BANDS
from eegpipe.features import band_power, check_bands, compute_psd, relative_band_power


def test_default_bands_do_not_overlap():
    check_bands(BANDS)


def test_overlapping_bands_rejected():
    with pytest.raises(ValueError):
        check_bands({"a": (1, 5), "b": (4, 8)})


def test_alpha_sine_power_matches_variance():
    fs, amp = 250.0, 10e-6
    t = np.arange(0, 20, 1 / fs)
    x = amp * np.sin(2 * np.pi * 10 * t)[None, None, :]
    freqs, psd = compute_psd(x, fs)
    p = band_power(freqs, psd, BANDS)[0, 0]
    alpha = p[list(BANDS).index("alpha")]
    assert alpha == pytest.approx(amp**2 / 2, rel=0.10)


def test_relative_power_sums_to_one_and_alpha_dominates():
    fs = 250.0
    t = np.arange(0, 20, 1 / fs)
    x = (10e-6 * np.sin(2 * np.pi * 10 * t))[None, None, :]
    freqs, psd = compute_psd(x, fs)
    rel = relative_band_power(band_power(freqs, psd, BANDS))[0, 0]
    assert rel.sum() == pytest.approx(1.0)
    assert rel[list(BANDS).index("alpha")] > 0.9

"""PSD and band-power utilities. Units: input volts -> PSD V^2/Hz -> power V^2."""
from __future__ import annotations

import numpy as np
from scipy.integrate import trapezoid
from scipy.signal import welch


def check_bands(bands: dict[str, tuple[float, float]]) -> None:
    edges = sorted(bands.values())
    for (lo, hi) in edges:
        if not lo < hi:
            raise ValueError(f"Invalid band {lo}-{hi}")
    for (_, hi1), (lo2, _) in zip(edges[:-1], edges[1:]):
        if hi1 > lo2:
            raise ValueError("Bands overlap")


def compute_psd(data: np.ndarray, sfreq: float, nperseg_sec: float = 2.0):
    nperseg = int(round(nperseg_sec * sfreq))
    return welch(data, fs=sfreq, nperseg=nperseg, noverlap=nperseg // 2, axis=-1)


def band_power(freqs: np.ndarray, psd: np.ndarray, bands: dict) -> np.ndarray:
    check_bands(bands)
    out = []
    for lo, hi in bands.values():
        mask = (freqs >= lo) & (freqs < hi)
        out.append(trapezoid(psd[..., mask], freqs[mask], axis=-1))
    return np.stack(out, axis=-1)


def relative_band_power(powers: np.ndarray) -> np.ndarray:
    """Each band divided by the sum of all bands (so values sum to 1)."""
    with np.errstate(divide="ignore", invalid="ignore"):
        return powers / powers.sum(axis=-1, keepdims=True)
"""Load a raw EEGLAB file, filter, epoch, and flag bad channel-epochs."""
from __future__ import annotations

from pathlib import Path

import numpy as np

from eegpipe.config import (EPOCH_SEC, FILTER_BAND_HZ, FLAT_V, FULL_19,
                            PTP_REJECT_V)


def load_epochs(set_path: Path):
    """Return (data[epochs, 19, samples] in volts, sfreq). Channels in FULL_19 order."""
    import mne

    raw = mne.io.read_raw_eeglab(str(set_path), preload=True, verbose="ERROR")
    raw.pick("eeg")
    missing = [c for c in FULL_19 if c not in raw.ch_names]
    if missing:
        raise ValueError(f"{set_path.name}: missing channels {missing}")
    raw.filter(FILTER_BAND_HZ[0], FILTER_BAND_HZ[1], method="fir",
               fir_design="firwin", verbose="ERROR")
    epochs = mne.make_fixed_length_epochs(raw, duration=EPOCH_SEC, overlap=0.0,
                                         preload=True, verbose="ERROR")
    data = epochs.get_data()
    idx = [epochs.ch_names.index(c) for c in FULL_19]
    return data[:, idx, :].astype(np.float64), float(raw.info["sfreq"])


def bad_mask(data: np.ndarray) -> np.ndarray:
    """Boolean [epochs, channels]: True where channel-epoch is too large or flat."""
    ptp = data.max(axis=-1) - data.min(axis=-1)
    return (ptp > PTP_REJECT_V) | (ptp < FLAT_V)

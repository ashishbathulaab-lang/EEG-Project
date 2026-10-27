"""Audit the downloaded dataset. Run: python -m eegpipe.audit"""
from __future__ import annotations

import sys

import pandas as pd

from eegpipe.config import FULL_19, GROUP_COL, RAW_DIR


def main() -> None:
    pfile = RAW_DIR / "participants.tsv"
    if not pfile.exists():
        print(f"MISSING: {pfile}. Check Stage 4 download path.")
        sys.exit(1)
    p = pd.read_csv(pfile, sep="\t")
    print("Columns:", p.columns.tolist())
    print("Rows:", len(p))
    if GROUP_COL not in p.columns:
        print(f"Column '{GROUP_COL}' not found: edit GROUP_COL in config.py")
        sys.exit(1)
    print(p[GROUP_COL].value_counts(dropna=False))
    numeric = [c for c in ("Age", "MMSE") if c in p.columns]
    if numeric:
        print(p.groupby(GROUP_COL)[numeric].agg(["count", "mean", "std", "min", "max"]))
    no_eeg = [pid for pid in p["participant_id"]
              if not list((RAW_DIR / pid / "eeg").glob("*_eeg.set"))]
    print("Participants with no .set file:", no_eeg)

    first = sorted(RAW_DIR.glob("sub-*/eeg/*_eeg.set"))
    if not first:
        print("No .set files found; paste the folder listing to your assistant.")
        sys.exit(1)
    import mne
    raw = mne.io.read_raw_eeglab(str(first[0]), preload=False, verbose="ERROR")
    print("File:", first[0].name)
    print("Channels:", raw.ch_names)
    print("Sampling rate:", raw.info["sfreq"], "Hz")
    print("Duration (s):", round(raw.times[-1], 1))
    print("Missing 10-20 channels:", [c for c in FULL_19 if c not in raw.ch_names])


if __name__ == "__main__":
    main()
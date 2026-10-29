"""Build per-participant features and a QC report. Run: python -m eegpipe.build_features"""
from __future__ import annotations

import numpy as np
import pandas as pd

from eegpipe.config import (BANDS, EPOCH_SEC, FULL_19, MONTAGES, PROCESSED_DIR,
                            RAW_DIR)
from eegpipe.features import band_power, compute_psd, relative_band_power
from eegpipe.preprocess import bad_mask, load_epochs


def main() -> None:
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    participants = pd.read_csv(RAW_DIR / "participants.tsv", sep="\t")
    rows = {m: [] for m in MONTAGES}
    qc = []
    for pid in participants["participant_id"]:
        files = sorted((RAW_DIR / pid / "eeg").glob("*_eeg.set"))
        if not files:
            qc.append({"participant_id": pid, "montage": "ALL", "note": "no file"})
            continue
        data, sfreq = load_epochs(files[0])
        bad = bad_mask(data)
        freqs, psd = compute_psd(data, sfreq)
        rel = relative_band_power(band_power(freqs, psd, BANDS))  # [epochs, 19, bands]
        for m, chans in MONTAGES.items():
            idx = [FULL_19.index(c) for c in chans]
            keep = ~bad[:, idx].any(axis=1)
            n = int(keep.sum())
            qc.append({"participant_id": pid, "montage": m, "n_epochs_total": len(data),
                       "n_epochs_usable": n, "usable_sec": n * EPOCH_SEC, "note": ""})
            if n == 0:
                continue
            feat = np.median(rel[keep][:, idx, :], axis=0)
            row = {"participant_id": pid}
            for i, ch in enumerate(chans):
                for j, band in enumerate(BANDS):
                    row[f"{ch}_{band}"] = feat[i, j]
            rows[m].append(row)
        print("done", pid)
    pd.DataFrame(qc).to_csv(PROCESSED_DIR / "qc_report.csv", index=False)
    for m, r in rows.items():
        pd.DataFrame(r).to_csv(PROCESSED_DIR / f"features_{m}.csv", index=False)
    print("Wrote features and qc_report to", PROCESSED_DIR)


if __name__ == "__main__":
    main()

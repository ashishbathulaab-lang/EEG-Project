"""Run: python -m eegpipe.make_figures"""
from __future__ import annotations

import json
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

from eegpipe import config as cfg
from eegpipe.config import RESULTS_DIR, PROCESSED_DIR


def main() -> None:
    # 1. AUROC by Montage Figure
    res = json.loads((RESULTS_DIR / "metrics.json").read_text())
    names = [k for k in res["models"] if k.startswith("eeg_") and not k.endswith("_plus_mmse")]
    est = [res["models"][k]["auroc_of_mean_score"] for k in names]
    lo = [res["models"][k]["auroc_95ci_participant_bootstrap"][0] for k in names]
    hi = [res["models"][k]["auroc_95ci_participant_bootstrap"][1] for k in names]
    
    fig, ax = plt.subplots(figsize=(6, 3.5))
    ax.errorbar(est, range(len(names)),
                xerr=[[e - l for e, l in zip(est, lo)], [h - e for e, h in zip(est, hi)]],
                fmt="o", capsize=3, color="teal")
    ax.axvline(0.5, linestyle="--", color="grey", alpha=0.7)
    ax.set_yticks(range(len(names)))
    ax.set_yticklabels([n.replace("eeg_", "") for n in names])
    ax.set_xlabel("AUROC (participant-bootstrap 95% CI)")
    ax.set_title("AD vs control, EEG only, nested subject-level CV")
    fig.tight_layout()
    fig.savefig(RESULTS_DIR / "fig_auroc_by_montage.png", dpi=200)
    plt.close(fig)
    print("Saved fig_auroc_by_montage.png")

    # 2. Usable Epochs / Seconds per Montage Boxplot
    qc = pd.read_csv(PROCESSED_DIR / "qc_report.csv")
    qc = qc[qc["montage"].isin(cfg.MONTAGES.keys())]
    
    qc["usable_seconds"] = qc["n_epochs_usable"] * cfg.EPOCH_SEC

    fig, ax = plt.subplots(figsize=(7, 4))
    montages_list = list(cfg.MONTAGES.keys())
    data_to_plot = [qc[qc["montage"] == m]["usable_seconds"].values for m in montages_list]
    
    ax.boxplot(data_to_plot, tick_labels=montages_list, patch_artist=True,
               boxprops=dict(facecolor="lightblue", color="darkblue"),
               medianprops=dict(color="red", linewidth=1.5))
    ax.axhline(cfg.MIN_USABLE_EPOCHS * cfg.EPOCH_SEC, color="orange", linestyle=":", label=f"Min threshold ({cfg.MIN_USABLE_EPOCHS * cfg.EPOCH_SEC}s)")
    ax.set_ylabel("Usable Duration (seconds)")
    ax.set_xlabel("Montage")
    ax.set_title("Usable Epoch Duration per Montage Across Cohort")
    ax.legend(loc="upper right")
    fig.tight_layout()
    fig.savefig(RESULTS_DIR / "fig_usable_seconds.png", dpi=200)
    plt.close(fig)
    print("Saved fig_usable_seconds.png")


if __name__ == "__main__":
    main()

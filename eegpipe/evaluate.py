"""Repeated nested subject-level CV. Run once, after the plan is frozen:
    python -m eegpipe.evaluate"""
from __future__ import annotations

import json
import platform
from datetime import datetime, timezone

import numpy as np
import pandas as pd
import sklearn
from sklearn.dummy import DummyClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import GridSearchCV, StratifiedKFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from eegpipe import config as cfg


def make_logreg() -> Pipeline:
    return Pipeline([
        ("impute", SimpleImputer(strategy="median")),
        ("scale", StandardScaler()),
        ("clf", LogisticRegression(max_iter=5000, class_weight="balanced")),
    ])


def nested_cv(X, y, estimator, grid, seed, n_splits, n_repeats, inner_splits):
    """Each row = one participant, so no participant can be in train and test.
    Returns per-repeat AUROC and the mean out-of-fold score per participant."""
    oof_all, aucs = [], []
    for r in range(n_repeats):
        outer = StratifiedKFold(n_splits, shuffle=True, random_state=seed + r)
        oof = np.zeros(len(y))
        for tr, te in outer.split(X, y):
            if grid:
                inner = StratifiedKFold(inner_splits, shuffle=True, random_state=seed + 1000 + r)
                model = GridSearchCV(estimator, grid, cv=inner, scoring="roc_auc")
            else:
                model = estimator
            model.fit(X[tr], y[tr])
            oof[te] = model.predict_proba(X[te])[:, 1]
        aucs.append(roc_auc_score(y, oof))
        oof_all.append(oof)
    return np.array(aucs), np.mean(oof_all, axis=0)


def boot_ci(y, score, n_boot, seed, score2=None):
    """Participant bootstrap CI for AUROC (or AUROC difference if score2 given)."""
    rng = np.random.default_rng(seed)
    vals = []
    for _ in range(n_boot):
        idx = rng.integers(0, len(y), len(y))
        if len(np.unique(y[idx])) < 2:
            continue
        a = roc_auc_score(y[idx], score[idx])
        if score2 is not None:
            a -= roc_auc_score(y[idx], score2[idx])
        vals.append(a)
    return [float(v) for v in np.percentile(vals, [2.5, 97.5])]


def threshold_metrics(y, score):
    pred = (score >= 0.5).astype(int)
    sens = float(((pred == 1) & (y == 1)).sum() / (y == 1).sum())
    spec = float(((pred == 0) & (y == 0)).sum() / (y == 0).sum())
    return {"sensitivity": sens, "specificity": spec, "balanced_accuracy": (sens + spec) / 2}


def main() -> None:
    cfg.RESULTS_DIR.mkdir(exist_ok=True)
    part = pd.read_csv(cfg.RAW_DIR / "participants.tsv", sep="\t")
    part = part[part[cfg.GROUP_COL].isin([cfg.GROUP_AD, cfg.GROUP_CN])].copy()
    part["y"] = (part[cfg.GROUP_COL] == cfg.GROUP_AD).astype(int)

    qc = pd.read_csv(cfg.PROCESSED_DIR / "qc_report.csv")
    qc = qc[qc.montage.isin(cfg.MONTAGES)]
    ok = qc.groupby("participant_id").apply(
        lambda d: (len(d) == len(cfg.MONTAGES)) and (d.n_epochs_usable >= cfg.MIN_USABLE_EPOCHS).all()
    )
    keep_ids = set(ok[ok].index)
    cohort = part[part.participant_id.isin(keep_ids)].sort_values("participant_id").reset_index(drop=True)
    y = cohort["y"].to_numpy()
    cohort.to_csv(cfg.RESULTS_DIR / "cohort_used.csv", index=False)

    results = {
        "created_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "python": platform.python_version(), "sklearn": sklearn.__version__,
        "seed": cfg.SEED,
        "cohort": {"n_total": int(len(cohort)), "n_AD": int(y.sum()), "n_CN": int((1 - y).sum()),
                   "n_excluded_for_data_quality": int(len(part) - len(cohort))},
        "models": {}, "differences": {},
    }
    grid = {"clf__C": cfg.C_GRID}
    kw = dict(seed=cfg.SEED, n_splits=cfg.OUTER_SPLITS, n_repeats=cfg.OUTER_REPEATS,
              inner_splits=cfg.INNER_SPLITS)
    oof_store = {"participant_id": cohort.participant_id, "y": y}

    def record(name, X):
        aucs, oof = nested_cv(X, y, make_logreg(), grid, **kw)
        results["models"][name] = {
            "auroc_mean_over_repeats": float(aucs.mean()),
            "auroc_sd_over_repeats": float(aucs.std()),
            "auroc_of_mean_score": float(roc_auc_score(y, oof)),
            "auroc_95ci_participant_bootstrap": boot_ci(y, oof, cfg.N_BOOT, cfg.SEED),
            **threshold_metrics(y, oof)}
        oof_store[name] = oof
        print(name, round(float(aucs.mean()), 3))

    _, dummy_oof = nested_cv(np.zeros((len(y), 1)), y, DummyClassifier(strategy="prior"),
                             None, **kw)
    results["models"]["dummy_prior"] = {"auroc_of_mean_score": float(roc_auc_score(y, dummy_oof))}

    mm = cohort.get("MMSE") if "MMSE" in cohort.columns else None
    for m in cfg.MONTAGES:
        feats = pd.read_csv(cfg.PROCESSED_DIR / f"features_{m}.csv").set_index("participant_id")
        Xdf = feats.loc[cohort.participant_id]
        assert not any(c in Xdf.columns for c in ("participant_id", "Group", "y")), "ID/label leak"
        record(f"eeg_{m}", Xdf.to_numpy())
        if mm is not None:
            record(f"eeg_{m}_plus_mmse", np.column_stack([Xdf.to_numpy(), mm.to_numpy()]))
    if mm is not None:
        record("mmse_only", mm.to_numpy()[:, None])
    if {"Age", "Gender"} <= set(cohort.columns):
        sex = (cohort["Gender"].astype(str).str.upper().str[0] == "M").astype(float).to_numpy()
        record("age_sex_only", np.column_stack([cohort["Age"].to_numpy(), sex]))

    if "eeg_frontal4" in oof_store and "eeg_full19" in oof_store:
        results["differences"]["frontal4_minus_full19_auroc"] = {
            "estimate": float(roc_auc_score(y, oof_store["eeg_frontal4"])
                              - roc_auc_score(y, oof_store["eeg_full19"])),
            "ci95": boot_ci(y, oof_store["eeg_frontal4"], cfg.N_BOOT, cfg.SEED,
                            score2=oof_store["eeg_full19"])}

    (cfg.RESULTS_DIR / "metrics.json").write_text(json.dumps(results, indent=2))
    pd.DataFrame(oof_store).to_csv(cfg.RESULTS_DIR / "oof_scores.csv", index=False)
    print("Wrote results/metrics.json")


if __name__ == "__main__":
    main()

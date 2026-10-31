import numpy as np

from eegpipe.evaluate import boot_ci, make_logreg, nested_cv


def test_random_features_give_chance_auroc():
    rng = np.random.default_rng(0)
    X = rng.normal(size=(60, 19))
    y = np.array([0] * 30 + [1] * 30)
    aucs, _ = nested_cv(X, y, make_logreg(), {"clf__C": [0.1, 1.0]},
                        seed=1, n_splits=5, n_repeats=3, inner_splits=3)
    assert abs(aucs.mean() - 0.5) < 0.2  # large gap would signal leakage


def test_bootstrap_ci_ordered_and_bounded():
    y = np.array([0, 1] * 20)
    score = np.linspace(0, 1, 40)
    lo, hi = boot_ci(y, score, 200, 0)
    assert 0 <= lo <= hi <= 1

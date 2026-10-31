# Model card: reduced-montage EEG classifier (research prototype)

- **Intended use:** Methodological research on montage reduction. NOT diagnosis, triage or CSF replacement.
- **Data:** OpenNeuro ds004504, N = 37 (AD 21, CN 16), single hospital.
- **Task:** AD vs cognitively normal (dataset labels), not CSF/biomarker status.
- **Inputs:** Relative band power (delta/theta/alpha/beta) from Welch PSD, median over clean 4 s epochs.
- **Model:** L2 logistic regression, C chosen in inner CV.
- **Evaluation:** Repeated nested subject-level CV; AUROC with participant-bootstrap CI (see results/metrics.json).
- **Not evaluated:** External cohorts, other devices, other populations, calibration, prospective use.
- **Known risks:** Small n, optimistic bias possible, conventional scalp EEG != wearable signal.
- **Reproducibility:** Seed 42, config in eegpipe/config.py, environment in docs/environment_record_*.txt.

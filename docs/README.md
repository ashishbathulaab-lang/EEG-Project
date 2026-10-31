# Reduced-Montage Resting EEG: Retrospective Research Prototype

## Purpose
This repository contains a retrospective research prototype evaluating whether reduced-montage resting-state EEG (derived from public OpenNeuro dataset `ds004504`) can classify Alzheimer's Disease (AD) vs. cognitively normal (CN) controls. It is built strictly for methodological exploration and model validation workflows.

---

## Application Modes
The project provides three functional modes:
1. **Mode A (Synthetic Demonstration):** `app/main.py` — Interactive demo app populated with synthetic data and explicit simulation warnings.
2. **Mode B (Research Results Viewer):** `app/research_app.py` — A read-only Streamlit viewer displaying held-out nested cross-validation metrics (`results/metrics.json`) and summary figures. Runs via:
   ```bash
   python -m streamlit run app/research_app.py
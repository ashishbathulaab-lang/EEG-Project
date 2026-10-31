"""Run: python -m streamlit run app/research_app.py"""
import json
from pathlib import Path

import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
METRICS = ROOT / "results" / "metrics.json"
FIG = ROOT / "results" / "fig_auroc_by_montage.png"

st.set_page_config(page_title="EEG montage-reduction study", layout="wide")
st.title("Reduced-montage resting EEG: retrospective research prototype")
st.error("Research prototype. Not a diagnostic tool. Not validated on any wearable "
         "device. Labels are dataset diagnoses (AD vs control), not CSF status.")

if not METRICS.exists():
    st.warning("results/metrics.json not found. Run the evaluation first.")
    st.stop()

res = json.loads(METRICS.read_text())
c = res["cohort"]
st.subheader("Cohort")
st.write(f"{c['n_total']} participants ({c['n_AD']} AD, {c['n_CN']} control); "
         f"{c['n_excluded_for_data_quality']} excluded for data quality.")

rows = []
for name, m in res["models"].items():
    ci = m.get("auroc_95ci_participant_bootstrap", [None, None])
    rows.append({"model": name, "AUROC": round(m["auroc_of_mean_score"], 3),
                 "CI low": None if ci[0] is None else round(ci[0], 3),
                 "CI high": None if ci[1] is None else round(ci[1], 3)})
st.subheader("Held-out results (participant-level, nested CV)")
st.dataframe(pd.DataFrame(rows), use_container_width=True)
if FIG.exists():
    st.image(str(FIG))

st.subheader("Limitations")
st.markdown("""
- Single-site public dataset; no external validation.
- Small sample; confidence intervals are wide.
- Retrospective analysis on conventional scalp EEG, not a wearable device.
- Classifier output is not a diagnosis and not a calibrated risk.
- MMSE-containing models are shown for ablation only.
""")
st.caption(f"Run {res['created_utc']} | Python {res['python']} | scikit-learn {res['sklearn']}")

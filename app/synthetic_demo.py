"""Mode A: synthetic demonstration only.
Run from the project root: python -m streamlit run app/synthetic_demo.py
"""
from pathlib import Path

import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
EEG_DIR = ROOT / "data" / "dummy" / "eeg"
TIME_NAMES = {"time", "time_s", "t", "timestamp"}

st.set_page_config(page_title="Synthetic EEG demo")
st.title("EEG Project: synthetic demonstration")
st.warning(
    "SYNTHETIC DEMONSTRATION DATA. These are artificial signals, not real "
    "patients. No clinical validity. Nothing here is a prediction or a diagnosis."
)

files = sorted(EEG_DIR.glob("*_eeg.csv")) if EEG_DIR.exists() else []
if not files:
    st.error(
        f"No synthetic EEG files found in {EEG_DIR}. "
        "Run scripts/generate_dummy_data.py first."
    )
    st.stop()

choice = st.selectbox("Synthetic recording", [f.name for f in files])

try:
    df = pd.read_csv(EEG_DIR / choice)
except (OSError, pd.errors.ParserError, pd.errors.EmptyDataError) as exc:
    st.error(f"Could not read {choice}: {exc}")
    st.stop()

numeric = df.select_dtypes("number")
if numeric.empty:
    st.error(f"{choice} has no numeric columns.")
    st.stop()

time_cols = [c for c in numeric.columns if c.lower() in TIME_NAMES]
channels = [c for c in numeric.columns if c not in time_cols]
selected = st.multiselect("Channels to plot", channels, default=channels[:2])

if selected:
    plot_df = numeric[selected]
    if time_cols:
        plot_df = plot_df.set_index(numeric[time_cols[0]])
    st.line_chart(plot_df)
else:
    st.info("Select at least one channel.")

st.caption(f"{len(df)} samples, {len(channels)} channels. Synthetic file: {choice}")
python -c '

import streamlit as st
import pandas as pd

st.title("EEG Project Dashboard")

st.warning("SYNTHETIC DEMONSTRATION DATA. Not real patients. No clinical validity. "
            "The CSF values shown are stored reference records, not predictions.")
st.write("Welcome to your EEG analysis app!")

# Load the dummy data
try:
    df = pd.read_csv("data/dummy_eeg.csv")
    st.subheader("Raw EEG Data Preview")
    st.dataframe(df.head())
    
    st.line_chart(df[['Channel_1', 'Channel_2']])
except Exception as e:
    st.error(f"Could not load data: {e}")
    
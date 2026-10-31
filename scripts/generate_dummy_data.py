import os
import pandas as pd
import numpy as np

# Create data directory if it doesn't exist
os.makedirs("data", exist_ok=True)

# Generate dummy EEG data
np.random.seed(42)
data = {
    "Timestamp": pd.date_range(start="2026-01-01", periods=100, freq="s"),
    "Channel_1": np.random.randn(100),
    "Channel_2": np.random.randn(100),
    "Target": np.random.choice([0, 1], size=100)
}

df = pd.DataFrame(data)
df.to_csv("data/dummy_eeg.csv", index=False)
print("Dummy EEG data generated successfully at data/dummy_eeg.csv!")
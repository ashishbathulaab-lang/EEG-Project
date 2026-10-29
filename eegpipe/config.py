from pathlib import Path

# Paths
ROOT_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = ROOT_DIR / "data" / "raw" / "ds004504"
PROCESSED_DIR = ROOT_DIR / "data" / "processed"

# Group Column & Standard 10-20 Channels
GROUP_COL = "Group"
FULL_19 = [
    "Fp1", "Fp2", "F3", "F4", "C3", "C4", "P3", "P4", "O1", "O2",
    "F7", "F8", "T3", "T4", "T5", "T6", "Fz", "Cz", "Pz"
]

# Frequency Bands
BANDS = {
    "delta": (1.0, 4.0),
    "theta": (4.0, 8.0),
    "alpha": (8.0, 13.0),
    "beta": (13.0, 30.0),
}

# Preprocessing & Rejection Parameters
FILTER_BAND_HZ = (0.5, 40.0)
EPOCH_SEC = 4.0
PTP_REJECT_V = 150e-6  # 150 uV peak-to-peak threshold
FLAT_V = 1e-6          # 1 uV flatness threshold

# Montage Definitions for Analysis
MONTAGES = {
    "full19": FULL_19,
    "frontal4": ["Fp1", "Fp2", "F7", "F8"],
    "fronto_temporal4": ["F7", "F8", "T3", "T4"],
    "prefrontal2": ["Fp1", "Fp2"],
    "occipital2": ["O1", "O2"],
}

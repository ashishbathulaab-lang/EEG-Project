from pathlib import Path

# Root directory of the project
ROOT_DIR = Path(__file__).resolve().parent

# Key subdirectories
APP_DIR = ROOT_DIR / "app"
DATA_DIR = ROOT_DIR / "data"
SCRIPTS_DIR = ROOT_DIR / "scripts"
EEG_DUMMY_DIR = DATA_DIR / "dummy" / "eeg"

# Ensure directories exist
DATA_DIR.mkdir(exist_ok=True)
EEG_DUMMY_DIR.mkdir(parents=True, exist_ok=True)

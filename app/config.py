"""
FuturSet Jobs Portal - Configuration Module
"""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
ROOT_DIR = BASE_DIR.parent
DATA_DIR = BASE_DIR / "data"
STATIC_DIR = BASE_DIR / "static"
TEMPLATES_DIR = BASE_DIR / "templates"

DB_PATH = DATA_DIR / "futurset_jobs.db"

HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8000"))

BRAND_NAME = "FuturSet"
PORTAL_TITLE = "FuturSet Rojgar - Next-Gen Government & State Jobs Portal"
PORTAL_GUJARAT_TITLE = "FuturSet ગુજરાત સરકારી ભરતી પોર્ટલ (Gujarat Govt Jobs Hub)"
APP_VERSION = "2.4.0"

BOARDS_GUJARAT = [
    "OJAS", "GPSC", "GSSSB", "Police", "High Court",
    "GSRTC", "Forest", "Electricity", "AMC/SMC", "Vidhyasahayak"
]
BOARDS_CENTRAL = ["SSC", "UPSC", "RRB", "Banking", "Defence", "ISRO/DRDO", "PSU"]

DATA_DIR.mkdir(parents=True, exist_ok=True)
STATIC_DIR.mkdir(parents=True, exist_ok=True)
TEMPLATES_DIR.mkdir(parents=True, exist_ok=True)

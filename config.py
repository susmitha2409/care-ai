import os
from pathlib import Path
from typing import Dict, Any

# Base Directory
BASE_DIR = Path(__file__).resolve().parent

# Database Configuration
DB_PATH = os.environ.get("CARESIM_DB_PATH", str(BASE_DIR / "caresim.db"))

# Groq Configuration
# Prioritize environment variables, then fallback to Streamlit secrets if running inside Streamlit
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
GROQ_MODEL = os.environ.get("GROQ_MODEL", "openai/gpt-oss-120b")
GROQ_TEMPERATURE = float(os.environ.get("GROQ_TEMPERATURE", "0.6"))
GROQ_MAX_TOKENS = int(os.environ.get("GROQ_MAX_TOKENS", "1024"))

# App Settings
APP_NAME = "CareSim AI"
APP_TAGLINE = "Agentic Virtual Patient Simulation Platform"
APP_VERSION = "1.0.0"

# Demo Mode
DEMO_MODE_DEFAULT = os.environ.get("CARESIM_DEMO_MODE", "false").lower() in ("true", "1", "yes")

# Educational Rubric Criteria and Weights
RUBRIC_WEIGHTS: Dict[str, float] = {
    "communication": 0.15,
    "information_gathering": 0.20,
    "holistic_assessment": 0.15,
    "risk_identification": 0.20,
    "clinical_reasoning": 0.15,
    "person_centred_care": 0.15,
}

# Educational Safety Disclaimer
DISCLAIMER_TEXT = (
    "CareSim AI is an educational simulation platform designed for healthcare students and "
    "practitioners. It is NOT a medical device, diagnostic tool, or substitute for professional "
    "clinical judgment. All patient profiles, data, and scenarios are fictional. In the event of "
    "a real-world medical emergency, immediately contact your local emergency services (e.g. 911 / 999 / 112)."
)

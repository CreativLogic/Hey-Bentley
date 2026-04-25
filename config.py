"""
Bentley Voice — Configuration
"""
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR  = Path(__file__).parent.resolve()
FILES_DIR = Path(os.getenv("FILES_DIR", BASE_DIR / "files"))
LOGS_DIR  = BASE_DIR / "logs"
FILES_DIR.mkdir(parents=True, exist_ok=True)
LOGS_DIR.mkdir(parents=True, exist_ok=True)

NOTION_API_KEY       = os.getenv("NOTION_API_KEY", "")
NOTION_DEFAULT_DB_ID = os.getenv("NOTION_DEFAULT_DATABASE_ID", "")

# "auto" → act immediately | "confirm" → ask before every action
DEFAULT_MODE = "confirm"

VOICE_RATE   = 175
VOICE_VOLUME = 0.9
BENTLEY_NAME = "Bentley"
WAKE_PHRASE  = "hey bentley"

SEARCH_MAX_RESULTS = 5
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

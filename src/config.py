import os
import json
from dotenv import load_dotenv

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
LM_STUDIO_URL = os.getenv("LM_STUDIO_URL")
MODEL = os.getenv("MODEL")
FRA_PATH = os.getenv("FRA_PATH")

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_DIR = os.path.join(ROOT_DIR, "data")
IMAGE_DIR = os.path.join(DATA_DIR, "images")
PROMPT_DIR = os.path.join(ROOT_DIR, "prompts")

OVERPASS_HEADERS = {"User-Agent": "BusStopEvaluator/1.0"}

DEBUG = os.getenv("DEBUG", "false").lower() == "true"

# _metadata = None

# def get_metadata() -> dict:
#     global _metadata
#     if _metadata is None:
#         metadata_path = os.path.join(DATA_DIR, "district_metadata.json")
#         if not os.path.exists(metadata_path):
#             return {}
#         with open(metadata_path) as f:
#             _metadata = json.load(f)
#     return _metadata

def load_prompt(name: str) -> str:
    with open(os.path.join(PROMPT_DIR, f"{name}.txt")) as f:
        return f.read().strip()

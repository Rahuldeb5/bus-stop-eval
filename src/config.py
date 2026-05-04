import os
import json
from dotenv import load_dotenv

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
LM_STUDIO_URL = os.getenv("LM_STUDIO_URL")
MODEL = os.getenv("MODEL")

OVERPASS_HEADERS = {"User-Agent": "BusStopEvaluator/1.0"}
PROMPT_DIR = "../prompts"
IMAGE_DIR = "../data/images/main"

FRA_PATH = os.getenv("FRA_PATH")

with open("../data/district_metadata.json") as f:
    METADATA = json.load(f)

def load_prompt(name: str) -> str:
    with open(os.path.join(PROMPT_DIR, f"{name}.txt")) as f:
        return f.read().strip()
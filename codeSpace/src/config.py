import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# API Credentials
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
GITHUB_PAT = os.getenv("GITHUB_PAT")
GITHUB_OWNER = os.getenv("GITHUB_OWNER")
GITHUB_REPO = os.getenv("GITHUB_REPO")

# Endpoints and Models
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"

MODELS = {
    "ingestion": "openrouter/auto",
    "evaluation": "openrouter/auto",
    "synthesis": "openrouter/auto"
}

# Directory Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INPUT_DIR = os.path.join(BASE_DIR, "data", "input")
OUTPUT_DIR = os.path.join(BASE_DIR, "data", "output")

# Ensure output directory exists
os.makedirs(OUTPUT_DIR, exist_ok=True)

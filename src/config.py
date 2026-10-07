import os
from dotenv import load_dotenv

load_dotenv()

NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")

if not NEO4J_URI:
    raise ValueError("NEO4J_URI is missing")

if not NEO4J_USERNAME:
    raise ValueError("NEO4J_USERNAME is missing")

if not NEO4J_PASSWORD:
    raise ValueError("NEO4J_PASSWORD is missing")

if not GEMINI_API_KEY and not OPENAI_API_KEY:
    raise ValueError("GEMINI_API_KEY (or OPENAI_API_KEY) is missing in .env")
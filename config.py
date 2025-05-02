import os
from dotenv import load_dotenv

load_dotenv()
MODEL_NAME = "all-MiniLM-L6-v2"
QDRANT_URL = os.environ.get("QDRANT_URL")
OPENAI_KEY = os.environ.get("OPENAI_KEY")

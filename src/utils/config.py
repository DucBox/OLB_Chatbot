from pathlib import Path
import os
from dotenv import load_dotenv


# === Base project root ===
BASE_DIR = Path(__file__).resolve().parents[2]  # chatbot_rag/

# === Define subdirectories ===
DATA_PATH = BASE_DIR / "data"
HISTORY_STORE_PATH = DATA_PATH / "history"
LOG_FILE_XML = DATA_PATH / "history" / "chat_history.xml"
CHROMADB_PATH = str(DATA_PATH / "chroma_db")

FIREBASE_COLLECTION_NAME = "olb_embeddings"
TOKEN_LIMIT = 2000 
KEEP_LAST_N_PAIRS = 1
CHUNK_SIZE = 700

# API KEY LOADED
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise RuntimeError("❌ OPENAI_API_KEY not found in environment variables.")


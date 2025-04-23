from pathlib import Path
import os
from dotenv import load_dotenv
TABLE_NAMES = ["bảng 1", "bảng 2", "bảng 3", "bảng 4", "bảng 5"]

# === Base project root ===
BASE_DIR = Path(__file__).resolve().parents[2]  # chatbot_rag/

# === Define subdirectories ===
DATA_PATH = BASE_DIR / "data"
HISTORY_STORE_PATH = DATA_PATH / "history"
LOG_FILE_XML = DATA_PATH / "history" / "chat_history.xml"
CHROMADB_PATH = str(DATA_PATH / "chroma_db")

TEMP_TXT_PATH = DATA_PATH / "uploads"
TEMP_PDF_PATH = DATA_PATH / "pdf_split"
FIREBASE_COLLECTION_NAME = "olb_embeddings"
TOKEN_LIMIT = 64000 
KEEP_LAST_N_PAIRS = 1
CHUNK_SIZE = 2000

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise RuntimeError("❌ OPENAI_API_KEY not found in environment variables.")

public_key = os.getenv("public_key")
if not public_key:
    raise RuntimeError("❌ public_key not found in environment variables.")

secret_key = os.getenv("secret_key")
if not secret_key:
    raise RuntimeError("❌ secret_key not found in environment variables.")

SURYA_API_KEY = os.getenv("SURYA_API_KEY")
if not SURYA_API_KEY:
    raise RuntimeError("❌ SURYA_API_KEY not found in environment variables.")


from pathlib import Path

# === Base project root ===
BASE_DIR = Path(__file__).resolve().parents[2]  # chatbot_rag/

# === Define subdirectories ===
DATA_PATH = BASE_DIR / "data"
LOG_FILE_XML = DATA_PATH / "history" / "chat_history.xml"
CHROMADB_PATH = str(DATA_PATH / "chroma_db")

FIREBASE_COLLECTION_NAME = "olb_embeddings"
TOKEN_LIMIT = 64000 
KEEP_LAST_N_PAIRS = 1
CHUNK_SIZE = 700


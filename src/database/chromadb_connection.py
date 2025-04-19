import chromadb
from src.utils.config import CHROMADB_PATH

# ✅ Init Chroma client
chroma_client = chromadb.PersistentClient(path=str(CHROMADB_PATH))

# ✅ Check + create collection if not exists
try:
    collection = chroma_client.get_collection(name="document_embeddings")
except Exception as e:
    print(f"⚠️ Could not get collection. Reason: {e}\n→ Creating new one...")
    collection = chroma_client.create_collection(name="document_embeddings")

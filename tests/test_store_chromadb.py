import sys
import os
from pathlib import Path

from src.database.chromadb_connection import collection

def inspect_chroma_collection():
    """
    Print all documents, ids, and metadata from current ChromaDB collection.
    """
    try:
        results = collection.get(include=["documents", "metadatas", "embeddings"])
        ids = results.get("ids", [])
        docs = results.get("documents", [])
        metas = results.get("metadatas", [])
        embeds = results.get("embeddings", [])
        

        print("🧠 ChromaDB Collection Overview:")
        for i in range(len(ids)):
            print(f"\n--- Entry {i+1} ---")
            print(f"ID       : {ids[i]}")
            print(f"Metadata : {metas[i]}")
            print(f"Text     : {docs[i][:100]}...")  
            print(f"Embed[0:5]: {results['embeddings'][i][:5]}\n")

    except Exception as e:
        print(f"❌ Failed to inspect collection: {str(e)}")

if __name__ == "__main__":
    inspect_chroma_collection()

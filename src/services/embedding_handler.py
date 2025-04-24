import sys
import os
import fitz 
import chromadb
import openai
from src.utils.config import FIREBASE_COLLECTION_NAME, OPENAI_API_KEY
from src.database.chromadb_connection import collection
from src.database.firebase_connection import db  
from datetime import datetime
from dotenv import load_dotenv

client = openai.OpenAI(api_key=OPENAI_API_KEY)

def store_embedding_to_firebase(
    embedding: list[float],
    text: str,
    chunk_id: str,
    metadata: dict
):
    """
    Lưu embedding và metadata vào Firestore (Firebase).
    """
    try:
        data = {
            "chunk_id": chunk_id,
            "embedding": embedding,
            "text": text,
            "created_at": datetime.utcnow().isoformat(),
            **metadata
        }

        db.collection(FIREBASE_COLLECTION_NAME).document(chunk_id).set(data)
        print(f"✅ [FIREBASE] Stored chunk: {chunk_id}")

    except Exception as e:
        print(f"❌ [FIREBASE] Failed to store chunk: {chunk_id}. Reason: {e}")

def embed_text(text: str, chunk_id: str, metadata: dict):
    """
    Generates embedding for the text and stores it in ChromaDB.

    Args:
        text (str): The text chunk to embed.
        chunk_id (str): Unique ID for this chunk (e.g., docid_chunk_0).
        metadata (dict): Metadata for this chunk (doc_id, source_type, user info, etc.)

    Returns:
        tuple: (embedding vector, chunk_id)
    """
    embedding = generate_embedding(text)
    if embedding:
        store_embedding_to_firebase(embedding, text, chunk_id, metadata)
    return embedding, chunk_id

def generate_embedding(text: str) -> list[float]:
    """
    Generates an embedding vector for the given text using OpenAI.
    """
    try:
        response = client.embeddings.create(
            input=text,
            model="text-embedding-3-small"
        )
        return response.data[0].embedding
    except Exception as e:
        print(f"⚠️ Error generating embedding: {str(e)}")
        return None
    

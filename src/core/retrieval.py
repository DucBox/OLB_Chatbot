import faiss
import numpy as np
from src.database.firebase_connection import db
from src.utils.config import FIREBASE_COLLECTION_NAME

def retrieve_relevant_chunks(query_embedding: list[float], top_k: int, user_id: str) -> list[dict]:
    """
    Retrieve top-k relevant document chunks Firestore using FAISS + embedding.
    Returns:
        list[dict]:
            - Category
            - Document Title
            - Chunk_ID
            - Content
    """
    try:
        docs = db.collection(FIREBASE_COLLECTION_NAME).stream()
        texts, embeddings, metadata = [], [], []

        for doc in docs:
            data = doc.to_dict()
            if data.get("source_type") in [f"{user_id}_conversation", "upload", "google_sheet"]:
                if all(k in data for k in ("embedding", "text", "category", "doc_title", "chunk_id")):
                    embeddings.append(data["embedding"])
                    texts.append(data["text"])
                    metadata.append({
                        "category": data["category"],
                        "doc_title": data["doc_title"],
                        "chunk_id": data["chunk_id"],
                        "content": data["text"]
                    })

        if not embeddings:
            return [{"error": "⚠️ Không có dữ liệu embedding để search."}]

        dim = len(embeddings[0])
        index = faiss.IndexFlatL2(dim)
        index.add(np.array(embeddings).astype('float32'))

        query_np = np.array([query_embedding]).astype('float32')
        distances, indices = index.search(query_np, top_k)

        results = []
        for idx in indices[0]:
            if idx < len(metadata):
                results.append(metadata[idx])

        return results if results else [{"error": "⚠️ Không tìm thấy kết quả gần nhất."}]

    except Exception as e:
        return [{"error": f"⚠️ Retrieval error: {str(e)}"}]



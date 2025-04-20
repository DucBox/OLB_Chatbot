# import chromadb
# import os
# from src.utils.config import CHROMADB_PATH
# from src.database.chromadb_connection import collection

# def retrieve_relevant_chunks(query_embedding: list[float], top_k: int = 3) -> list[str]:
#     """
#     Retrieves relevant document chunks from ChromaDB using the provided query embedding.

#     Args:
#         query_embedding (list): Embedding vector of the user's query.
#         top_k (int): Number of top relevant chunks to retrieve.

#     Returns:
#         list: A list of relevant document chunks.
#     """
#     try:
#         results = collection.query(query_embeddings=[query_embedding], n_results=top_k)

#         if results.get("documents"):
#             return results["documents"][:top_k]
#         else:
#             return ["⚠️ No relevant information found in the uploaded documents."]

#     except Exception as e:
#         return [f"⚠️ Retrieval error: {str(e)}"]

import faiss
import numpy as np
from src.database.firebase_connection import db
from src.utils.config import FIREBASE_COLLECTION_NAME

def retrieve_relevant_chunks(query_embedding: list[float], top_k: int, user_id: str) -> list[str]:
    """
    Truy vấn top-k văn bản gần nhất từ Firestore dùng FAISS + embedding.

    Args:
        query_embedding (list): vector embedding của user input
        top_k (int): số chunk gần nhất cần lấy

    Returns:
        list[str]: Danh sách văn bản gần nhất
    """
    try:
        docs = db.collection(FIREBASE_COLLECTION_NAME).stream()
        texts, embeddings = [], []

        for doc in docs:
            data = doc.to_dict()
            if data.get("source_type") == "upload" or data.get("source_type") == f"{user_id}_conversation":
                if "embedding" in data and "text" in data:
                    embeddings.append(data["embedding"])
                    texts.append(data["text"])

        if not embeddings:
            return ["⚠️ Không có dữ liệu embedding để search."]

        # 2. Dùng FAISS để search
        dim = len(embeddings[0])
        index = faiss.IndexFlatL2(dim)
        index.add(np.array(embeddings).astype('float32'))

        query_np = np.array([query_embedding]).astype('float32')
        distances, indices = index.search(query_np, top_k)

        # 3. Lấy văn bản tương ứng
        results = []
        for idx in indices[0]:
            if idx < len(texts):
                results.append(texts[idx])

        return results if results else ["⚠️ Không tìm thấy kết quả gần nhất."]

    except Exception as e:
        return [f"⚠️ Retrieval error: {str(e)}"]


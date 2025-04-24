import os
from src.database.firebase_connection import db 
from src.utils.config import FIREBASE_COLLECTION_NAME
       
def list_all_doc_ids_firebase(user_id: str) -> list[str]:
    """
    Truy vấn tất cả doc_id từ:
    - Public uploads (source_type == 'upload')
    - Lịch sử chat riêng của user (source_type == '{user_id}_conversation')

    Returns:
        list[str]: Danh sách các doc_id (duy nhất, đã sắp xếp).
    """
    try:
        public_docs = db.collection(FIREBASE_COLLECTION_NAME) \
                        .where("source_type", "==", "upload") \
                        .stream()

        personal_docs = db.collection(FIREBASE_COLLECTION_NAME) \
                        .where("source_type", "==", f"{user_id}_conversation") \
                        .stream()
        
        online_docs = db.collection(FIREBASE_COLLECTION_NAME) \
                        .where("source_type", "==", "google_sheet") \
                        .stream()

        all_docs = list(public_docs) + list(personal_docs) + list(online_docs)

        doc_ids = {
            doc.to_dict().get("doc_id")
            for doc in all_docs
            if doc.to_dict().get("doc_id")
        }

        return sorted(doc_ids)
    except Exception as e:
        print(f"❌ Error listing doc_ids: {e}")
        return []

def delete_document_firebase(doc_id: str):
    """
    Xoá tất cả embedding chunks có doc_id tương ứng trong Firestore.
    """
    try:
        # Dùng positional arguments (truyền 3 đối số)
        docs = db.collection(FIREBASE_COLLECTION_NAME).where("doc_id", "==", doc_id).stream()
        count = 0
        for doc in docs:
            db.collection(FIREBASE_COLLECTION_NAME).document(doc.id).delete()
            count += 1
        print(f"🗑️ Deleted {count} chunks with doc_id: {doc_id}")
    except Exception as e:
        print(f"❌ Error deleting doc_id {doc_id}: {e}")

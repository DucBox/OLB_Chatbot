import os
from src.database.firebase_connection import db 
from src.utils.config import FIREBASE_COLLECTION_NAME
       
def list_all_docs_metadata_firebase(user_id: str) -> list[dict]:
    """
    Return all documents from db: upload, conversation, google_sheet.
    Including metadata: doc_id, doc_title, category, ...
    """
    try:
        types = ["uploaded_file", f"{user_id}_conversation", "google_sheet"]
        all_docs = []
        for t in types:
            docs = db.collection(FIREBASE_COLLECTION_NAME).where("source_type", "==", t).stream()
            all_docs.extend([doc.to_dict() for doc in docs])
        
        return all_docs
    except Exception as e:
        print(f"❌ Error fetching doc metadata: {e}")
        return []

def delete_by_doc_id(doc_id: str):
    try:
        docs = db.collection(FIREBASE_COLLECTION_NAME).where("doc_id", "==", doc_id).stream()
        count = 0
        for doc in docs:
            db.collection(FIREBASE_COLLECTION_NAME).document(doc.id).delete()
            count += 1
        print(f"🗑️ Deleted {count} chunks with doc_id: {doc_id}")
    except Exception as e:
        print(f"❌ Error deleting doc_id {doc_id}: {e}")

def delete_by_category(category: str):
    try:
        docs = db.collection(FIREBASE_COLLECTION_NAME).where("category", "==", category).stream()
        count = 0
        for doc in docs:
            db.collection(FIREBASE_COLLECTION_NAME).document(doc.id).delete()
            count += 1
        print(f"🗑️ Deleted {count} chunks in category: {category}")
    except Exception as e:
        print(f"❌ Error deleting category {category}: {e}")

def delete_by_doc_title(category: str, doc_title: str):
    try:
        docs = db.collection(FIREBASE_COLLECTION_NAME) \
                 .where("category", "==", category) \
                 .where("doc_title", "==", doc_title) \
                 .stream()
        count = 0
        for doc in docs:
            db.collection(FIREBASE_COLLECTION_NAME).document(doc.id).delete()
            count += 1
        print(f"🗑️ Deleted {count} chunks in {category} / {doc_title}")
    except Exception as e:
        print(f"❌ Error deleting doc_title {doc_title} in category {category}: {e}")


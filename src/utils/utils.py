import os
import tiktoken  
import fitz
from datetime import datetime
from pathlib import Path
from src.utils.config import CHUNK_SIZE, BASE_DIR, FIREBASE_COLLECTION_NAME
from src.database.chromadb_connection import collection
from src.database.firebase_connection import db  
import xml.etree.ElementTree as ET
import streamlit as st

def count_tokens(text):
    """
    Counts the number of tokens in a given text using tiktoken.

    Args:
        text (str): The text to be tokenized.

    Returns:
        int: The token count.
    """
    encoding = tiktoken.encoding_for_model("gpt-4o")
    return len(encoding.encode(text))

def extract_text_from_pdf(pdf_path):
    """
    Extracts text from a PDF file.

    Args:
        pdf_path (str): The path to the PDF file.

    Returns:
        str: The extracted text.
    """
    try:
        doc = fitz.open(pdf_path)
        text = "\n".join(page.get_text() for page in doc)
        return text.strip()
    except Exception as e:
        print(f"⚠️ Error extracting text from PDF: {str(e)}")
        return ""
    
def extract_text_from_txt(txt_path):
    """
    Extracts text from a TXT file.

    Args:
        txt_path (str): The path to the TXT file.

    Returns:
        str: The extracted text.
    """
    try:
        with open(txt_path, "r", encoding="utf-8") as file:
            return file.read().strip()
    except Exception as e:
        print(f"⚠️ Error reading TXT file: {str(e)}")
        return ""
    
def chunk_text(text, chunk_size=CHUNK_SIZE):
    """
    Splits text into fixed-size chunks.

    Args:
        text (str): The full text to be chunked.
        chunk_size (int): The maximum number of words per chunk.

    Returns:
        list: A list of text chunks.
    """
    words = text.split()
    chunks = [" ".join(words[i:i + chunk_size]) for i in range(0, len(words), chunk_size)]
    return chunks

def format_chat_history(chat_history: list[tuple[str, str]]) -> str:
    """
    Converts a list of (user, bot) pairs into a single text block.

    Args:
        chat_history (list): List of conversation pairs.

    Returns:
        str: Concatenated string representing full conversation.
    """
    return "\n".join([f"User: {user}\nBot: {bot}" for user, bot in chat_history])

def save_uploaded_file(file_path: str, doc_id: str):
    """Lưu lại bản gốc file upload để tái sử dụng."""
    UPLOADS_DIR = BASE_DIR / "data" / "uploads"
    UPLOADS_DIR.mkdir(parents=True, exist_ok=True)

    file_name = Path(file_path).name
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    new_name = f"{doc_id}__{timestamp}__{file_name}"
    new_path = UPLOADS_DIR / new_name

    with open(file_path, "rb") as src, open(new_path, "wb") as dst:
        dst.write(src.read())
    print(f"✅ Saved uploaded file to: {new_path}")


def list_all_doc_ids_chromadb() -> list[str]:
    """
    Returns a list of all unique doc_id values currently stored in the ChromaDB collection.

    Returns:
        list[str]: List of doc_ids found in metadata.
    """
    try:
        all = collection.get(include=["metadatas"], limit=None)
        metadatas = all.get("metadatas", [])

        doc_ids = {meta.get("doc_id") for meta in metadatas if "doc_id" in meta}
        return sorted(doc_ids)  # ✅ Duy nhất và gọn gàng

    except Exception as e:
        print(f"⚠️ Failed to list doc_ids: {str(e)}")
        return []

def delete_document_chromadb(doc_id: str):
    """
    Deletes all embedding chunks from ChromaDB that belong to a specific doc_id.

    Args:
        doc_id (str): The ID of the document to delete (not chunk_id).
    """
    try:
        collection.delete(where={"doc_id": doc_id})
        print(f"🗑️ Successfully deleted all chunks with doc_id: {doc_id}")
    except Exception as e:
        print(f"⚠️ Failed to delete doc_id {doc_id}: {str(e)}")
        
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

        all_docs = list(public_docs) + list(personal_docs)

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

def parse_history_xml(xml_path: str) -> list[tuple[str, str]]:
    """
    Đọc file XML và trả ra danh sách (user, bot) pairs.
    """
    try:
        tree = ET.parse(xml_path)
        root = tree.getroot()

        history = []
        for conv in root.findall("conversation"):
            user_msg = conv.find("user").text or "[Empty]"
            bot_msg = conv.find("bot").text or "[Empty]"
            history.append((user_msg, bot_msg))

        return history
    except Exception as e:
        print(f"❌ Error parsing XML {xml_path}: {e}")
        return []

def display_history_chat(history: list[tuple[str, str]], user_id: str):
    """
    Hiển thị nội dung lịch sử chat dạng gọn đẹp trên UI.
    """
    for i, (user_msg, bot_msg) in enumerate(history):
        st.markdown(f"**🧑 {user_id}:** {user_msg}")
        st.markdown(f"**🤖 Bot:** {bot_msg}")
        st.markdown("---")

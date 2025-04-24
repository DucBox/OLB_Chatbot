import os
import chromadb
from datetime import datetime
from src.utils.config import CHUNK_SIZE
from src.services.embedding_handler import embed_text
from src.utils.text_chunking import chunk_text
from src.utils.utils import save_uploaded_file
from src.services.txt_pdf_handler import extract_document_text

def process_uploaded_docs(file_path: str, doc_id: str, uploaded_by: str, position: str):
    """
    Full pipeline to process uploaded document:
    1. Extract text from file
    2. Chunk the text
    3. Embed each chunk into vector DB with full metadata

    Args:
        file_path (str): Path to a PDF or TXT document.
        doc_id (str): Unique identifier for the document.
        uploaded_by (str): User who uploaded the file.
        position (str): Position of the uploader (e.g., HR Manager).
    """
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        return

    # Step 1: Extract and save
    text, _ = extract_document_text(file_path)
    if not text:
        print("⚠️ No text extracted.")
        return
    
    # save_uploaded_file(file_path, doc_id)

    # Step 2: Chunk
    chunks = chunk_text(text, chunk_size=CHUNK_SIZE)

    # Step 3: Embed with metadata
    timestamp = datetime.now().isoformat()
    for i, chunk in enumerate(chunks):
        chunk_id = f"{doc_id}_chunk_{i}"
        metadata = {
            "doc_id": doc_id,
            "chunk_index": i,
            "source_type": "upload",
            "uploaded_by": uploaded_by,
            "position": position,
            "timestamp": timestamp
        }
        embed_text(chunk, chunk_id, metadata)

    print(f"✅ Embedded {len(chunks)} chunks for doc: {doc_id}")


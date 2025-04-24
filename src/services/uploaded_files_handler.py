import os
import chromadb
from datetime import datetime
from src.utils.config import CHUNK_SIZE
from src.services.embedding_handler import embed_text
from src.utils.text_chunking import chunk_text
from src.utils.utils import save_uploaded_file
from src.services.txt_pdf_handler import extract_document_text

def process_uploaded_docs(file_path: str, category: str, doc_title: str, uploaded_by: str):
    """
    Process uploaded PDF/TXT file with unified metadata structure:
    - Auto-generate doc_id using category + doc_title + timestamp
    - Embed with full metadata
    """
    from datetime import datetime
    import os

    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        return

    # Step 1: Extract text
    text, _ = extract_document_text(file_path)
    if not text:
        print("⚠️ No text extracted.")
        return

    # Step 2: Normalize + generate doc_id
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    timestamp_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    normalized_title = normalize_text(doc_title)
    doc_id = f"{category}_{normalized_title}_{timestamp_id}"

    # Step 3: Chunk
    chunks = chunk_text(text, chunk_size=CHUNK_SIZE)

    # Step 4: Embed with metadata
    for i, chunk in enumerate(chunks):
        chunk_id = f"{doc_id}_chunk_{i}"
        metadata = {
            "doc_id": doc_id,
            "doc_title": doc_title,
            "category": category,
            "chunk_index": i,
            "source_type": "uploaded_file",
            "user_id": uploaded_by,
            "timestamp": timestamp
        }
        embed_text(chunk, chunk_id, metadata)

    print(f"✅ Embedded {len(chunks)} chunks for doc: {doc_id}")



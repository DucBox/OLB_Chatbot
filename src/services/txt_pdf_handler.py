import os
from src.utils.config import SURYA_API_KEY
from src.utils.utils import extract_text_from_pdf, extract_text_from_txt

def extract_document_text(file_path: str) -> tuple[str, str]:
    """
    Extracts text from a file and returns (text, doc_id)

    Returns:
        str: Cleaned extracted text
        str: Document ID (based on filename)
    """
    if not os.path.exists(file_path):
        print("⚠️ File not found.")
        return "", ""

    ext = os.path.splitext(file_path)[-1].lower()

    if ext == ".pdf":
        text = extract_text_from_pdf(file_path, SURYA_API_KEY)
    elif ext == ".txt":
        text = extract_text_from_txt(file_path)
    else:
        print("⚠️ Unsupported file format. Only PDF and TXT are supported.")
        return "", ""

    doc_id = os.path.basename(file_path)
    return text.strip(), doc_id
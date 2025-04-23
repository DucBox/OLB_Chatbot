import os
import tiktoken  
import fitz
import xml.etree.ElementTree as ET
import streamlit as st
import time
import requests
import shutil
import re
import pandas as pd
from datetime import datetime
from pathlib import Path
from compdfkit.client import CPDFClient 
from compdfkit.enums import CPDFConversionEnum
from compdfkit.param import CPDFToTxtParameter
from compdfkit.constant import CPDFConstant
from src.utils.config import CHUNK_SIZE, BASE_DIR, FIREBASE_COLLECTION_NAME, TEMP_TXT_PATH, TEMP_PDF_PATH
from src.database.chromadb_connection import collection
from src.database.firebase_connection import db  
from src.database.cpdf_connection import client
from shapely.geometry import box as shapely_box
from PyPDF2 import PdfReader, PdfWriter
from langchain_text_splitters import RecursiveCharacterTextSplitter

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

def split_pdf_to_pages(pdf_path: str, output_dir: str) -> list[str]:
    reader = PdfReader(pdf_path)
    output_paths = []

    for i, page in enumerate(reader.pages):
        writer = PdfWriter()
        writer.add_page(page)

        out_path = os.path.join(output_dir, f"page_{i+1}.pdf")
        with open(out_path, "wb") as f:
            writer.write(f)
        output_paths.append(out_path)

    return output_paths

def bbox_overlap(b1, b2):
    box1 = shapely_box(b1[0], b1[1], b1[2], b1[3])
    box2 = shapely_box(b2[0], b2[1], b2[2], b2[3])
    return box1.intersection(box2).area / box2.area

def extract_text_by_layout_order(file_path: str, api_key: str):
    headers = {"X-Api-Key": api_key}
    
    output_dir = TEMP_PDF_PATH
    os.makedirs(output_dir, exist_ok=True)
    
    split_pages = split_pdf_to_pages(file_path, output_dir)
    total_pages = len(split_pages)

    print(f"📄 Total pages: {total_pages}")
    all_page_outputs = []

    for page_num, page_path in enumerate(split_pages, start=1):
        print(f"\n=== Processing page {page_num} ===")

        # Layout
        f_page = {"file": (os.path.basename(page_path), open(page_path, "rb"), "application/pdf")}
        layout_resp = requests.post("https://www.datalab.to/api/v1/layout", files=f_page, headers=headers)
        layout_check_url = layout_resp.json()["request_check_url"]

        for _ in range(300):
            time.sleep(1)
            layout_result = requests.get(layout_check_url, headers=headers).json()
            if layout_result["status"] == "complete":
                break
        else:
            raise TimeoutError(f"Layout polling page {page_num} timed out")

        # OCR
        f_ocr = {"file": (os.path.basename(page_path), open(page_path, "rb"), "application/pdf")}
        ocr_resp = requests.post("https://www.datalab.to/api/v1/ocr", files=f_ocr, headers=headers, data={"langs": "en,vi"})
        ocr_check_url = ocr_resp.json()["request_check_url"]

        for _ in range(300):
            time.sleep(1)
            ocr_result = requests.get(ocr_check_url, headers=headers).json()
            if ocr_result["status"] == "complete":
                break
        else:
            raise TimeoutError(f"OCR polling page {page_num} timed out")

        layout_page = layout_result["pages"][0]  # vì file PDF chỉ có 1 trang
        ocr_page = ocr_result["pages"][0]
        ocr_lines = ocr_page["text_lines"]

        layout_boxes = layout_page["bboxes"]
        for lbox in layout_boxes:
            lbox["text"] = ""
            lbox_bbox = lbox["bbox"]
            for line in ocr_lines:
                if bbox_overlap(lbox_bbox, line["bbox"]) > 0.5:
                    lbox["text"] += line["text"] + " "

        layout_boxes.sort(key=lambda x: x["position"])
        all_page_outputs.append((page_num, layout_boxes))
    # 🧹 Cleanup folder PDF 
    shutil.rmtree(output_dir)
    return all_page_outputs

def reconstruct_page(blocks: list[dict]) -> list[str]:
    output = []
    for box in blocks:
        label = box["label"]
        text = box.get("text", "").strip()
        if not text:
            continue
        if label == "SectionHeader":
            output.append(f"🔷 {text.upper()}")
        elif label == "Text":
            output.append(f"  👉↳ {text}")
        elif label == "ListItem":
            output.append(f"    👉• {text}")
    return output

def extract_text_from_pdf(file_path: str, api_key: str) -> str:
    pages = extract_text_by_layout_order(file_path, api_key)
    full_output = []
    for _, blocks in pages:
        full_output.extend(reconstruct_page(blocks))
    return "\n".join(full_output)
    
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
            text = file.read()
            return text
    except Exception as e:
        print(f"⚠️ Error reading TXT file: {str(e)}")
        return ""
    
def chunk_text(text: str, chunk_size: int = CHUNK_SIZE) -> list[str]:
    """
    Chia văn bản bằng RecursiveCharacterTextSplitter của LangChain,
    GIỮ nguyên định dạng dòng và cho phép chồng lấn giữa các chunk.

    Args:
        text (str): Văn bản gốc.
        chunk_size (int): Số lượng ký tự mỗi chunk.

    Returns:
        list[str]: Danh sách các đoạn text đã chia.
    """
    CHUNK_OVERLAP = 100
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=CHUNK_OVERLAP
    )
    chunks = splitter.split_text(text)

    for i, chunk in enumerate(chunks, 1):
        print(f"\n🧩 Chunk {i}:\n{'-'*40}\n{chunk}\n{'='*40}")

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
        
        online_docs = public_docs = db.collection(FIREBASE_COLLECTION_NAME) \
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
        
def clear_user_chat_history(xml_path: str, session_key: str = "chat_history") -> bool:
    """
    Xoá nội dung file XML và xoá session_state tương ứng.

    Returns:
        bool: True nếu xoá thành công, False nếu gặp lỗi.
    """
    try:
        with open(xml_path, "w") as f:
            f.write('<?xml version="1.0" encoding="utf-8"?><chat_history></chat_history>')

        if session_key in st.session_state:
            st.session_state[session_key] = []

        return True
    except Exception as e:
        st.error(f"❌ Failed to clear history: {e}")
        return False

def find_cell_coordinates(df, keyword: str):
    for r in range(df.shape[0]):
        for c in range(df.shape[1]):
            value = str(df.iat[r, c]).strip().lower()
            if keyword.lower() in value:
                print(f"🔍 Found '{keyword}' at row {r}, col {c} → '{value}'")
                return r, c
    print(f"❌ Không tìm thấy keyword: {keyword}")
    return None, None

def extract_google_sheet_id(url: str) -> str:
    """
    Extracts the spreadsheet ID from a Google Sheets URL.

    Args:
        url (str): The full Google Sheets URL.

    Returns:
        str: The extracted sheet ID.
    """
    match = re.search(r"/spreadsheets/d/([a-zA-Z0-9-_]+)", url)
    if match:
        return match.group(1)
    else:
        raise ValueError("❌ Invalid Google Sheets URL. Cannot extract spreadsheet ID.")
    
def extract_table_by_coords(df, start_marker="bảng 1", end_marker="hết bảng 1"):
    r1, c1 = find_cell_coordinates(df, start_marker)
    r2, c2 = find_cell_coordinates(df, end_marker)

    if r1 is None or r2 is None:
        print(f"⚠️ Không tìm thấy marker: {start_marker} hoặc {end_marker}")
        return None

    # Lấy vùng từ sau dòng r1 đến trước dòng r2
    table_df = df.iloc[r1 + 1 : r2, c1 : c2 + 1].copy()

    return table_df.dropna(how="all")

def group_rows_by_first_col_gap(df: pd.DataFrame) -> list[str]:
    """
    Gộp các dòng liên tiếp trong DataFrame dựa theo khoảng cách giữa các dòng có nội dung ở cột đầu tiên.
    Mỗi block sẽ được gộp thành 1 dòng văn bản, bỏ qua các ô trống hoặc NaN.
    Ký tự xuống dòng \n sẽ được thay bằng khoảng trắng.
    """
    print(f"📊 [DEBUG] Tổng số dòng nhận vào: {df.shape[0]}")
    print(df.head(3))
    
    lines = []
    i = 0
    n = df.shape[0]

    while i < n:
        print(f"🔄 Row {i}: {repr(str(df.iloc[i, 0]))}")
        
        first_cell = str(df.iloc[i, 0]).strip()
        if first_cell and first_cell.lower() != "nan":

            j = i + 1
            while j < n and not str(df.iloc[j, 0]).strip():
                j += 1

            gap = j - i
            block = df.iloc[i:i + gap]

            block_text = []
            for _, row in block.iterrows():
                cells = [
                    str(cell).replace("\n", " ").strip()
                    for cell in row
                    if pd.notna(cell) and str(cell).strip()
                ]
                if cells:
                    block_text.append(" --- ".join(cells))

            full_line = " | ".join(block_text)
            if full_line.strip():
                lines.append(full_line)


            i = i + gap
        else:
            i += 1

    return lines

def save_text_to_txt(lines: list[str], output_path: str):
    with open(output_path, "w", encoding="utf-8") as f:
        for line in lines:
            f.write(line + "\n")
    print(f"✅ Đã lưu kết quả vào: {output_path}")
   
def fetch_sheet_metadata(service, sheet_id):
    return service.spreadsheets().get(
        spreadsheetId=sheet_id,
        fields="sheets.properties,sheets.merges"
    ).execute()

def select_target_sheet(metadata, index=0):
    return metadata['sheets'][index]

def fetch_sheet_values(service, sheet_id, sheet_title):
    start_fetch = time.time()
    result = service.spreadsheets().values().get(
        spreadsheetId=sheet_id,
        range=sheet_title
    ).execute()
    print(f"✅ [Fetch values] Done in {time.time() - start_fetch:.2f}s")
    return result.get('values', [])

def convert_values_to_dataframe(values):
    return pd.DataFrame(values)

def process_and_save_all_tables(df, table_names, output_folder, save_debug=False):
    table_texts = []

    for table_idx, table_name in enumerate(table_names, start=1):
        start_token = table_name
        end_token = f"hết {table_name}"
        table_df = extract_table_by_coords(df, start_token, end_token)

        if table_df is not None:
            lines = group_rows_by_first_col_gap(table_df)
            table_text = "\n".join(lines)
            table_texts.append(table_text)

            if save_debug:
                output_path = os.path.join(output_folder, f"table_{table_idx}.txt")
                save_text_to_txt(lines, output_path)

            print(f"{table_name} ✅")
            print("-----------")
        else:
            print(f"⚠️ Bỏ qua {table_name} (không tìm thấy)")
            table_texts.append("") 

    return table_texts

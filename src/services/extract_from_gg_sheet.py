import pandas as pd
import time
import re
import os
import time
import streamlit as st
from datetime import datetime
from src.utils.config import TABLE_NAMES
from src.utils.gg_sheet_utils import extract_google_sheet_id, group_rows_by_first_col_gap, fetch_sheet_metadata, select_target_sheet, fetch_sheet_values, process_and_save_all_tables, describe_table_briefly
from src.utils.utils import extract_table_by_coords, save_text_to_txt, convert_values_to_dataframe, normalize_text
from src.utils.text_chunking import chunk_text
from src.database.gg_sheet_connection import get_sheets_service
from src.services.embedding_handler import generate_embedding, store_embedding_to_firebase, embed_text

service = get_sheets_service()

def read_google_sheet_from_url(sheet_url: str, index: int):
    """
    Orchestrator: Đọc dữ liệu từ Google Sheet, tách bảng, lưu file. Gọi các hàm xử lý con.
    """
    sheet_id = extract_google_sheet_id(sheet_url)
    metadata = fetch_sheet_metadata(service, sheet_id)
    total_sheets = len(metadata["sheets"])
    print(f"📊 Google Sheet thực tế có {total_sheets} sheet(s).")
    sheet = select_target_sheet(metadata, index)

    sheet_title = sheet['properties']['title']
    merges = sheet.get('merges', [])

    values = fetch_sheet_values(service, sheet_id, sheet_title)
    if not values:
        return []

    df = convert_values_to_dataframe(values)

    table_texts = process_and_save_all_tables(
                    df,
                    table_names=TABLE_NAMES,
                )

    return table_texts

def process_google_sheet_to_embedding(sheet_url: str, category: str, uploaded_by: str, max_sheets: int):
    """
    Đọc Google Sheet nhiều tab (sheet index), xử lý embedding từng bảng.
    Với mỗi bảng, sinh mô tả ngắn qua GPT, rồi chunk và embed lại (có context).
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    timestamp_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    chunk_global_index = 0

    service = get_sheets_service()
    sheet_id = extract_google_sheet_id(sheet_url)
    metadata = fetch_sheet_metadata(service, sheet_id)
    sheets = metadata["sheets"]
    total_sheets = len(sheets)
    print(f"📊 Google Sheet thực tế có {total_sheets} sheet(s).")

    for sheet_index in range(min(max_sheets, total_sheets)):
        sheet_title = sheets[sheet_index]["properties"]["title"]
        normalized_title = normalize_text(sheet_title)
        doc_id = f"{category}_{normalized_title}_{timestamp_id}"

        try:
            table_texts = read_google_sheet_from_url(sheet_url, sheet_index)

            for table_idx, table_text in enumerate(table_texts):
                if not table_text.strip():
                    print(f"⚠️ Sheet '{sheet_title}' - Table {table_idx} is empty. Skipped.")
                    continue

                print(f"🧠 Calling GPT to describe Sheet '{sheet_title}' - Table {table_idx}...")
                brief = describe_table_briefly(table_text)
                chunks = chunk_text(table_text)
                total_parts = len(chunks)

                for i, chunk in enumerate(chunks):
                    enhanced_chunk = f"{brief}\n(PART {i+1}/{total_parts})\n{chunk}"
                    print("---------------")
                    print(enhanced_chunk)
                    chunk_id = f"{doc_id}_chunk_{chunk_global_index}"

                    metadata_obj = {
                        "doc_id": doc_id,
                        "doc_title": sheet_title,
                        "category": category,
                        "chunk_index": chunk_global_index,
                        "source_type": "google_sheet",
                        "timestamp": timestamp,
                        "sheet_index": sheet_index,
                        "table_index": table_idx,
                        "user_id": uploaded_by
                    }

                    try:
                        embedding, returned_chunk_id = embed_text(enhanced_chunk, chunk_id, metadata_obj)
                        print(f"✅ {doc_id} - Table {table_idx} - Chunk {chunk_global_index} → {returned_chunk_id}")
                    except Exception as e:
                        print(f"❌ [ERROR] Embed failed: {doc_id} - Table {table_idx} - Chunk {chunk_global_index}: {e}")

                    chunk_global_index += 1

        except Exception as e:
            print(f"❌ [ERROR] Sheet index {sheet_index} ('{sheet_title}') skipped: {e}")

@st.dialog("📘 Hướng dẫn định dạng Sheet và upload")
def show_tutorial():
    st.markdown("### 🧩 Bước 1: Đánh dấu điểm đầu tiên của bảng trong nội dung")
    st.image("frontend/assets/Step_1.png", caption="Bắt đầu mỗi bảng bằng dòng **'Bảng X'** để đảm bảo phân đoạn chính xác. Ô - Cell đánh dấu bằng 'Bảng X' sẽ là ô phía trên của ô đầu tiên của bảng, lưu ý ô đánh dấu chỉ là ô đơn, không được phép là merged cell. Mỗi sheet có thể đánh dấu nhiều bảng, qua sheet khác thì đánh lại từ Bảng 1.")

    st.markdown("### ✨ Bước 2: Đánh dấu điểm kết thúc cuối cùng của bảng trong nội dung")
    st.image("frontend/assets/Step_2.png", caption="Kết thúc mỗi bảng bằng dòng chữ **'Hết bảng X'** để hệ thống nhận dạng đúng ranh giới. Ô đánh dấu bằng 'Hết bảng X' sẽ là ô ngay dưới ô cuối cùng của bảng, lưu ý ô đánh dấu chỉ là ô đơn, không được phép là merged cell")

    st.markdown("### 🧱 Bước 3: Lấy link Google Sheet")
    st.image("frontend/assets/Step_3.png", caption="Copy đường dẫn từ trình duyệt và đảm bảo đã share quyền truy cập cho account 'quangducngo0811@gmail.com'. Đây chính là URL Sheet. Tiếp đến max_sheet chính là số trang sheet tối đa trong 1 link google sheet đang có, tính từ sheet đầu tiên là số 1 (Có thể nhập nhỏ hơn số lượng sheet thực tế có, nó sẽ chỉ lấy các sheet từ 1 đến số max_sheets mà user nhập)")


# process_google_sheet_to_embedding('https://docs.google.com/spreadsheets/d/1x8vgWHd38bnxYeaRBg-3i1ONMvDJ2Oq2fmhPHLLB9KA/edit?gid=1932410194#gid=1932410194', 'EM_Bắc_Kan', 'Duc', 3)
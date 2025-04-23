import pandas as pd
import time
import re
import os
import time
from datetime import datetime
from src.utils.config import TABLE_NAMES
from src.utils.utils import extract_google_sheet_id, extract_table_by_coords, group_rows_by_first_col_gap, save_text_to_txt, fetch_sheet_metadata, select_target_sheet, fetch_sheet_values, convert_values_to_dataframe, process_and_save_all_tables, chunk_text
from src.database.gg_sheet_connection import get_sheets_service
from src.services.embedding import generate_embedding, store_embedding_to_firebase, embed_text

def read_google_sheet_from_url(sheet_url: str, index: int):
    """
    Orchestrator: Đọc dữ liệu từ Google Sheet, tách bảng, lưu file. Gọi các hàm xử lý con.
    """
    import time

    start_total = time.time()
    sheet_id = extract_google_sheet_id(sheet_url)
    service = get_sheets_service()

    print("Start lấy metadata")
    metadata = fetch_sheet_metadata(service, sheet_id)
    sheet = select_target_sheet(metadata, index)
    sheet_title = sheet['properties']['title']
    merges = sheet.get('merges', [])
    print(f"✅ [Metadata] Done in {time.time() - start_total:.2f}s")

    values = fetch_sheet_values(service, sheet_id, sheet_title)
    if not values:
        print("⚠️ Sheet trống.")
        return []

    df = convert_values_to_dataframe(values)

    output_folder = "/Users/ngoquangduc/Desktop/AI_Project/chatbot_rag/data_test"
    
    table_texts = process_and_save_all_tables(
                    df,
                    table_names=TABLE_NAMES,
                    output_folder=output_folder,
                    save_debug=True 
                )

    return table_texts

def process_google_sheet_to_embedding(sheet_url: str, doc_id: str, position: str, uploaded_by: str, index: int):
    """
    Full pipeline:
    1. Đọc Google Sheet
    2. Tách các bảng thành text
    3. Chia nhỏ văn bản nếu dài
    4. Embed từng chunk và lưu
    """
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")

    table_texts = read_google_sheet_from_url(sheet_url, index)

    chunk_global_index = 0 

    for table_idx, table_text in enumerate(table_texts):
        if not table_text.strip():
            print(f"⚠️ Table {table_idx} is empty, skip.")
            continue

        chunks = chunk_text(table_text)

        for j, chunk in enumerate(chunks):
            chunk_id = f"{doc_id}_chunk_{chunk_global_index}"
            metadata = {
                "doc_id": doc_id,
                "chunk_index": chunk_global_index,
                "source_type": "google_sheet",
                "uploaded_by": uploaded_by,
                "position": position,
                "timestamp": timestamp
            }

            try:
                embedding, returned_chunk_id = embed_text(chunk, chunk_id, metadata)
                print(f"✅ Embedded table {table_idx} → Chunk {j} → Chunk ID: {returned_chunk_id}")
            except Exception as e:
                print(f"❌ [ERROR] Table {table_idx} / Chunk {j} failed → {e}")

            chunk_global_index += 1

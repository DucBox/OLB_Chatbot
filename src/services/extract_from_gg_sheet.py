import pandas as pd
import time
import re
import os
import time
from datetime import datetime
from src.utils.config import TABLE_NAMES
from src.utils.gg_sheet_utils import extract_google_sheet_id, group_rows_by_first_col_gap, fetch_sheet_metadata, select_target_sheet, fetch_sheet_values, process_and_save_all_tables
from src.utils.utils import extract_table_by_coords, save_text_to_txt, convert_values_to_dataframe
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
            except Exception as e:
                print(f"❌ [ERROR] Table {table_idx} / Chunk {j} failed → {e}")

            chunk_global_index += 1

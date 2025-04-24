import os
import pandas as pd
import numpy as np
import re
from src.utils.utils import extract_table_by_coords 

def process_and_save_all_tables(df, table_names):
    table_texts = []

    for table_idx, table_name in enumerate(table_names, start=1):
        start_token = table_name
        end_token = f"hết {table_name}"
        table_df = extract_table_by_coords(df, start_token, end_token)

        if table_df is not None:
            lines = group_rows_by_first_col_gap(table_df)
            table_text = "\n".join(lines)
            table_texts.append(table_text)

        else:
            print(f"⚠️ Bỏ qua {table_name} (không tìm thấy)")
            table_texts.append("") 

    return table_texts

def select_target_sheet(metadata, index=0):
    return metadata['sheets'][index]

def fetch_sheet_values(service, sheet_id, sheet_title):
    result = service.spreadsheets().values().get(
        spreadsheetId=sheet_id,
        range=sheet_title
    ).execute()
    return result.get('values', [])

def fetch_sheet_metadata(service, sheet_id):
    return service.spreadsheets().get(
        spreadsheetId=sheet_id,
        fields="sheets.properties,sheets.merges"
    ).execute()

def group_rows_by_first_col_gap(df: pd.DataFrame) -> list[str]:
    """
    Gộp các dòng liên tiếp trong DataFrame dựa theo khoảng cách giữa các dòng có nội dung ở cột đầu tiên.
    Mỗi block sẽ được gộp thành 1 dòng văn bản, bỏ qua các ô trống hoặc NaN.
    Ký tự xuống dòng \n sẽ được thay bằng khoảng trắng.
    """
    lines = []
    i = 0
    n = df.shape[0]

    while i < n:
        
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
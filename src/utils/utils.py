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
 
from src.database.cpdf_connection import client
from langchain_text_splitters import RecursiveCharacterTextSplitter
from src.utils.pdf_utils import extract_text_by_layout_order, reconstruct_page

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
    
def extract_table_by_coords(df, start_marker="bảng 1", end_marker="hết bảng 1"):
    r1, c1 = find_cell_coordinates(df, start_marker)
    r2, c2 = find_cell_coordinates(df, end_marker)

    if r1 is None or r2 is None:
        return None

    # Lấy vùng từ sau dòng r1 đến trước dòng r2
    table_df = df.iloc[r1 + 1 : r2, c1 : c2 + 1].copy()

    return table_df.dropna(how="all")

def save_text_to_txt(lines: list[str], output_path: str):
    with open(output_path, "w", encoding="utf-8") as f:
        for line in lines:
            f.write(line + "\n")
    print(f"✅ Đã lưu kết quả vào: {output_path}")
   
def select_target_sheet(metadata, index=0):
    return metadata['sheets'][index]

def convert_values_to_dataframe(values):
    return pd.DataFrame(values)

def find_cell_coordinates(df, keyword: str):
    for r in range(df.shape[0]):
        for c in range(df.shape[1]):
            value = str(df.iat[r, c]).strip().lower()
            if keyword.lower() in value:
                print(f"🔍 Found '{keyword}' at row {r}, col {c} → '{value}'")
                return r, c
    return None, None
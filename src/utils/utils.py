import os
import tiktoken  
import fitz
import xml.etree.ElementTree as ET
import streamlit as st
import time
import requests
import shutil
import re
import unicodedata
import pandas as pd
from datetime import datetime
from pathlib import Path
from src.utils.config import CHUNK_SIZE, BASE_DIR, FIREBASE_COLLECTION_NAME, TEMP_TXT_PATH, TEMP_PDF_PATH
from src.database.chromadb_connection import collection
 
from src.database.cpdf_connection import client
from langchain_text_splitters import RecursiveCharacterTextSplitter
from src.utils.pdf_utils import extract_text_by_layout_order, reconstruct_page

from openai import OpenAI
from src.utils.config import OPENAI_API_KEY

client = OpenAI(api_key=OPENAI_API_KEY)

def call_gpt(system_prompt: str, user_prompt: str, model: str = "gpt-4o-mini") -> str:
    """
    Call GPT Model API

    Args:
        prompt (str): Detail prompt sent to model
        model (str): Model type

    Returns:
        str: Response from GPT
    """
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.0 
        )
        bot_response = response.choices[0].message.content.strip()
        return bot_response
    except Exception as e:
        print(f"❌ GPT API error: {e}")
        return "[ERROR] GPT failed to generate response."

def extract_text_from_pdf(file_path: str, api_key: str) -> str:
    """
    Extracts text from a PDF file
    Args:
        file_path (str): PDF File path
        api_key (str): Surya API Tool
    Return:
        str: The extracted text
    """
    pages = extract_text_by_layout_order(file_path, api_key)
    full_output = []
    for _, blocks in pages:
        full_output.extend(reconstruct_page(blocks))
    return "\n".join(full_output)
    
def extract_text_from_txt(txt_path):
    """
    Extracts text from a TXT file
    Args:
        txt_path (str): The path to the TXT file
    Returns:
        str: The extracted text
    """
    try:
        with open(txt_path, "r", encoding="utf-8") as file:
            text = file.read()
            return text
    except Exception as e:
        print(f"⚠️ Error reading TXT file: {str(e)}")
        return ""

def extract_table_by_coords(df, start_marker="bảng 1", end_marker="hết bảng 1"):
    """
    Extract sub table from a df
    Args:
        df(pd.DataFrame): Data Frame
        start_marker (str, optional): Start Cell
        end_marker (str, optional): End Cell
    Returns:
        A new sub table from a df
    """
    r1, c1 = find_cell_coordinates(df, start_marker)
    r2, c2 = find_cell_coordinates(df, end_marker)

    if r1 is None or r2 is None:
        return None

    table_df = df.iloc[r1 + 1 : r2, c1 : c2 + 1].copy()

    return table_df.dropna(how="all")

def save_text_to_txt(lines: list[str], output_path: str):
    with open(output_path, "w", encoding="utf-8") as f:
        for line in lines:
            f.write(line + "\n")
    print(f"✅ Đã lưu kết quả vào: {output_path}")

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

def normalize_text(text: str) -> str:
    text = unicodedata.normalize("NFKD", text)
    text = text.encode("ascii", "ignore").decode("ascii")
    text = re.sub(r"[^\w]+", "_", text)
    return text.strip("_")

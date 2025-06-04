import json
import os
from dotenv import load_dotenv
from google.oauth2 import service_account
from googleapiclient.discovery import build

# Load biến môi trường
load_dotenv()

SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]

def get_sheets_service():
    """Xác thực và trả về dịch vụ Google Sheets API bằng Service Account."""
    gg_credentials = os.getenv("GOOGLE_CREDENTIALS")
    if not gg_credentials:
        raise ValueError("GOOGLE_CREDENTIALS environment variable not found.")

    # FIX: nếu chưa escape \\n, thì tự escape
    if "\\n" not in gg_credentials:
        gg_credentials = gg_credentials.replace("\n", "\\n")

    try:
        creds_dict = json.loads(gg_credentials)
    except json.JSONDecodeError as e:
        raise ValueError(f"Lỗi khi decode GOOGLE_CREDENTIALS: {e}")

    # Tạo credentials trực tiếp từ dict, không cần ghi ra file
    creds = service_account.Credentials.from_service_account_info(
        creds_dict,
        scopes=SCOPES,
    )

    return build("sheets", "v4", credentials=creds)

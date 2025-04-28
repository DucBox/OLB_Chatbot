import os
import json
from google.oauth2 import service_account
from googleapiclient.discovery import build
from dotenv import load_dotenv

# Load biến môi trường
load_dotenv()

SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

def get_sheets_service():
    """Xác thực và trả về dịch vụ Google Sheets API bằng Service Account."""
    
    # Lấy GOOGLE_CREDENTIALS từ biến môi trường (chứa JSON service account)
    gg_credentials = os.getenv("GOOGLE_CREDENTIALS")
    if not gg_credentials:
        raise ValueError("GOOGLE_CREDENTIALS environment variable not found.")

    # Ghi ra file tạm /tmp/gg_credentials.json
    creds_data = json.loads(gg_credentials)
    service_account_path = "/tmp/gg_credentials.json"
    with open(service_account_path, "w") as f:
        json.dump(creds_data, f)

    # Authenticate bằng Service Account
    creds = service_account.Credentials.from_service_account_file(
        service_account_path,
        scopes=SCOPES,
    )

    service = build('sheets', 'v4', credentials=creds)
    return service

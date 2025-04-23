import os
import re
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import pandas as pd
import json
from dotenv import load_dotenv

SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

def get_sheets_service():
    """Xác thực và trả về dịch vụ Google Sheets API."""
    creds = None
    gg_credentials = os.getenv("GOOGLE_CREDENTIALS")
    if gg_credentials:
        gg_cre = json.loads(gg_credentials)
        with open("/tmp/gg_credentials.json", "w") as f:
            json.dump(gg_cre, f)
        
    gg_sheet_token = os.getenv("GOOGLE_SHEET_TOKEN")
    if gg_sheet_token:
        gg_sheet = json.loads(gg_sheet_token)
        with open("/tmp/gg_sheet_token.json", "w") as f:
            json.dump(gg_sheet, f)
            
    creds_path = '/tmp/gg_credentials.json'
    token_path = '/tmp/gg_sheet_token.json'

    # Đọc token nếu đã tồn tại
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)

    # Nếu chưa có token hoặc token hết hạn
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(creds_path, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(token_path, 'w') as token:
            token.write(creds.to_json())

    service = build('sheets', 'v4', credentials=creds)
    return service
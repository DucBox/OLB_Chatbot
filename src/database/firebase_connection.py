import os
import json
import firebase_admin
from firebase_admin import credentials, firestore
from dotenv import load_dotenv

# load_dotenv()

# FIREBASE_KEY_PATH = os.getenv("FIREBASE_KEY_JSON_PATH", "src/utils/firebase_key.json")

# # Chỉ khởi tạo nếu chưa có app
# if not firebase_admin._apps:
#     cred = credentials.Certificate(FIREBASE_KEY_PATH)
#     firebase_admin.initialize_app(cred)

# # Kết nối đến Firestore
# db = firestore.client()

firebase_json_str = os.getenv("FIREBASE_KEY_JSON")

if firebase_json_str:
    key_data = json.loads(firebase_json_str)
    with open("/tmp/firebase_key.json", "w") as f:
        json.dump(key_data, f)

    cred = credentials.Certificate("/tmp/firebase_key.json")
    firebase_admin.initialize_app(cred)
    db = firestore.client()
else:
    raise RuntimeError("❌ FIREBASE_KEY_JSON environment variable not found.")

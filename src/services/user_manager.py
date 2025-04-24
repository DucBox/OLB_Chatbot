
from src.database.firebase_connection import db

def get_user_by_id(user_id: str):
    try:
        user_ref = db.collection("users").document(user_id)
        user_doc = user_ref.get()
        if user_doc.exists:
            return user_doc.to_dict()
        return None
    except Exception as e:
        print(f"❌ Error fetching user: {e}")
        return None
    
def create_user(user_id: str, password: str, role: str == "user"):
    try:
        db.collection("users").document(user_id).set({
            "user_id": user_id,
            "password": password,
            "role": role
        })
        print(f"✅ Created user: {user_id} with role '{role}'")
    except Exception as e:
        print(f"❌ Error creating user {user_id}: {e}")

def check_user_credentials(user_id: str, password: str) -> bool:
    user = get_user_by_id(user_id)
    if user and user.get("password") == password:
        return True
    return False

def get_user_role(user_id: str) -> str:
    user = get_user_by_id(user_id)
    return user.get("role", "user") if user else "user"


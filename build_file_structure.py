import os

SRC_DIR = "/Users/ngoquangduc/Desktop/AI_Project/chatbot_rag/src"

def create_init_files(base_dir):
    for root, dirs, files in os.walk(base_dir):
        init_path = os.path.join(root, "__init__.py")
        if not os.path.exists(init_path):
            with open(init_path, "w") as f:
                f.write("")  # Bạn có thể ghi default export ở đây nếu cần
            print(f"✅ Created: {init_path}")
        else:
            print(f"✔️ Already exists: {init_path}")

create_init_files(SRC_DIR)

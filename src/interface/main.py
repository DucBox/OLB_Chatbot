# src/interface/main.py

import sys
import os
from pathlib import Path
from src.core.chat import chat_with_gpt
from src.storage.history import load_history_from_xml, save_history_to_xml
from src.services.files import process_uploaded_docs
from src.utils.utils import delete_document_chromadb, list_all_doc_ids_chromadb
from src.utils.utils import delete_document_firebase, list_all_doc_ids_firebase

def upload_mode():
    print("\n📤 Upload Document Mode")

    # Step 1: Get file path
    file_path = input("📁 Enter file path to upload (PDF/TXT): ").strip()
    if not os.path.exists(file_path):
        print("❌ File not found.")
        return

    # Step 2: Get additional info
    doc_id = input("🆔 Enter a unique document ID: ").strip()
    uploaded_by = input("👤 Enter your name: ").strip()
    position = input("💼 Enter your position (e.g., HR Manager): ").strip()

    # Step 3: Process and embed
    process_uploaded_docs(
        file_path=file_path,
        doc_id=doc_id,
        uploaded_by=uploaded_by,
        position=position
    )

    print(f"✅ Document '{doc_id}' processed successfully.")


def chat_mode():
    print("\n💬 Chat Mode (type 'exit' to return)")
    history = load_history_from_xml()
    while True:
        user_input = input("\n🧑 You: ").strip()
        if user_input.lower() == "exit":
            print("🔙 Exiting chat...")
            break
        response, history = chat_with_gpt(user_input, history)
        save_history_to_xml(history)
        print(f"\n🤖 Bot: {response}")

def main():
    print("\n🤖 OLB Assistant — Terminal Mode")
    while True:
        print("\n1: Chat with Bot")
        print("2: Upload Document (PDF/TXT)")
        print("3: Delete Document")
        print("0: Exit")
        choice = input("Choose an option: ").strip()
        if choice == "1":
            chat_mode()
        elif choice == "2":
            upload_mode()
        elif choice == "3":
            available_doc_ids = list_all_doc_ids_firebase()
            print("🗂 Available documents:")
            for doc in available_doc_ids:
                print("  -", doc)

            doc_id = input("\nChoose a document to delete: ")
            delete_document_firebase(doc_id)
        elif choice == "0":
            print("👋 Goodbye!")
            break
        else:
            print("⚠️ Invalid choice. Please try again.")

if __name__ == "__main__":
    main()

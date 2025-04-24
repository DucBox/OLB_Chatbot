# ================== PYTHONPATH CONFIG ==================
import os
import sys
import streamlit as st
import time
from pathlib import Path
from datetime import datetime
from collections import defaultdict

# ========== Imports ==========
from src.core.chat import chat_with_gpt
from src.utils.xml_utils import load_history_from_xml, save_history_to_xml
from src.utils.config import LOG_FILE_XML, HISTORY_STORE_PATH
from src.services.uploaded_files_handler import process_uploaded_docs
from src.services.doc_storage_manager import list_all_docs_metadata_firebase, delete_by_doc_id, delete_by_category, delete_by_doc_title
from src.services.chat_history_handler import render_user_chat_history
from src.services.extract_from_gg_sheet import process_google_sheet_to_embedding
from src.services.user_manager import (
    get_user_by_id,
    create_user,
    check_user_credentials,
    get_user_role
)

# ========== UI Setup ==========
st.set_page_config(page_title="EM Assistant", page_icon="🤖", layout="wide")
st.title("🤖 EM AI Bot Assistant")
# ========== Session info ==========
user_id = st.session_state.get("user_id")
user_role = st.session_state.get("user_role")

# ========== Nếu chưa login, hiện panel đăng nhập/đăng ký ==========
if not user_id or not user_role:
    with st.sidebar.expander("🔐 Admin / Core Login/Register", expanded=True):
        action = st.radio("Select action", ["Login", "Register"], horizontal=True)

        user_input = st.text_input("👤 ID")
        password_input = st.text_input("🔑 Password", type="password")

        if st.button("🚀 Proceed"):
            if not user_input or not password_input:
                st.warning("⚠️ Please fill in both fields.")
                st.stop()

            user_data = get_user_by_id(user_input)

            if action == "Register":
                if user_data:
                    st.error("❌ User ID already exists. Try logging in.")
                else:
                    create_user(user_input, password_input, role="user")
                    st.session_state.user_id = user_input
                    st.session_state.user_role = "user"
                    st.success(f"👋 Welcome, {user_input}! Your account has been created.")
                    st.rerun()

            elif action == "Login":
                if not user_data:
                    st.error("❌ User ID not found. Please register first.")
                elif not check_user_credentials(user_input, password_input):
                    st.error("❌ Incorrect password.")
                else:
                    st.session_state.user_id = user_input
                    st.session_state.user_role = get_user_role(user_input)
                    st.success(f"✅ Welcome back, {user_input}!")
                    st.rerun()

# ========== Đã login: show thông tin ==========
else:
    st.sidebar.success(f"👋 Welcome, {user_id} ({user_role})")
    
if not user_id or not user_role:
    st.stop()
    
if st.sidebar.button("🚪 Logout"):
    st.session_state.clear()
    st.rerun()

USER_HISTORY_CHAT_FILE = HISTORY_STORE_PATH / f"chat_history_{user_id}.xml"

# ===== Tạo file XML rỗng nếu chưa có =====
if not os.path.exists(USER_HISTORY_CHAT_FILE):
    os.makedirs(os.path.dirname(USER_HISTORY_CHAT_FILE), exist_ok=True)
    print(f"Created new history chat for {user_id} at {USER_HISTORY_CHAT_FILE}")
    with open(USER_HISTORY_CHAT_FILE, "w") as f:
        f.write('<?xml version="1.0" encoding="utf-8"?><chat_history></chat_history>')

# ========== Sidebar: Document Management ==========
if user_role in ["admin", "core"]:
    st.sidebar.markdown("### 🗂 Document Manager")

    try:
        all_docs = list_all_docs_metadata_firebase(user_id)
        print("Available categories:")
        for doc in all_docs:
            print("→", doc.get("category"))

        grouped_docs = defaultdict(lambda: defaultdict(list))

        for doc in all_docs:
            category = doc.get("category", "Uncategorized")
            doc_title = doc.get("doc_title", "Untitled")
            grouped_docs[category][doc_title].append(doc["doc_id"])

        if not grouped_docs:
            st.sidebar.info("No documents found.")
        else:
            for category, docs_in_cat in grouped_docs.items():
                with st.sidebar.expander(f"📁 {category}", expanded=False):
                    # Nút xoá toàn bộ category
                    if st.button(f"🗑️ Delete All in '{category}'", key=f"delete_cat_{category}"):
                        delete_by_category(category)
                        st.success(f"🗑️ Deleted all in category: {category}")
                        st.rerun()

                    doc_titles = list(docs_in_cat.keys())
                    if doc_titles:
                        selected_doc_title = st.selectbox(
                            f"📄 Select document in {category}",
                            options=doc_titles,
                            key=f"select_doc_{category}"
                        )

                        if selected_doc_title:
                            if st.button(f"❌ Delete '{selected_doc_title}'", key=f"delete_{category}_{selected_doc_title}"):
                                delete_by_doc_title(category, selected_doc_title)
                                st.success(f"🗑️ Deleted: {category} / {selected_doc_title}")
                                st.rerun()
    except Exception as e:
        st.sidebar.error(f"⚠️ Failed to load documents: {e}")

# ========== Sidebar: System Logs ==========
st.sidebar.markdown("---")  # Separator
st.sidebar.markdown("### 📂 System Logs")

with st.sidebar.expander("📜 View Your Chat History", expanded=False):
    render_user_chat_history(USER_HISTORY_CHAT_FILE, user_id)

# ========== CSS ==========
st.markdown("""
    <style>
    .chat-container { margin-bottom: 1.2rem; }
    .user { text-align: right; }
    .bot { text-align: left; }
    .chat-bubble {
        display: inline-block;
        padding: 10px 14px;
        border-radius: 12px;
        max-width: 70%;
        word-wrap: break-word;
        background-color: #f1f1f1;
        color: black;
    }
    </style>
""", unsafe_allow_html=True)

# ========== Load Chat History ==========
if "chat_history" not in st.session_state:
    st.session_state.chat_history = load_history_from_xml(path = USER_HISTORY_CHAT_FILE)

# ========== Display Chat ==========
for user_msg, bot_msg in st.session_state.chat_history:
    st.markdown(f'<div class="chat-container user"><div class="chat-bubble">{user_msg}</div></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="chat-container bot"><div class="chat-bubble">{bot_msg}</div></div>', unsafe_allow_html=True)

# ========== Chat Input ==========
user_input = st.chat_input("Ask me anything...")

if user_input:
    st.markdown(f'<div class="chat-container user"><div class="chat-bubble">{user_input}</div></div>', unsafe_allow_html=True)
    bot_placeholder = st.empty()
    bot_placeholder.markdown('<div class="chat-container bot"><div class="chat-bubble">🤖 Thinking...</div></div>', unsafe_allow_html=True)

    response, updated_history = chat_with_gpt(user_input, st.session_state.chat_history, user_id)
    bot_placeholder.markdown(f'<div class="chat-container bot"><div class="chat-bubble">{response}</div></div>', unsafe_allow_html=True)

    st.session_state.chat_history = updated_history
    save_history_to_xml(updated_history, path = USER_HISTORY_CHAT_FILE)

    st.rerun()

if user_role in ["admin", "core"]:
    with st.expander("📤 Upload Document", expanded=False):  
        col1, col2, col3, col4 = st.columns([5, 2, 2, 2])

        with col1:
            uploaded_file = st.file_uploader("📂 File", type=["pdf", "txt"], label_visibility="collapsed")

        with col2:
            category = st.text_input("🏷️ Category")

        with col3:
            doc_title = st.text_input("📄 Document Title")

        with col4:
            uploaded_by = st.text_input("👤 Uploaded by")

        st.markdown("<div style='height: 10px'></div>", unsafe_allow_html=True)
        if st.button("📤 Upload"):
            if uploaded_file and category and doc_title and uploaded_by:
                temp_path = os.path.join("temp", uploaded_file.name)
                os.makedirs("temp", exist_ok=True)
                with open(temp_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())

                process_uploaded_docs(
                    file_path=temp_path,
                    category=category,
                    doc_title=doc_title,
                    uploaded_by=uploaded_by,
                )
                st.rerun()
            else:
                st.warning("⚠️ Please fill all fields.")

if user_role in ["admin", "core"]:
    with st.expander("🌐 Use Google Sheet Link", expanded=False):
        col1, col2, col3, col4 = st.columns([4, 1, 2, 2])

        with col1:
            sheet_url = st.text_input("🔗 Google Sheet URL")

        with col2:
            max_sheets = st.number_input("📄 Max Sheets", min_value=1, value=5, step=1)

        with col3:
            category = st.text_input("🏷️ Category (e.g., EM_Project)")

        with col4:
            uploaded_by = st.text_input("👤 Name")

        st.markdown("<div style='height: 10px'></div>", unsafe_allow_html=True)
        if st.button("🚀 Process Sheet"):
            if sheet_url and category and uploaded_by:
                process_google_sheet_to_embedding(
                    sheet_url=sheet_url,
                    category=category,
                    uploaded_by=uploaded_by,
                    max_sheets=int(max_sheets)
                )
                st.rerun()
            else:
                st.warning("⚠️ Please fill in all fields.")



# ================== PYTHONPATH CONFIG ==================
import os
import sys
from pathlib import Path
from datetime import datetime
import streamlit as st
import time

# ========== Imports ==========
from src.core.chat import chat_with_gpt
from src.storage.history import load_history_from_xml, save_history_to_xml
from src.services.files import process_uploaded_docs
from src.utils.utils import delete_document_chromadb, list_all_doc_ids_chromadb
from src.utils.utils import delete_document_firebase, list_all_doc_ids_firebase
from src.utils.config import LOG_FILE_XML, HISTORY_STORE_PATH
from src.services.chat_history_handler import render_user_chat_history

# ========== UI Setup ==========
st.set_page_config(page_title="OLB Assistant", page_icon="🤖", layout="wide")
st.title("🤖 OLB AI Bot Assistant")
user_input = st.sidebar.text_input("👤 Enter your name or ID:", key="user_id_input")

if "user_id" not in st.session_state and user_input:
    st.session_state.user_id = user_input
    st.rerun()

if "user_id" not in st.session_state:
    st.stop()

user_id = st.session_state.user_id
USER_HISTORY_CHAT_FILE = HISTORY_STORE_PATH / f"chat_history_{user_id}.xml"

# ===== Tạo file XML rỗng nếu chưa có =====
if not os.path.exists(USER_HISTORY_CHAT_FILE):
    os.makedirs(os.path.dirname(USER_HISTORY_CHAT_FILE), exist_ok=True)
    print(f"Created new history chat for {user_id} at {USER_HISTORY_CHAT_FILE}")
    with open(USER_HISTORY_CHAT_FILE, "w") as f:
        f.write('<?xml version="1.0" encoding="utf-8"?><chat_history></chat_history>')

# ========== Sidebar: Document Management ==========
st.sidebar.markdown("### 🗂 Document Manager")

try:
    doc_ids = list_all_doc_ids_firebase(user_id)
    if not doc_ids:
        st.sidebar.info("No documents found.")
    else:
        for doc_id in doc_ids:
            with st.sidebar.expander(f"📄 {doc_id}", expanded=False):
                if st.button(f"❌ Delete '{doc_id}'", key=f"delete_{doc_id}"):
                    delete_document_firebase(doc_id)
                    st.success(f"🗑️ Deleted document: {doc_id}")
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

with st.expander("📤 Upload Document", expanded=False):  # ✅ collapsed by default
    col1, col2, col3, col4, col5 = st.columns([5, 2, 2, 2, 1])

    with col1:
        uploaded_file = st.file_uploader("📂 File", type=["pdf", "txt"], label_visibility="collapsed")

    with col2:
        doc_id = st.text_input("🆔 Doc ID")

    with col3:
        uploaded_by = st.text_input("👤 Name")

    with col4:
        position = st.text_input("💼 Position")

    with col5:
        st.markdown("<div style='height: 28px'></div>", unsafe_allow_html=True)
        centered = st.columns([1, 1, 1])
        with centered[1]:
            if st.button("📤"):
                if uploaded_file and doc_id and uploaded_by and position:
                    temp_path = os.path.join("temp", uploaded_file.name)
                    os.makedirs("temp", exist_ok=True)
                    with open(temp_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())

                    process_uploaded_docs(
                        file_path=temp_path,
                        doc_id=doc_id,
                        uploaded_by=uploaded_by,
                        position=position
                    )
                    st.rerun()
                else:
                    st.warning("⚠️ Please fill all fields.")

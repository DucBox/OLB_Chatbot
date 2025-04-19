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
from src.utils.config import LOG_FILE_XML

# ========== UI Setup ==========
st.set_page_config(page_title="OLB Assistant", page_icon="🤖", layout="wide")
st.title("🤖 OLB AI Bot Assistant")

# ========== Sidebar: Document Management ==========
st.sidebar.markdown("### 🗂 Document Manager")

try:
    doc_ids = list_all_doc_ids_firebase()
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

if os.path.exists(LOG_FILE_XML):
    with st.sidebar.expander("📜 View history_chat.xml", expanded=False):
        with open(LOG_FILE_XML, "r") as f:
            history_content = f.read()
        st.code(history_content, language="xml")
        
        # Hiển thị thời gian cập nhật
        last_modified = os.path.getmtime(LOG_FILE_XML)
        st.caption(f"🕓 Last updated: {time.ctime(last_modified)}")

        # Nút clear nội dung
        if st.button("🧹 Clear History Content", key="clear_history"):
            try:
                with open(LOG_FILE_XML, "w") as f:
                    f.write("")  # chỉ xoá nội dung
                st.success("✅ History content cleared.")
                st.rerun()
            except Exception as e:
                st.error(f"❌ Failed to clear content: {e}")
else:
    st.sidebar.info("🕵️ No history_chat.xml found.")



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
    st.session_state.chat_history = load_history_from_xml()

# ========== Display Chat ==========
for user_msg, bot_msg in st.session_state.chat_history:
    st.markdown(f'<div class="chat-container user"><div class="chat-bubble">{user_msg}</div></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="chat-container bot"><div class="chat-bubble">{bot_msg}</div></div>', unsafe_allow_html=True)

# ========== Chat Input ==========
user_input = st.chat_input("Ask me anything...")

if user_input:
    # Hiển thị user message ngay
    st.markdown(f'<div class="chat-container user"><div class="chat-bubble">{user_input}</div></div>', unsafe_allow_html=True)

    # Tạo khung tạm thời hiển thị bot đang suy nghĩ
    bot_placeholder = st.empty()
    bot_placeholder.markdown('<div class="chat-container bot"><div class="chat-bubble">🤖 Thinking...</div></div>', unsafe_allow_html=True)

    # Gọi GPT và lấy response
    response, updated_history = chat_with_gpt(user_input, st.session_state.chat_history)

    # Ghi đè Thinking... bằng bot response thật
    bot_placeholder.markdown(f'<div class="chat-container bot"><div class="chat-bubble">{response}</div></div>', unsafe_allow_html=True)

    # Cập nhật history và lưu file
    st.session_state.chat_history = updated_history
    save_history_to_xml(updated_history)

    st.rerun()

# ========== Upload Section: Inline Form ==========
st.markdown("---")
st.subheader("📤 Upload a Document")

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
    with centered[1]:  # center column
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

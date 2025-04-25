import streamlit as st
import os
import time
from datetime import datetime
from uuid import uuid4

from src.core.summarizer import summarize_chunks
from src.services.embedding_handler import embed_text
from src.utils.config import KEEP_LAST_N_PAIRS, CHUNK_SIZE
from src.utils.text_chunking import chunk_text
from src.utils.history_format import format_chat_history, display_history_chat, clear_user_chat_history
from src.utils.xml_utils import parse_history_xml

def process_history_chat(
    history: list[tuple[str, str]],
    uploaded_by: str = "system",
    user_id: str = "unknown_id",
    source_type: str = "user_conversation"
) -> list[tuple[str, str]]:
    """
    Process chat history into summarized chunks + embedded with metadata.
    Refactored to align with the new metadata standard.
    """
    formatted_text = format_chat_history(history)
    chunks = chunk_text(formatted_text, chunk_size=CHUNK_SIZE)
    summaries = summarize_chunks(chunks)

    # === Generate doc_id from new convention ===
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    timestamp_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    doc_title = "chat_history"
    category = "chat"
    doc_id = f"{category}_{doc_title}_{user_id}_{timestamp_id}"

    for i, (chunk_id, summary) in enumerate(summaries):
        full_chunk_id = f"{doc_id}_summary_chunk_{i}"

        metadata = {
            "doc_id": doc_id,
            "doc_title": doc_title,
            "category": category,
            "chunk_index": i,
            "source_type": source_type,
            "uploaded_by": uploaded_by,
            "user_id": user_id,
            "timestamp": timestamp
        }

        # print(f"📥 Embedding chunk {i}: {full_chunk_id}")
        embed_text(summary, full_chunk_id, metadata)

    return history[-KEEP_LAST_N_PAIRS:] if KEEP_LAST_N_PAIRS > 0 else []


def render_user_chat_history(xml_path: str, user_id: str, session_key: str = "chat_history"):
    with st.sidebar.expander("📜 View Your Chat History", expanded=False):
        history = parse_history_xml(xml_path)
        display_history_chat(history, user_id)

        if os.path.exists(xml_path):
            last_modified = os.path.getmtime(xml_path)
            st.caption(f"🕓 Last updated: {time.ctime(last_modified)}")

        if st.button("🧹 Clear History Content", key="clear_history"):
            if clear_user_chat_history(xml_path, session_key=session_key):
                st.success("✅ Cleared file and in-memory chat history.")
                st.rerun()



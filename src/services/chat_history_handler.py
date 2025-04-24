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
    doc_id: str = "conversation",
    uploaded_by: str = "system",
    position: str = "user",
    source_type: str = "user_conversation",
    user_id: str = "unknown_id"
) -> list[tuple[str, str]]:
    """
    Processes chat history by:
    1. Formatting full conversation
    2. Chunking it
    3. Summarizing each chunk
    4. Embedding summaries with metadata
    5. Truncating history if needed

    Args:
        history (list): List of (user, bot) message pairs.
        doc_id (str): Identifier for this chat history batch.
        uploaded_by (str): Who initiated the chat session.
        position (str): Role of the user or system.

    Returns:
        list: Truncated history for continued tracking.
    """
    formatted_text = format_chat_history(history)
    chunks = chunk_text(formatted_text, chunk_size=CHUNK_SIZE)
    summarized_chunks = summarize_chunks(chunks, doc_id=doc_id)

    timestamp = datetime.now().isoformat()
    session_id = datetime.now().strftime("%Y%m%d%H%M%S")
    
    full_doc_id = f"{doc_id}_{session_id}"
    for i, (chunk_id, summary) in enumerate(summarized_chunks):
        metadata = {
            "doc_id": doc_id,
            "chunk_index": i,
            "source_type": source_type,
            "uploaded_by": uploaded_by,
            "position": position,
            "timestamp": timestamp
        }
        full_chunk_id = f"{doc_id}_{session_id}_summary_chunk_{i}_{user_id}"
        print(full_chunk_id)
        embed_text(summary, full_chunk_id, metadata)

    truncated = history[-KEEP_LAST_N_PAIRS:] if KEEP_LAST_N_PAIRS > 0 else []
    return truncated

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



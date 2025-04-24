import streamlit as st
import os

def display_history_chat(history: list[tuple[str, str]], user_id: str):
    """
    Hiển thị nội dung lịch sử chat dạng gọn đẹp trên UI.
    """
    for i, (user_msg, bot_msg) in enumerate(history):
        st.markdown(f"**🧑 {user_id}:** {user_msg}")
        st.markdown(f"**🤖 Bot:** {bot_msg}")
        st.markdown("---")
        
def clear_user_chat_history(xml_path: str, session_key: str = "chat_history") -> bool:
    """
    Xoá nội dung file XML và xoá session_state tương ứng.

    Returns:
        bool: True nếu xoá thành công, False nếu gặp lỗi.
    """
    try:
        with open(xml_path, "w") as f:
            f.write('<?xml version="1.0" encoding="utf-8"?><chat_history></chat_history>')

        if session_key in st.session_state:
            st.session_state[session_key] = []

        return True
    except Exception as e:
        st.error(f"❌ Failed to clear history: {e}")
        return False

def format_chat_history(chat_history: list[tuple[str, str]]) -> str:
    """
    Converts a list of (user, bot) pairs into a single text block.

    Args:
        chat_history (list): List of conversation pairs.

    Returns:
        str: Concatenated string representing full conversation.
    """
    return "\n".join([f"User: {user}\nBot: {bot}" for user, bot in chat_history])
        
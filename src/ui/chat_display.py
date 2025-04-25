import streamlit as st

def render_chat_history(chat_history):
    """
    Hiển thị toàn bộ lịch sử hội thoại đã lưu trong session_state.chat_history.
    """
    for user_msg, bot_msg in chat_history:
        st.markdown(
            f'<div class="chat-container user"><div class="chat-bubble">{user_msg}</div></div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            f'<div class="chat-container bot"><div class="chat-bubble">{bot_msg}</div></div>',
            unsafe_allow_html=True,
        )

    # CSS để style khung chat
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

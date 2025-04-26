import streamlit as st
GREETING_MESSAGE = """Tôi là EM Bot, là 1 trợ lý hỗ trợ trả lời các câu hỏi liên quan đến dự án 'CHO EM' - Educational Missions, một dự án giáo dục thiện nguyện dành cho các em nhỏ có hoàn cảnh khó khăn ở các vùng sâu vùng xa. Nếu bạn có bất cứ thắc mắc gì về dự án cần hỏi, hãy cho tôi biết và tôi luôn sẵn lòng trả lời bạn. Nếu bạn muốn theo dõi hành trình của 'EM', hãy nhấn vào link: https://www.facebook.com/info.duanchoem và đừng ngần ngại cho 'EM' xin một follow và một lượt like cũng như lượt chia sẻ nhé!"""
import re

def render_chat_history(chat_history):
    def auto_linkify(text):
        # Detect URL và biến thành thẻ <a>
        url_pattern = r"(https?://[^\s]+)"
        return re.sub(url_pattern, r'<a href="\1" target="_blank">\1</a>', text)

    # Nếu history trống thì show greeting
    if not chat_history:
        bot_message = auto_linkify(GREETING_MESSAGE)
        st.markdown(
            f'<div class="chat-container bot"><div class="chat-bubble">{bot_message}</div></div>',
            unsafe_allow_html=True,
        )

    # Render history
    for user_msg, bot_msg in chat_history:
        user_message = auto_linkify(user_msg)
        bot_message = auto_linkify(bot_msg)

        st.markdown(
            f'<div class="chat-container user"><div class="chat-bubble">{user_message}</div></div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            f'<div class="chat-container bot"><div class="chat-bubble">{bot_message}</div></div>',
            unsafe_allow_html=True,
        )

    # CSS
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
        .user .chat-bubble {
            background-color: #DCF8C6;
        }
        .bot .chat-bubble {
            background-color: #f1f1f1;
        }
        a {
            color: #1a73e8;
            text-decoration: underline;
        }
        </style>
    """, unsafe_allow_html=True)

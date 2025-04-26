import streamlit as st
from src.core.chat import chat_with_gpt
from src.utils.xml_utils import save_history_to_xml
from src.core.traffic_controller import queue_if_overloaded, check_and_dispatch

def chat_input(user_id: str, history_file_path):

    user_input = st.chat_input("Ask me anything...")

    if user_input:
        if queue_if_overloaded(user_id, query_type="chat"):
            st.warning("⏳ Hệ thống đang bận. Bạn đang được đưa vào hàng chờ.")
            st.stop()

        if not check_and_dispatch(user_id):
            st.info("🔄 Vui lòng đợi vài giây, hệ thống sẽ tự động xử lý khi sẵn sàng.")
            st.stop()

        st.markdown(
            f'<div class="chat-container user"><div class="chat-bubble">{user_input}</div></div>',
            unsafe_allow_html=True
        )

        bot_placeholder = st.empty()
        bot_placeholder.markdown(
            '<div class="chat-container bot"><div class="chat-bubble">🤖 Thinking...</div></div>',
            unsafe_allow_html=True
        )

        response, updated_history = chat_with_gpt(user_input, st.session_state.chat_history, user_id)

        bot_placeholder.markdown(
            f'<div class="chat-container bot"><div class="chat-bubble">{response}</div></div>',
            unsafe_allow_html=True
        )

        # ====== Save to session + file XML ======
        st.session_state.chat_history = updated_history
        save_history_to_xml(updated_history, path=history_file_path)

        st.rerun()

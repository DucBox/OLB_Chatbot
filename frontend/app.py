# ================== PYTHONPATH CONFIG ==================
import os
import streamlit as st
from src.utils.config import HISTORY_STORE_PATH
from src.utils.xml_utils import load_history_from_xml
from src.ui.login_panel import login_panel
from src.ui.sidebar_manager import sidebar_doc_manager
from src.ui.chat_display import render_chat_history
from src.ui.chat_input_box import chat_input
from src.ui.upload_file_ui import render_upload_block
from src.ui.gg_sheet import render_gsheet_block
from src.ui.title import render_logo_header


# ========== UI Setup ==========
st.set_page_config(page_title="EM Assistant", page_icon="🤖", layout="wide")
render_logo_header("frontend/assets/EM_logo.png")

# ========== LOGIN ==========
user_id, user_role = login_panel()
if not user_id or not user_role:
    st.stop()
if st.sidebar.button("🚪 Logout"):
        st.session_state.clear()
        st.rerun()# ========== Sidebar ==========
sidebar_doc_manager(user_id, user_role)

# ========== File XML ==========
USER_HISTORY_CHAT_FILE = HISTORY_STORE_PATH / f"chat_history_{user_id}.xml"

if not os.path.exists(USER_HISTORY_CHAT_FILE):
    os.makedirs(os.path.dirname(USER_HISTORY_CHAT_FILE), exist_ok=True)
    with open(USER_HISTORY_CHAT_FILE, "w", encoding="utf-8") as f:
        f.write(
            """<?xml version="1.0" encoding="utf-8"?>
            <chat_history>
                <exchange>
                    <user> Bạn là ai? Bạn có thể làm những gì? </user>
                    <bot> Tôi là EM Bot, là 1 trợ lý hỗ trợ trả lời các câu hỏi liên quan đến dự án 'CHO EM' - Educational Missions, một dự án giáo dục thiện nguyện dành cho các em nhỏ có hoàn cảnh khó khăn ở các vùng sâu vùng xa. Nếu bạn có bất cứ thắc mắc gì về dự án cần hỏi, hãy cho tôi biết và tôi luôn sẵn lòng trả lời bạn. Nếu bạn muốn theo dõi hành trình của 'EM', hãy nhấn vào link: https://www.facebook.com/info.duanchoem và đừng ngần ngại cho 'EM' xin một follow và một lượt like cũng như lượt chia sẻ nhé! </bot>
                </exchange>
            </chat_history>
            """
        )

# ========== Load Chat History ==========
if "chat_history" not in st.session_state:
    st.session_state.chat_history = load_history_from_xml(USER_HISTORY_CHAT_FILE)

# ========== Display Chat ==========
render_chat_history(st.session_state.chat_history)

# ========== Chat Input ==========
chat_input(user_id, USER_HISTORY_CHAT_FILE)

# ========== Upload (Admin/Core) ==========
if user_role in ["admin", "core"]:
    render_upload_block()
    render_gsheet_block()
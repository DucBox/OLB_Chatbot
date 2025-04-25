import streamlit as st
from collections import defaultdict
from src.services.doc_storage_manager import (
    list_all_docs_metadata_firebase,
    delete_by_doc_id,
    delete_by_category,
    delete_by_doc_title
)
from src.services.chat_history_handler import render_user_chat_history
from src.utils.config import HISTORY_STORE_PATH
from src.core.traffic_controller import get_current_queue
import psutil
import time
import os
from streamlit_autorefresh import st_autorefresh
def sidebar_doc_manager(user_id: str, user_role: str):
    """
    Hiển thị sidebar cho admin/core để quản lý tài liệu và lịch sử chat.
    """
    st.sidebar.success(f"👋 Welcome, {user_id} ({user_role})")

    if user_role in ["admin", "core"]:
        st.sidebar.markdown("### 🗂 Document Manager")

        try:
            all_docs = list_all_docs_metadata_firebase(user_id)

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
    
        # ================== DEBUG TRAFFIC QUEUE (for admin/core) ==================
    if user_role in ["admin"]:
        st.sidebar.markdown("### 🚦 Traffic Monitor")

        with st.sidebar.expander("📊 Current Traffic Queue", expanded=False):
            queue = get_current_queue()

            if not queue:
                st.markdown("✅ No user currently in queue.")
            else:
                for i, entry in enumerate(queue, start=1):
                    wait_sec = time.time() - entry["timestamp"]
                    st.markdown(
                        f"**{i}.** 👤 `{entry['user']}` | Type: `{entry['type']}` | Wait: `{int(wait_sec)}s`"
                    )
        with st.sidebar.expander("🧠 RAM Usage (Auto Update)", expanded=True):
            # ⏱️ Tự động refresh lại mỗi 3 giây
            st_autorefresh(interval=3000, key="ram_update")

            # 📊 Thông tin RAM của toàn hệ thống
            mem = psutil.virtual_memory()
            total = mem.total / (1024 ** 3)
            used = mem.used / (1024 ** 3)
            percent = mem.percent

            # 📦 RAM của process hiện tại (Python app của bạn)
            process = psutil.Process(os.getpid())
            ram_usage = process.memory_info().rss / (1024 ** 3)

            st.markdown(f"**Your App RAM Usage:** {ram_usage:.2f} GB")
            st.markdown(f"**Total RAM:** {total:.2f} GB")
            st.markdown(f"**Used RAM:** {used:.2f} GB ({percent}%)")
                

    # Hiển thị lịch sử chat người dùng
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📂 System Logs")
    with st.sidebar.expander("📜 View Your Chat History", expanded=False):
        USER_HISTORY_CHAT_FILE = HISTORY_STORE_PATH / f"chat_history_{user_id}.xml"
        render_user_chat_history(USER_HISTORY_CHAT_FILE, user_id)

import os
import streamlit as st
from src.services.uploaded_files_handler import process_uploaded_docs

def render_upload_block():

    with st.expander("📤 Upload Document", expanded=False):  
        col1, col2, col3, col4 = st.columns([5, 2, 2, 2])

        with col1:
            uploaded_file = st.file_uploader("📂 File", type=["pdf", "txt"], label_visibility="collapsed")

        with col2:
            category = st.text_input("🏷️ Category", key="file_category_input")

        with col3:
            doc_title = st.text_input("📄 Document Title", key="file_uploaded_by_input")

        with col4:
            uploaded_by = st.text_input("👤 Uploaded by")

        st.markdown("<div style='height: 10px'></div>", unsafe_allow_html=True)

        if st.button("📤 Upload"):
            if uploaded_file and category and doc_title and uploaded_by:
                temp_path = os.path.join("temp", uploaded_file.name)
                os.makedirs("temp", exist_ok=True)
                with open(temp_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())

                process_uploaded_docs(
                    file_path=temp_path,
                    category=category,
                    doc_title=doc_title,
                    uploaded_by=uploaded_by,
                )
                st.rerun()
            else:
                st.warning("⚠️ Please fill all fields.")

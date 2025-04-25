import streamlit as st
from src.services.extract_from_gg_sheet import process_google_sheet_to_embedding

def render_gsheet_block():
    """
    UI để người dùng nhập Google Sheet URL và đưa vào hệ thống (chỉ admin/core).
    """
    with st.expander("🌐 Use Google Sheet Link", expanded=False):
        col1, col2, col3, col4 = st.columns([4, 1, 2, 2])

        with col1:
            sheet_url = st.text_input("🔗 Google Sheet URL", key="sheet_url_input")

        with col2:
            max_sheets = st.number_input("📄 Max Sheets",  min_value=1, value=5, step=1)

        with col3:
            category = st.text_input("🏷️ Category (e.g., EM_Project", key="gsheet_category_input")

        with col4:
            uploaded_by = st.text_input("👤 Name", key="gsheet_uploaded_by_input")

        # 👉 Nút mở tutorial dialog
        if st.button("📘 How to Upload Google Sheet?"):
            show_tutorial()

        st.markdown("<div style='height: 10px'></div>", unsafe_allow_html=True)

        if st.button("🚀 Process Sheet"):
            if sheet_url and category and uploaded_by:
                process_google_sheet_to_embedding(
                    sheet_url=sheet_url,
                    category=category,
                    uploaded_by=uploaded_by,
                    max_sheets=int(max_sheets)
                )
                st.rerun()
            else:
                st.warning("⚠️ Please fill in all fields.")

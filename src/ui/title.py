import base64
import streamlit as st

def render_logo_header(image_path: str):

    image_base64 = get_image_base64(image_path)

    st.markdown(
        f"""
        <h1 style='display: flex; align-items: center; gap: 10px;'>
            <img src='data:image/png;base64,{image_base64}' width='65'/>
            AI Bot Assistant
        </h1>
        """,
        unsafe_allow_html=True
    )

def get_image_base64(path):
    with open(path, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()

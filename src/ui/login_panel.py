import streamlit as st
from src.services.user_manager import get_user_by_id, create_user, check_user_credentials, get_user_role

def login_panel():
    user_id = st.session_state.get("user_id")
    user_role = st.session_state.get("user_role")

    if not user_id or not user_role:
        with st.sidebar.expander("🔐 Admin / Core Login/Register", expanded=True):
            action = st.radio("Select action", ["Login", "Register"], horizontal=True)
            user_input = st.text_input("👤 ID")
            password_input = st.text_input("🔑 Password", type="password")

            if st.button("🚀 Proceed"):
                if not user_input or not password_input:
                    st.warning("⚠️ Please fill in both fields.")
                    st.stop()

                user_data = get_user_by_id(user_input)
                if action == "Register":
                    if user_data:
                        st.error("❌ User ID already exists.")
                    else:
                        create_user(user_input, password_input, role="user")
                        st.session_state.user_id = user_input
                        st.session_state.user_role = "user"
                        st.rerun()
                elif action == "Login":
                    if not user_data:
                        st.error("❌ User ID not found.")
                    elif not check_user_credentials(user_input, password_input):
                        st.error("❌ Incorrect password.")
                    else:
                        st.session_state.user_id = user_input
                        st.session_state.user_role = get_user_role(user_input)
                        st.rerun()

    return st.session_state.get("user_id"), st.session_state.get("user_role")

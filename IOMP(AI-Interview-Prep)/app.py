import streamlit as st
from dotenv import load_dotenv
import os

from components.auth import render_auth
from components.dashboard import render_dashboard
from components.interview import render_interview
from components.feedback import render_feedback
from components.chatbot import render_chatbot
from components.verification import render_verification

load_dotenv(override=True)

st.set_page_config(
    page_title="AI Interview Coach",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="collapsed"
)
st.markdown("""
<style>
    /* Hide top header and main menu to feel like an app */
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Ensure no visual layout shifting */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
</style>
""", unsafe_allow_html=True)

def main():
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 'auth'
    if 'user_data' not in st.session_state:
        st.session_state.user_data = None
        
    if not st.session_state.authenticated:
        render_auth()
    else:
        if st.session_state.current_page == 'dashboard':
            render_dashboard()
        elif st.session_state.current_page == 'interview':
            render_interview()
        elif st.session_state.current_page == 'feedback':
            render_feedback()
        elif st.session_state.current_page == 'chatbot':
            render_chatbot()
        elif st.session_state.current_page == 'verification':
            render_verification()
        else:
            st.session_state.current_page = 'dashboard'
            st.rerun()

if __name__ == "__main__":
    main()
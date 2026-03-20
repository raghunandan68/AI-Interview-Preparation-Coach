import streamlit as st

def render_dashboard():
    st.markdown("<h1 style='text-align: center; margin-bottom: 2rem;'>Dashboard 🏠</h1>", unsafe_allow_html=True)
    
    if st.session_state.get('user_data'):
        name = st.session_state.user_data.user_metadata.get('full_name', 'User')
        st.markdown(f"### Welcome, {name}!")
        
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Select Job Role")
        roles = [
            "Software Engineer",
            "Data Analyst",
            "Product Manager",
            "Data Scientist",
            "Frontend Developer",
            "Backend Developer",
            "Full Stack Developer",
            "DevOps Engineer"
        ]
        selected_role = st.selectbox("Job Role", roles, label_visibility="collapsed")
        
        st.markdown("### Select Interview Round")
        rounds = [
            "Technical Round",
            "HR Round",
            "Behavioral Round"
        ]
        selected_round = st.selectbox("Interview Round", rounds, label_visibility="collapsed")
        
    st.markdown("---")
    
    col_t1, col_t2 = st.columns([1, 1])
    with col_t1:
        st.markdown("### ⏱️ Timer Settings")
        timer_options = {
            "5 Minutes": 300,
            "10 Minutes": 600,
            "15 Minutes": 900,
            "20 Minutes": 1200,
            "No Timer": None
        }
        selected_timer_label = st.selectbox("Duration", list(timer_options.keys()), index=1)
        selected_timer_seconds = timer_options[selected_timer_label]

    with col_t2:
        st.markdown("### ⚙️ Interview Settings")
        categories = ["DSA (LeetCode Style)", "Logic & Math", "Project-based Scenario", "System Design"]
        selected_category = st.selectbox("Question Category", categories, index=0)
        difficulty = st.selectbox("Difficulty Level", ["Easy", "Medium", "Hard"], index=0)
    
    col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
    with col_btn2:
        if st.button("🚀 Start Interview", use_container_width=True, type="primary"):
            st.session_state.interview_role = selected_role
            st.session_state.interview_round = selected_round
            st.session_state.interview_difficulty = difficulty
            st.session_state.interview_category = selected_category
            st.session_state.interview_timer_limit = selected_timer_seconds
            st.session_state.current_page = 'interview'
            if "start_time" in st.session_state: del st.session_state.start_time
            # Clear previous questions for a fresh start
            if "current_question" in st.session_state: del st.session_state.current_question
            if "current_hr_question" in st.session_state: del st.session_state.current_hr_question
            st.rerun()

    # Log out logic
    if st.button("Logout", key="logout_btn", type="secondary"):
        st.session_state.authenticated = False
        st.session_state.user_data = None
        st.session_state.current_page = 'auth'
        st.rerun()

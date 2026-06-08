import streamlit as st

from utils.supabase_client import get_supabase

def render_dashboard():
    st.markdown("<h1 style='text-align: center; margin-bottom: 2rem;'>Dashboard 🏠</h1>", unsafe_allow_html=True)
    
    if st.session_state.get('user_data'):
        name = st.session_state.user_data.user_metadata.get('full_name', 'User')
        st.markdown(f"### Welcome, {name}!")
        
    st.markdown("---")
    
    # Tab selection logic (Hide Past Interviews tab in Guest Mode)
    if st.session_state.user_data.is_dev:
        # Only show the "Start New Interview" content directly
        st.markdown("### 🚀 Start New Practice Session (Guest)")
        # We reuse the tab_new logic but without the tab structure
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### Select Job Role")
            roles = ["Software Engineer", "Data Analyst", "Product Manager", "Data Scientist", "Frontend Developer", "Backend Developer", "Full Stack Developer", "DevOps Engineer"]
            selected_role = st.selectbox("Job Role", roles, label_visibility="collapsed", key="guest_role")
            
            st.markdown("### Select Interview Round")
            rounds = ["Technical Round", "HR Round", "Behavioral Round"]
            selected_round = st.selectbox("Interview Round", rounds, label_visibility="collapsed", key="guest_round")
            
        st.markdown("---")
        
        col_t1, col_t2 = st.columns([1, 1])
        with col_t1:
            st.markdown("### ⏱️ Timer Settings")
            timer_options = {"5 Minutes": 300, "10 Minutes": 600, "15 Minutes": 900, "20 Minutes": 1200, "No Timer": None}
            selected_timer_label = st.selectbox("Duration", list(timer_options.keys()), index=1, key="guest_timer")
            selected_timer_seconds = timer_options[selected_timer_label]

        with col_t2:
            st.markdown("### ⚙️ Interview Settings")
            categories = ["DSA (LeetCode Style)", "Logic & Math", "Project-based Scenario", "System Design"]
            selected_category = st.selectbox("Question Category", categories, index=0, key="guest_category")
            difficulty = st.selectbox("Difficulty Level", ["Easy", "Medium", "Hard"], index=0, key="guest_difficulty")
        
        col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
        with col_btn2:
            if st.button("🚀 Start Guest Interview", use_container_width=True, type="primary"):
                st.session_state.interview_role = selected_role
                st.session_state.interview_round = selected_round
                st.session_state.interview_difficulty = difficulty
                st.session_state.interview_category = selected_category
                st.session_state.interview_timer_limit = selected_timer_seconds
                st.session_state.current_page = 'verification'
                
                # Wipe all previous interview-related state for a clean start
                keys_to_clear = [
                    'start_time', 'time_limit', 'current_question', 'current_hr_question', 
                    'code_answer', 'answer_text', 'interview_transcript', 'interview_data', 
                    'feedback_report', 'code_output', 'esc_count', 'last_q_added', 'messages',
                    'permissions_confirmed', 'mic_granted'
                ]
                for k in keys_to_clear:
                    if k in st.session_state:
                        del st.session_state[k]
                st.rerun()
    else:
        # Normal Tabbed Interface for Registered Users
        tab_new, tab_history = st.tabs(["🚀 Start New Interview", "📜 Past Interviews"])
        
        with tab_new:
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### Select Job Role")
                roles = ["Software Engineer", "Data Analyst", "Product Manager", "Data Scientist", "Frontend Developer", "Backend Developer", "Full Stack Developer", "DevOps Engineer"]
                selected_role = st.selectbox("Job Role", roles, label_visibility="collapsed")
                
                st.markdown("### Select Interview Round")
                rounds = ["Technical Round", "HR Round", "Behavioral Round"]
                selected_round = st.selectbox("Interview Round", rounds, label_visibility="collapsed")
                
            st.markdown("---")
            
            col_t1, col_t2 = st.columns([1, 1])
            with col_t1:
                st.markdown("### ⏱️ Timer Settings")
                timer_options = {"5 Minutes": 300, "10 Minutes": 600, "15 Minutes": 900, "20 Minutes": 1200, "No Timer": None}
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
                    st.session_state.current_page = 'verification'
                    
                    # Wipe all previous interview-related state for a clean start
                    keys_to_clear = [
                        'start_time', 'time_limit', 'current_question', 'current_hr_question', 
                        'code_answer', 'answer_text', 'interview_transcript', 'interview_data', 
                        'feedback_report', 'code_output', 'esc_count', 'last_q_added', 'messages',
                        'permissions_confirmed', 'mic_granted'
                    ]
                    for k in keys_to_clear:
                        if k in st.session_state:
                            del st.session_state[k]
                    st.rerun()

        with tab_history:
            st.markdown("### Your Interview History")
            try:
                supabase = get_supabase()
                user_id = st.session_state.user_data.id
                
                # Fetch history sorted by date
                response = supabase.table("interview_history").select("*").eq("user_id", user_id).order("created_at", desc=True).execute()
                history_data = response.data
                
                if not history_data:
                    st.info("You haven't completed any interviews yet. Your past performance will appear here.")
                else:
                    for idx, entry in enumerate(history_data):
                        date_str = entry['created_at'][:10]
                        with st.expander(f"📅 {date_str} - {entry['role']} ({entry['round_type']})"):
                            st.markdown(f"**Question:** {entry['question']}")
                            st.markdown("---")
                            st.markdown("### 📝 Your Answer")
                            if "Technical" in entry['round_type']:
                                st.code(entry['user_answer'], language="python")
                            else:
                                st.write(entry['user_answer'])
                            st.markdown("---")
                            st.markdown("### 📊 AI Feedback")
                            st.markdown(entry['feedback_report'])
            except Exception as e:
                st.error(f"Error loading history: {e}")

    # Log out logic
    st.markdown("---")
    if st.button("Logout", key="logout_btn", type="secondary"):
        st.session_state.authenticated = False
        st.session_state.user_data = None
        st.session_state.current_page = 'auth'
        st.rerun()

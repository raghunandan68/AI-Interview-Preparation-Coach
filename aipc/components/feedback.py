import streamlit as st
from utils.grok_api import call_grok_api

def generate_feedback(interview_data):
    prompt = f"""
    You are an expert AI Interview Coach. The user just completed a {interview_data['round']} interview.
    
    Question asked:
    {interview_data['question']}
    
    User's Answer text/code:
    {interview_data['answer']}
    
    Evaluate the performance and provide a detailed review formatted exactly in this markdown structure:
    ### 1. Score / Performance Summary
    [Score out of 10 and brief summary]
    
    ### 2. Ideal Answer
    [What the perfect answer or optimal code looks like]
    
    ### 3. Comparison Analysis
    [How the user's answer compares to the ideal answer]
    
    ### 4. Skill Gap Identification
    [Highlight specific areas where the candidate is lacking]
    
    ### 5. Suggestions for Improvement
    [Actionable advice for the candidate to improve]
    """
    
    return call_grok_api([{"role": "system", "content": "You are a helpful and strict expert technical interviewer."}, {"role": "user", "content": prompt}], temperature=0.5)

def render_feedback():
    st.markdown("<h1 style='text-align: center;'>Interview Feedback & Analysis 📊</h1>", unsafe_allow_html=True)
    st.markdown("---")
    
    if 'interview_data' not in st.session_state or not st.session_state.interview_data:
        st.warning("No interview data found. Please complete an interview first.")
        if st.button("Return to Dashboard", type="primary"):
            st.session_state.current_page = 'dashboard'
            st.rerun()
        return

    if 'feedback_report' not in st.session_state:
        with st.spinner("Analyzing your performance... This may take a moment."):
            report = generate_feedback(st.session_state.interview_data)
            st.session_state.feedback_report = report
            
            # Save to Supabase interview_history
            try:
                from utils.supabase_client import get_supabase
                supabase = get_supabase()
                user_id = st.session_state.user_data.id
                
                supabase.table("interview_history").insert({
                    "user_id": user_id,
                    "role": st.session_state.get('interview_role', 'Unknown'),
                    "round_type": st.session_state.interview_data['round'],
                    "question": st.session_state.interview_data['question'],
                    "user_answer": st.session_state.interview_data['answer'],
                    "feedback_report": report
                }).execute()
            except Exception as e:
                st.warning(f"Could not save history to database (ensure schema is deployed): {e}")
            
    st.markdown(st.session_state.feedback_report)
    
    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔙 Back to Dashboard", use_container_width=True):
            # Clean up interview state
            keys_to_clear = ['interview_data', 'feedback_report', 'current_question', 'current_hr_question', 'code_answer']
            for k in keys_to_clear:
                if k in st.session_state:
                    del st.session_state[k]
            st.session_state.current_page = 'dashboard'
            st.rerun()
            
    with col2:
        if st.button("💬 Chat with AI Coach", use_container_width=True, type="primary"):
            st.session_state.current_page = 'chatbot'
            st.rerun()

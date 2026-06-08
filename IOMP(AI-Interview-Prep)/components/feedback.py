import streamlit as st
from utils.grok_api import call_grok_api

def generate_feedback(interview_data):
    transcript = interview_data.get('transcript', [])
    if not transcript:
        # Fallback for old single-question data
        transcript = [{"question": interview_data.get('question', 'N/A'), "answer": interview_data.get('answer', 'N/A')}]
    
    transcript_text = ""
    for i, entry in enumerate(transcript):
        transcript_text += f"\n### Question {i+1}\n{entry['question']}\n\n### Answer {i+1}\n{entry['answer']}\n\n"

    prompt = f"""
    You are an expert AI Interview Coach. The user just completed a {interview_data['round']} interview session with {len(transcript)} question(s).
    
    Here is the full transcript of the interview:
    {transcript_text}
    
    Evaluate the candidate's overall performance across all questions and provide a comprehensive review formatted exactly in this markdown structure:
    ### 1. Score / Performance Summary
    [Provide an overall score out of 10 and a summary of their performance across all questions]
    
    ### 2. Ideal Answers / Approach
    [Briefly describe the ideal approach or code for each question asked]
    
    ### 3. Comprehensive Analysis
    [How the user's answers compare to the ideal benchmarks across the entire session]
    
    ### 4. Skill Gap Identification
    [Highlight recurring or specific themes where the candidate is lacking]
    
    ### 5. Suggestions for Improvement
    [Actionable advice for the candidate to improve their performance in future interviews]
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
        with st.spinner("Analyzing your full performance... This may take a moment."):
            report = generate_feedback(st.session_state.interview_data)
            st.session_state.feedback_report = report
            
            # Save to Supabase interview_history (skip if in Guest Mode)
            try:
                if st.session_state.user_data.is_dev:
                    st.info("💡 Guest Mode: Your feedback is provided below, but it will NOT be saved. Ensure you copy anything you'd like to keep before leaving this page.")
                else:
                    from utils.supabase_client import get_supabase
                    supabase = get_supabase()
                    user_id = st.session_state.user_data.id
                    
                    transcript = st.session_state.interview_data.get('transcript', [])
                    consolidated_questions = "\n\n".join([f"Q{i+1}: {e['question']}" for i, e in enumerate(transcript)])
                    consolidated_answers = "\n\n".join([f"A{i+1}: {e['answer']}" for i, e in enumerate(transcript)])

                    supabase.table("interview_history").insert({
                        "user_id": user_id,
                        "role": st.session_state.get('interview_role', 'Unknown'),
                        "round_type": st.session_state.interview_data['round'],
                        "question": consolidated_questions,
                        "user_answer": consolidated_answers,
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
            keys_to_clear = [
                'interview_data', 'feedback_report', 'current_question', 'current_hr_question', 
                'code_answer', 'answer_text', 'interview_transcript', 'code_output', 
                'start_time', 'time_limit', 'esc_count', 'last_q_added', 'messages'
            ]
            for k in keys_to_clear:
                if k in st.session_state:
                    del st.session_state[k]
            st.session_state.current_page = 'dashboard'
            st.rerun()
            
    with col2:
        if st.button("💬 Chat with AI Coach", use_container_width=True, type="primary"):
            st.session_state.current_page = 'chatbot'
            st.rerun()

import streamlit as st
from streamlit_ace import st_ace
from utils.grok_api import call_grok_api

def inject_tab_switching_js(remaining_seconds=None):
    timer_script = ""
    if remaining_seconds:
        timer_script = f"""
        // 4. Live Timer Countdown
        let secondsLeft = {remaining_seconds};
        const timerInterval = setInterval(() => {{
            const timerSpan = parentDoc.getElementById("live-timer-text");
            if (timerSpan) {{
                let mins = Math.floor(secondsLeft / 60);
                let secs = secondsLeft % 60;
                timerSpan.innerText = `⏱️ ${{mins.toString().padStart(2, '0')}}:${{secs.toString().padStart(2, '0')}}`;
                
                if (secondsLeft < 60) timerSpan.style.color = "red";
                
                if (secondsLeft <= 0) {{
                    clearInterval(timerInterval);
                    const buttons = Array.from(parentDoc.querySelectorAll('button'));
                    const submitBtn = buttons.find(b => b.innerText.includes('Submit Answer & End Round'));
                    if (submitBtn) submitBtn.click();
                }}
            }}
            secondsLeft--;
        }}, 1000);
        """

    js_code = f"""
    <script>
    const parentDoc = window.parent.document;
    
    // 1. Detect tab switching
    parentDoc.addEventListener("visibilitychange", function() {{
        if (parentDoc.hidden) {{
            alert("WARNING: Tab switching detected! Your interview is completely terminated and evaluated.");
            const buttons = Array.from(parentDoc.querySelectorAll('button'));
            const terminateBtn = buttons.find(b => b.innerText.includes('TAB_SWITCH_TERMINATE'));
            if (terminateBtn) terminateBtn.click();
        }}
    }});
    
    // 2. Hide the secret terminate button visually using JS
    setTimeout(() => {{
        const buttons = Array.from(parentDoc.querySelectorAll('button'));
        const terminateBtn = buttons.find(b => b.innerText.includes('TAB_SWITCH_TERMINATE'));
        if (terminateBtn) terminateBtn.style.display = 'none';
        
        // 3. Fullscreen logic (Auto-fullscreen attempt)
        if (parentDoc.documentElement.requestFullscreen) {{
            parentDoc.documentElement.requestFullscreen().catch(e => {{
                console.log("Auto-fullscreen requires user interaction.");
            }});
        }}

        const fsBtn = buttons.find(b => b.innerText.includes('Enter Full Screen'));
        if (fsBtn) {{
            fsBtn.addEventListener('click', () => {{
                if (parentDoc.documentElement.requestFullscreen) {{
                    parentDoc.documentElement.requestFullscreen();
                }}
            }});
        }}
        {timer_script}
    }}, 500);
    </script>
    """
    st.components.v1.html(js_code, height=0)

def end_interview():
    st.session_state.current_page = 'feedback'
    st.rerun()

def render_technical_round():
    # Split layout: Question/Editor on left, small camera on the right
    col_main, col_cam = st.columns([3, 1])
    
    with col_main:
        st.markdown("### Technical Round")
        
        if 'current_question' not in st.session_state:
            with st.spinner("Generating question..."):
                dif = st.session_state.get('interview_difficulty', 'Medium')
                cat = st.session_state.get('interview_category', 'DSA (LeetCode Style)')
                prompt = (
                    f"Generate a {dif} difficulty coding interview question in the category of '{cat}' for a {st.session_state.interview_role} role. "
                    "If the category is DSA, focus on a high-quality problem (e.g., Arrays, Strings, Trees, DP) that is commonly asked in real interviews. "
                    "Keep the question text and requirements EXTREMELY CONCISE (max 3-4 sentences total). "
                    "Return ONLY the question text and requirements, no code."
                )
                question = call_grok_api([{"role": "user", "content": prompt}])
                st.session_state.current_question = question
                st.session_state.code_answer = "# Write your code here\n"
        
        st.info(st.session_state.current_question)
        
        st.markdown("#### Code Editor")
        code = st_ace(
            value=st.session_state.code_answer,
            language="python",
            theme="monokai",
            keybinding="vscode",
            font_size=16,
            tab_size=4,
            height=400
        )
        
        if code != st.session_state.code_answer:
            st.session_state.code_answer = code
            
    with col_cam:
        # Consistency: Tech round now also has webcam proctoring
        st.camera_input("Proctoring Feed", key="tech_cam_input")
        
    if st.button("Submit Answer & End Round", type="primary", use_container_width=True):
        st.session_state.interview_data = {
            "question": st.session_state.current_question,
            "answer": st.session_state.code_answer,
            "round": "Technical"
        }
        end_interview()

def render_hr_round():
    st.markdown("### HR / Behavioral Round")
    
    if 'current_hr_question' not in st.session_state:
        with st.spinner("Generating question..."):
            dif = st.session_state.get('interview_difficulty', 'Medium')
            cat = st.session_state.get('interview_category', 'Project-based Scenario')
            prompt = (
                f"Generate a {dif} difficulty behavioral/HR interview question focused on '{cat}' for a {st.session_state.interview_role} role. "
                "The question should be a realistic industry scenario and concise (max 2 sentences). "
                "Return ONLY the question text."
            )
            question = call_grok_api([{"role": "user", "content": prompt}])
            st.session_state.current_hr_question = question
            
    # Split layout: Question/Answer on left, small camera on the right
    col_main, col_cam = st.columns([3, 1])
    
    with col_main:
        st.info(st.session_state.current_hr_question)
        
        st.markdown("#### Voice Answer (Optional)")
        audio_val = st.audio_input("Record your answer via microphone 🎤", key="hr_audio_input")
        
        transcribed_text = ""
        if audio_val:
            with st.spinner("Transcribing audio..."):
                try:
                    import speech_recognition as sr
                    r = sr.Recognizer()
                    with sr.AudioFile(audio_val) as source:
                        audio_data = r.record(source)
                        transcribed_text = r.recognize_google(audio_data)
                except Exception as e:
                    st.error(f"Speech recognition error: {e}")
                    
        st.markdown("#### Your Final Answer")
        # Auto-fills with voice transcription if provided, otherwise blank for typing
        answer_text = st.text_area("Type or edit your answer here...", value=transcribed_text, height=150)
        
    with col_cam:
        img = st.camera_input("Webcam Feed")
    
    if st.button("Submit Answer & End Round", type="primary", use_container_width=True):
        st.session_state.interview_data = {
            "question": st.session_state.current_hr_question,
            "answer": answer_text,
            "round": st.session_state.interview_round
        }
        end_interview()

def render_interview():
    # CSS to hide the secret proctoring button immediately
    st.markdown("""
        <style>
        div[data-testid="stButton"] button:contains("TAB_SWITCH_TERMINATE") {
            display: none !important;
        }
        </style>
    """, unsafe_allow_html=True)
    
    
    role = st.session_state.get('interview_role', 'Candidate')
    round_type = st.session_state.get('interview_round', 'Technical Round')
    # Check for timer settings from dashboard
    time_limit = st.session_state.get('interview_timer_limit')
    
    timer_html = ""
    remaining_seconds = None
    
    if time_limit:
        if "start_time" not in st.session_state:
            import time
            st.session_state.start_time = time.time()
            st.session_state.time_limit = time_limit
            
        import time
        elapsed = time.time() - st.session_state.start_time
        remaining_seconds = max(0, int(st.session_state.time_limit - elapsed))
        
        # Initial display values
        mins, secs = divmod(remaining_seconds, 60)
        timer_color = "red" if remaining_seconds < 60 else "white"
        
        timer_html = f"""
            <div style='background: #333; padding: 10px 20px; border-radius: 10px; border: 1px solid {timer_color};'>
                <span id="live-timer-text" style='color: {timer_color}; font-family: monospace; font-size: 1.5rem;'>
                    ⏱️ {mins:02d}:{secs:02d}
                </span>
            </div>
        """
    else:
        timer_html = "<div style='color: gray; font-style: italic;'>Timer Disabled</div>"

    inject_tab_switching_js(remaining_seconds)
    
    st.markdown(f"<div style='display: flex; justify-content: space-between; align-items: center;'><h2>🔴 {role} ({round_type})</h2>{timer_html}</div>", unsafe_allow_html=True)
    st.markdown("---")
    
    col_fs, col_end = st.columns([4, 1])
    with col_fs:
        st.button("🔲 Enter Full Screen", type="primary", use_container_width=True)
    with col_end:
        if st.button("End Early", type="secondary", use_container_width=True):
            st.session_state.interview_data = {
                "question": st.session_state.get('current_hr_question', st.session_state.get('current_question', '(No question generated)')),
                "answer": "Candidate ended interview manually.",
                "round": round_type
            }
            if "start_time" in st.session_state: del st.session_state.start_time
            end_interview()
            st.rerun()
            
    # Secret button that Javascript clicks when Tab Switching is detected
    if st.button("TAB_SWITCH_TERMINATE", type="secondary"):
        st.session_state.interview_data = {
            "question": st.session_state.get('current_hr_question', st.session_state.get('current_question', '(No question generated)')),
            "answer": "SYSTEM VIOLATION: Candidate completely switched tabs during the live interview. Evaluate them strictly. Note this massive negative cheating behavioral flag.",
            "round": round_type
        }
        end_interview()
            
    if "Technical" in round_type:
        render_technical_round()
    else:
        render_hr_round()

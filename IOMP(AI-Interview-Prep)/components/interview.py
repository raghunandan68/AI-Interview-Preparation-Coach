import streamlit as st
from streamlit_ace import st_ace
from utils.grok_api import call_grok_api
from utils.piston_api import execute_code
import cv2
import numpy as np

# Load the pre-trained Haar Cascade for face detection
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

def count_faces(image_file):
    if image_file is None:
        return 0
    try:
        if face_cascade.empty():
            print("Face cascade is empty! Check path.")
            return 1 # Fail safe: assume at least 1 person exists if we can't detect
            
        # Read image using getvalue() to be safer than read()
        file_bytes = np.asarray(bytearray(image_file.getvalue()), dtype=np.uint8)
        img = cv2.imdecode(file_bytes, 1)
        if img is None:
            return 0
        
        # Convert to grayscale for Haar Cascade
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Detect faces with more sensitive parameters
        # scaleFactor=1.1 (instead of 1.3) is much more sensitive
        # minNeighbors=4 (instead of 5) allows for slightly weaker detections
        faces = face_cascade.detectMultiScale(
            gray, 
            scaleFactor=1.1, 
            minNeighbors=4,
            minSize=(30, 30)
        )
        return len(faces)
    except Exception as e:
        print(f"Face detection error: {e}")
    return 0

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
    let parentDoc;
    try {{
        parentDoc = window.parent.document;
    }} catch (e) {{
        console.warn("Cross-origin restriction: Cannot access parent document.");
        parentDoc = document; // Fallback to current iframe document
    }}
    
    const clickButton = (btnText) => {{
        try {{
            const buttons = Array.from(parentDoc.querySelectorAll('button'));
            const btn = buttons.find(b => b.innerText.includes(btnText));
            if (btn) btn.click();
        }} catch(e) {{}}
    }};
    
    // 1. Detect tab switching (Attach to both parent and current window for robustness)
    let visibilityTimeout;
    const handleVisibilityChange = () => {{
        const isHidden = (parentDoc && parentDoc !== document) ? parentDoc.hidden : document.hidden;
        
        if (isHidden) {{
            // Wait 500ms to ensure it's a real browser tab switch, not just a Streamlit React UI flicker
            visibilityTimeout = setTimeout(() => {{
                const stillHidden = (parentDoc && parentDoc !== document) ? parentDoc.hidden : document.hidden;
                if (stillHidden) {{
                    console.log("Tab switch confirmed. Terminating interview.");
                    try {{ alert("WARNING: Tab switching detected! Your interview is completely terminated and evaluated."); }} catch(e) {{}}
                    clickButton('TAB_SWITCH_TERMINATE');
                }}
            }}, 500);
        }} else {{
            clearTimeout(visibilityTimeout);
        }}
    }};
    
    // Delay attaching the event listener to avoid false positives when the iframe first loads
    setTimeout(() => {{
        document.addEventListener("visibilitychange", handleVisibilityChange);
        if (parentDoc && parentDoc !== document) {{
            parentDoc.addEventListener("visibilitychange", handleVisibilityChange);
        }}
    }}, 1000);
    
    // 2. Detect Escape key or Fullscreen exit
    const handleEscViolation = () => {{
        clickButton('ESC_PRESSED_TERMINATE');
    }};

    const handleKeyDown = (event) => {{
        if (event.key === "Escape" || event.keyCode === 27) {{
            handleEscViolation();
        }}
    }};

    window.addEventListener("keydown", handleKeyDown, true);
    document.addEventListener("keydown", handleKeyDown, true);
    if (parentDoc && parentDoc !== document) {{
        parentDoc.addEventListener("keydown", handleKeyDown, true);
        
        parentDoc.addEventListener("fullscreenchange", function() {{
            if (!parentDoc.fullscreenElement) {{
                handleEscViolation();
            }}
        }});
    }}

    // 3. Hide the secret buttons visually using JS (Retry mechanism)
    let attempts = 0;
    const hideInterval = setInterval(() => {{
        if (!parentDoc) return;
        const buttons = Array.from(parentDoc.querySelectorAll('button'));
        const tabBtn = buttons.find(b => b.innerText.includes('TAB_SWITCH_TERMINATE'));
        const escBtn = buttons.find(b => b.innerText.includes('ESC_PRESSED_TERMINATE'));
        
        if (tabBtn) tabBtn.style.display = 'none';
        if (escBtn) escBtn.style.display = 'none';
        
        if (tabBtn && escBtn) {{
            clearInterval(hideInterval);
            
            // Fullscreen logic
            const fsBtn = buttons.find(b => b.innerText.includes('Enter Full Screen'));
            if (fsBtn) {{
                fsBtn.addEventListener('click', () => {{
                    if (parentDoc.documentElement.requestFullscreen) {{
                        parentDoc.documentElement.requestFullscreen().catch(e => console.log(e));
                    }}
                }});
            }}
        }}
        
        attempts++;
        if (attempts > 20) clearInterval(hideInterval); // Stop trying after 10 seconds
    }}, 500);

    {timer_script}
    </script>
    """
    st.components.v1.html(js_code, height=0)

def check_permissions():
    st.markdown("### 🛡️ Mandatory Media Permissions")
    st.markdown("To ensure interview integrity and enable voice features, we require access to your **Camera** and **Microphone**.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 1. Camera Check")
        cam_check = st.camera_input("Please capture a test photo to verify camera access", key="perm_cam")
    
    with col2:
        st.markdown("#### 2. Microphone Check")
        st.info("Record a short test audio (even 1 second) to verify access.")
        audio_check = st.audio_input("Test Microphone 🎤", key="perm_mic")
        if audio_check:
            with st.spinner("Verifying audio..."):
                try:
                    import speech_recognition as sr
                    r = sr.Recognizer()
                    with sr.AudioFile(audio_check) as source:
                        audio_data = r.record(source)
                        # Attempt recognition to confirm audio quality
                        try:
                            r.recognize_google(audio_data)
                        except:
                            pass # Even if no speech recognized, getting data confirms mic works
                        
                        st.success("✅ Microphone access confirmed!")
                        st.session_state.mic_granted = True
                except Exception as e:
                    st.error(f"❌ Microphone error: {e}")
                    st.session_state.mic_granted = False
    
    if cam_check and st.session_state.get('mic_granted'):
        st.success("🎉 All permissions granted! You can now proceed to the interview.")
        if st.button("🚀 Enter Interview Room", key="btn_enter_room", type="primary", use_container_width=True):
            st.session_state.permissions_confirmed = True
            st.rerun()
            
        js_code = """
        <script>
            const parentDoc = window.parent.document;
            const buttons = Array.from(parentDoc.querySelectorAll('button'));
            const enterBtn = buttons.find(b => b.innerText.includes('Enter Interview Room'));
            if (enterBtn && !enterBtn.dataset.fullscreenAttached) {
                enterBtn.dataset.fullscreenAttached = 'true';
                enterBtn.addEventListener('click', () => {
                    if (parentDoc.documentElement.requestFullscreen) {
                        parentDoc.documentElement.requestFullscreen().catch(e => console.log(e));
                    }
                });
            }
        </script>
        """
        st.components.v1.html(js_code, height=0)
    elif not cam_check:
        st.warning("⚠️ Camera access is required to proceed.")
    elif not st.session_state.get('mic_granted'):
        st.warning("⚠️ Microphone access is required to proceed.")

def end_interview(violation_msg=None):
    # Finalize the transcript with the last answered question if it exists
    if 'current_question' in st.session_state or 'current_hr_question' in st.session_state:
        q = st.session_state.get('current_question') or st.session_state.get('current_hr_question')
        # Only add if it wasn't already added (we use a flag to prevent duplicates if user clicks End after Next)
        if q and not st.session_state.get('last_q_added', False):
             ans = violation_msg or st.session_state.get('code_answer') or st.session_state.get('answer_text', 'No answer provided.')
             st.session_state.interview_transcript.append({"question": q, "answer": ans})
             st.session_state.last_q_added = True

    st.session_state.interview_data = {
        "transcript": st.session_state.interview_transcript,
        "round": st.session_state.get('interview_round', 'General')
    }
    st.session_state.current_page = 'feedback'
    st.rerun()

def display_interview_history():
    if st.session_state.interview_transcript:
        st.markdown("### 📜 Interview History")
        for i, entry in enumerate(st.session_state.interview_transcript):
            with st.chat_message("assistant"):
                st.markdown(f"**Question {i+1}:** {entry['question']}")
            with st.chat_message("user"):
                if "Technical" in st.session_state.get('interview_round', ''):
                    st.code(entry['answer'])
                else:
                    st.markdown(entry['answer'])
        st.markdown("---")

def render_technical_round():
    display_interview_history()
    
    # Split layout: Question/Editor on left, small camera on the right
    col_main, col_cam = st.columns([3, 1])
    
    with col_main:
        st.markdown(f"### Technical Round - Question {len(st.session_state.interview_transcript) + 1}")
        
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
        
        col_lang, col_run = st.columns([2, 1])
        with col_lang:
            languages = ["python", "javascript", "c_cpp", "java", "csharp", "c"]
            selected_lang = st.selectbox("Select Language", options=languages, index=0)
        
        code = st_ace(
            value=st.session_state.code_answer,
            language=selected_lang,
            theme="monokai",
            keybinding="vscode",
            font_size=16,
            tab_size=4,
            height=400
        )
        
        if code != st.session_state.code_answer:
            st.session_state.code_answer = code

        with col_run:
            st.write("") # Spacer
            st.write("") # Spacer
            if st.button("▶️ Run Code", use_container_width=True):
                # Basic validation: ensure code isn't just the placeholder or empty
                stripped_code = code.strip()
                placeholder = "# Write your code here"
                if not stripped_code or stripped_code == placeholder or (stripped_code.startswith(placeholder) and len(stripped_code) < len(placeholder) + 5):
                     st.warning("⚠️ Please write some code before running.")
                else:
                    with st.spinner("Executing..."):
                        result = execute_code(selected_lang, code)
                        if "error" in result:
                            st.error(f"Execution Error: {result['error']}")
                        else:
                            st.session_state.code_output = result
        
        if "code_output" in st.session_state:
            res = st.session_state.code_output
            if isinstance(res, dict) and "error" in res:
                st.error(f"❌ {res['error']}")
            elif isinstance(res, dict):
                if res.get("code", 0) != 0:
                    st.error(f"⚠️ Execution Failed (Exit Code {res['code']})")
                    if res.get("stderr"):
                        st.markdown("**Error details:**")
                        st.code(res.get("stderr", ""), language="text")
                    if res.get("stdout"):
                        st.markdown("**Output (if any):**")
                        st.code(res.get("stdout", ""), language="text")
                else:
                    output = res.get("output", "").strip()
                    if not output:
                        st.info("✅ Execution Successful (No output produced)")
                    else:
                        st.success("✅ Execution Successful")
                        st.code(output, language="text")
            else:
                # Fallback for old state format
                st.markdown("#### Execution Output")
                st.code(res, language="text")
            
    with col_cam:
        # Consistency: Tech round now also has webcam proctoring
        img = st.camera_input("Proctoring Feed", key="tech_cam_input")
        if img:
            faces = count_faces(img)
            if faces == 1:
                st.success("✅ Proctoring Active: Face Detected")
            elif faces == 0:
                st.warning("⚠️ Face Not Detected")
            else:
                st.error(f"🚨 {faces} Faces Detected")

            if (faces > 1):
                msg = f"SYSTEM TERMINATION: Multiple people detected ({faces} faces) in the camera feed. This is a major cheating violation."
                st.error(f"🚨 Multiple people detected ({faces})! The interview is being terminated for cheating violation.")
                import time
                time.sleep(3)
                end_interview(violation_msg=msg)
        
    
    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        if st.button("➕ Ask Next Question", key="btn_next_tech", use_container_width=True):
            st.session_state.interview_transcript.append({
                "question": st.session_state.current_question,
                "answer": st.session_state.code_answer
            })
            # Clear current question to trigger new generation
            del st.session_state.current_question
            del st.session_state.code_answer
            if "code_output" in st.session_state: del st.session_state.code_output
            st.rerun()
            
    with col_btn2:
        if st.button("🏁 End Interview & Get Feedback", key="btn_end_tech", type="primary", use_container_width=True):
            end_interview()

def render_hr_round():
    display_interview_history()
    st.markdown(f"### HR / Behavioral Round - Question {len(st.session_state.interview_transcript) + 1}")
    
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
                except sr.RequestError:
                    st.error("🚨 Speech API connection error. Please check your internet.")
                except sr.UnknownValueError:
                    st.warning("Could not understand audio. Try speaking clearer.")
                except Exception as e:
                    st.error(f"🚨 Microphone Error: {e}. Please ensure permissions are granted.")
                    
        st.markdown("#### Your Final Answer")
        # Auto-fills with voice transcription if provided, otherwise blank for typing
        answer_text = st.text_area("Type or edit your answer here...", value=transcribed_text, height=150)
        st.session_state.answer_text = answer_text
        
    with col_cam:
        img = st.camera_input("Webcam Feed", key="hr_cam_input")
        if img:
            faces = count_faces(img)
            if faces == 1:
                st.success("✅ Proctoring Active: Face Detected")
            elif faces == 0:
                st.warning("⚠️ Face Not Detected")
            else:
                st.error(f"🚨 {faces} Faces Detected")

            if (faces > 1):
                msg = f"SYSTEM TERMINATION: Multiple people detected ({faces} faces) in the camera feed. This is a major cheating violation."
                st.error(f"🚨 Multiple people detected ({faces})! The interview is being terminated for cheating violation.")
                import time
                time.sleep(3)
                end_interview(violation_msg=msg)
    
    
    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        if st.button("➕ Ask Next Question", key="btn_next_hr", use_container_width=True):
            st.session_state.interview_transcript.append({
                "question": st.session_state.current_hr_question,
                "answer": st.session_state.answer_text
            })
            del st.session_state.current_hr_question
            del st.session_state.answer_text
            st.rerun()
            
    with col_btn2:
        if st.button("🏁 End Interview & Get Feedback", key="btn_end_hr", type="primary", use_container_width=True):
            end_interview()

def render_interview():
    if 'interview_transcript' not in st.session_state:
        st.session_state.interview_transcript = []
    
    # Reset the flag that prevents double adding on End Interview
    st.session_state.last_q_added = False

    st.markdown("""
        <style>
        div[data-testid="stButton"] button:contains("TAB_SWITCH_TERMINATE"),
        div[data-testid="stButton"] button:contains("ESC_PRESSED_TERMINATE") {
            display: none !important;
        }
        </style>
    """, unsafe_allow_html=True)

    if not st.session_state.get('permissions_confirmed'):
        st.warning("⚠️ Please complete the verification process first.")
        if st.button("Go to Verification"):
            st.session_state.current_page = 'verification'
            st.rerun()
        return

    # Secret buttons that Javascript clicks
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

    if remaining_seconds is not None and remaining_seconds <= 0:
        msg = "TIME EXPIRED: Candidate did not submit in time."
        st.error("⏳ Time is up! Terminating interview...")
        import time
        time.sleep(2)
        end_interview(violation_msg=msg)

    inject_tab_switching_js(remaining_seconds)
    
    st.markdown(f"<div style='display: flex; justify-content: space-between; align-items: center;'><h2>🔴 {role} ({round_type})</h2>{timer_html}</div>", unsafe_allow_html=True)
    st.markdown("---")
    
    col_fs, col_end = st.columns([4, 1])
    with col_fs:
        st.button("🔲 Enter Full Screen", key="btn_fullscreen", type="primary", use_container_width=True)
    with col_end:
        if st.button("End Early", key="btn_end_early", type="secondary", use_container_width=True):
            msg = "Candidate ended interview manually."
            if "start_time" in st.session_state: del st.session_state.start_time
            end_interview(violation_msg=msg)
            st.rerun()
            
    # Secret buttons that Javascript clicks
    if st.button("TAB_SWITCH_TERMINATE", key="btn_tab_violation", type="secondary"):
        msg = "SYSTEM VIOLATION: Candidate completely switched tabs during the live interview. Evaluate them strictly. Note this massive negative cheating behavioral flag."
        end_interview(violation_msg=msg)

    if st.button("ESC_PRESSED_TERMINATE", key="btn_esc_violation", type="secondary"):
        if 'esc_count' not in st.session_state:
            st.session_state.esc_count = 0
        st.session_state.esc_count += 1
        
        if st.session_state.esc_count == 1:
            st.warning("⚠️ WARNING: Escape key pressed! This is your first warning. Pressing it again will terminate the interview immediately.")
        else:
            msg = f"SYSTEM TERMINATION: Escape key pressed twice (Count: {st.session_state.esc_count}). Cheating violation/Attempt to exit restricted environment."
            st.error("🚨 Escape key pressed again! Terminating interview due to strictness violation.")
            import time
            time.sleep(3)
            end_interview(violation_msg=msg)
            
    if "Technical" in round_type:
        render_technical_round()
    else:
        render_hr_round()

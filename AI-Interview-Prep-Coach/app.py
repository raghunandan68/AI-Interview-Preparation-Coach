import streamlit as st
import time
import sys
import io
import subprocess
import tempfile
import os
import re
from google import genai
from groq import Groq
from streamlit_ace import st_ace
from prompts import (
    interview_question_prompt,
    technical_coding_prompt,
    coding_evaluation_prompt,
    skill_gap_analysis_prompt
)

# ---------------- CONFIG ----------------
st.set_page_config(page_title="AI Interview Coach", layout="centered")

st.title("🎯 AI Interview Preparation Coach")
st.caption("Real interviews • Coding rounds • Live code editor")

# ---------------- SESSION STATE ----------------
defaults = {
    "question_number": 1,
    "conversation": [],
    "current_question": None,
    "scores": [],
    "start_time": None,
    "final_score": False,
    "interview_started": False,
    "interview_active": False,
    "skill_gap_analysis": None
}

for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ---------------- API SETUP ----------------
gemini_key = st.secrets.get("GEMINI_API_KEY")
groq_key = st.secrets.get("GROQ_API_KEY")

if not gemini_key and not groq_key:
    st.error("No API keys found in secrets.toml. Please add GEMINI_API_KEY or GROQ_API_KEY.")
    st.stop()

# Initialize Clients
gemini_client = genai.Client(api_key=gemini_key) if gemini_key else None
groq_client = Groq(api_key=groq_key) if groq_key and groq_key != "paste_your_groq_key_here" else None

def call_llm_with_retry(prompt, purpose="performance", max_retries=3):
    """Calls LLM with automatic role-based assignment and provider fallback."""
    
    # Logic: Performance (Groq first) vs Analysis (Gemini first)
    if purpose == "analysis":
        providers = [
            ("Gemini", "gemini-2.0-flash"), 
            ("Groq", "llama-3.3-70b-versatile")
        ]
    else: # performance
        providers = [
            ("Groq", "llama-3.3-70b-versatile"),
            ("Gemini", "gemini-2.0-flash")
        ]

    for current_provider, model_name in providers:
        # Skip if provider not initialized
        if current_provider == "Gemini" and not gemini_client: continue
        if current_provider == "Groq" and not groq_client: continue

        for attempt in range(max_retries):
            try:
                if current_provider == "Gemini":
                    response = gemini_client.models.generate_content(
                        model=model_name,
                        contents=prompt
                    )
                    return response
                elif current_provider == "Groq":
                    response = groq_client.chat.completions.create(
                        model=model_name,
                        messages=[{"role": "user", "content": prompt}]
                    )
                    # Wrap Groq response to match Gemini's .text attribute
                    class WrappedResponse:
                        def __init__(self, text): self.text = text
                    return WrappedResponse(response.choices[0].message.content)
            
            except Exception as e:
                error_msg = str(e).lower()
                is_rate_limit = any(x in error_msg for x in ["rate limit", "429", "quota", "resource_exhausted"])
                
                if is_rate_limit:
                    if attempt < max_retries - 1:
                        time.sleep((attempt + 1) * 2)
                    else:
                        break # Try next provider
                else:
                    st.error(f"🚨 {current_provider} API Error: {str(e)}")
                    st.stop()
                    
    st.error("🚨 All API providers are currently rate-limited. Please wait 60 seconds.")
    st.stop()

# ---------------- SIDEBAR ----------------
st.sidebar.header("🛠 Interview Settings")

# Hidden auto-selection (Removing manual choice as requested)
job_role = st.sidebar.selectbox(
    "Job Role",
    ["Cloud Engineer", "Software Developer", "Data Scientist", "DevOps Engineer", "Custom"]
)

if job_role == "Custom":
    job_role = st.sidebar.text_input("Enter Job Role")

interview_type = st.sidebar.selectbox(
    "Interview Type",
    ["HR", "Behavioral", "Technical"]
)

difficulty = None
timer_limit = None
language = None

if interview_type == "Technical":
    difficulty = st.sidebar.selectbox("DSA Difficulty", ["Easy", "Medium", "Hard"])
    timer_limit = st.sidebar.slider("Time Limit (minutes)", 5, 45, 20)

    language = st.sidebar.selectbox(
        "Programming Language",
        ["Python", "C", "C++", "Java", "C#", "JavaScript"]
    )

if st.sidebar.button("🔄 Reset Interview"):
    for k in defaults:
        st.session_state[k] = defaults[k]
    st.rerun()

# ---------------- MAIN ACTION AREA ----------------
if not st.session_state.interview_started and not st.session_state.final_score:
    st.info("Configure your interview settings in the sidebar, then click Start Interview.")
    if st.button("🚀 Start Interview", use_container_width=True):
        st.session_state.interview_started = True
        st.session_state.interview_active = True
        st.rerun()

elif st.session_state.interview_active:
    st.success("✅ Interview is currently active.")
    if st.button("🛑 Stop Interview", use_container_width=True, type="primary"):
        if len(st.session_state.scores) == 0:
            st.error("⚠️ Please attempt and submit at least one question before ending the interview to receive a scorecard!")
        else:
            st.session_state.interview_active = False
            st.session_state.final_score = True
            st.rerun()

    # ---------------- ASK QUESTION ----------------
    if st.button("🧠 Ask Next Question") and not st.session_state.current_question:
        history = "\n".join([f"{s}: {m}" for s, m in st.session_state.conversation])
        
        if interview_type == "Technical":
            prompt = technical_coding_prompt(
                job_role, difficulty, st.session_state.question_number, history
            )
            st.session_state.start_time = time.time()
        else:
            prompt = interview_question_prompt(
                job_role, interview_type, st.session_state.question_number, history
            )
            
        with st.spinner("Generating question..."):
            response = call_llm_with_retry(
                prompt=prompt,
                purpose="performance"
            )
            
            question = response.text
            st.session_state.current_question = question
            st.session_state.conversation.append(("Interviewer", question))
            st.session_state.question_number += 1
            st.rerun()

# ---------------- DISPLAY CONVERSATION ----------------
st.subheader("💬 Interview Conversation")

for speaker, msg in st.session_state.conversation:
    icon = "🤖" if speaker == "Interviewer" else "🧑"
    st.markdown(f"**{icon} {speaker}:** {msg}")

# ---------------- ANSWER INPUT ----------------
if st.session_state.current_question:

    if interview_type == "Technical":
        elapsed = int(time.time() - st.session_state.start_time)
        remaining = max(0, timer_limit * 60 - elapsed)
        
        # Inject CSS to force solid dark background for the ace editor container
        st.markdown(
            """
            <style>
            .st-ace {
                background-color: #272822 !important;
            }
            .timer-container {
                font-size: 1.2rem;
                font-weight: bold;
                padding: 10px;
                border-radius: 5px;
                margin-bottom: 10px;
                display: inline-block;
            }
            </style>
            """,
            unsafe_allow_html=True
        )

        # Client-side HTML/JS Timer to prevent Streamlit Ace transparency reloading bug
        timer_html = f"""
        <div id="countdown-timer" class="timer-container" style="background-color: #fca5a5; color: #7f1d1d; border: 1px solid #f87171;">
            ⏳ Time Remaining: <span id="time-display">{remaining//60}:{remaining%60:02d}</span>
        </div>
        
        <script>
            var remaining = {remaining};
            var display = document.getElementById('time-display');
            var container = document.getElementById('countdown-timer');
            
            var timer = setInterval(function() {{
                if (remaining <= 0) {{
                    clearInterval(timer);
                    container.innerHTML = "⏰ Time's up! Click Submit Answer below.";
                    return;
                }}
                remaining--;
                
                var minutes = Math.floor(remaining / 60);
                var seconds = remaining % 60;
                display.innerHTML = minutes + ":" + (seconds < 10 ? "0" : "") + seconds;
                
                if (remaining <= 60) {{
                    container.style.backgroundColor = "#fecaca";
                    container.style.color = "#991b1b";
                }} else {{
                    container.style.backgroundColor = "#fef3c7";
                    container.style.color = "#92400e";
                    container.style.border = "1px solid #fcd34d";
                }}
            }}, 1000);
        </script>
        """
        st.components.v1.html(timer_html, height=60)

        code = st_ace(
            language=language.lower(),
            theme="monokai",
            height=320,
            font_size=14,
            show_gutter=True,
            wrap=True,
            auto_update=False # Prevent frequent reruns while typing
        )
        
        # We handle submission strictly on button click since JS can't natively force a Streamlit Python callback directly easily without external components.
        auto_submit = False
        if remaining <= 0:
            st.error("⏰ Time's up! Please click Submit to evaluate your final code.")
            
        col1, col2 = st.columns([1, 1])
        run_code = col1.button("▶️ Run Code", use_container_width=True)
        submit_answer = col2.button("✅ Submit Answer", type="primary", use_container_width=True)
        
        # Execute User Code Locally
        if run_code and code:
            st.markdown("### 🖥️ Output Terminal")
            with st.expander("Terminal Logs", expanded=True):
                if language == "Python":
                    # Run Python natively using exec() and capture stdout
                    old_stdout = sys.stdout
                    redirected_output = sys.stdout = io.StringIO()
                    try:
                        exec(code, {})
                        output = redirected_output.getvalue()
                        if not output: output = "Code executed successfully. No output."
                        st.code(output, language="bash")
                    except Exception as e:
                        st.error(f"Error:\n{str(e)}")
                    finally:
                        sys.stdout = old_stdout
                else:
                    # Multi-language execution via Subprocess
                    with tempfile.TemporaryDirectory() as temp_dir:
                        try:
                            if language == "JavaScript":
                                file_path = os.path.join(temp_dir, "main.js")
                                with open(file_path, "w") as f: f.write(code)
                                result = subprocess.run(["node", file_path], capture_output=True, text=True, timeout=10)
                            
                            elif language == "C":
                                file_path = os.path.join(temp_dir, "main.c")
                                exe_path = os.path.join(temp_dir, "main.exe")
                                with open(file_path, "w") as f: f.write(code)
                                compile_res = subprocess.run(["gcc", file_path, "-o", exe_path], capture_output=True, text=True)
                                if compile_res.returncode == 0:
                                     result = subprocess.run([exe_path], capture_output=True, text=True, timeout=10)
                                else:
                                    result = compile_res
                                    
                            elif language == "C++":
                                file_path = os.path.join(temp_dir, "main.cpp")
                                exe_path = os.path.join(temp_dir, "main.exe")
                                with open(file_path, "w") as f: f.write(code)
                                compile_res = subprocess.run(["g++", file_path, "-o", exe_path], capture_output=True, text=True)
                                if compile_res.returncode == 0:
                                    result = subprocess.run([exe_path], capture_output=True, text=True, timeout=10)
                                else:
                                    result = compile_res
                                    
                            elif language == "Java":
                                file_path = os.path.join(temp_dir, "Main.java")
                                with open(file_path, "w") as f: f.write(code)
                                result = subprocess.run(["java", file_path], capture_output=True, text=True, timeout=10)
                                
                            elif language == "C#":
                                file_path = os.path.join(temp_dir, "main.cs")
                                exe_path = os.path.join(temp_dir, "main.exe")
                                with open(file_path, "w") as f: f.write(code)
                                compile_res = subprocess.run(["csc", "/nologo", f"/out:{exe_path}", file_path], capture_output=True, text=True)
                                if compile_res.returncode == 0:
                                    result = subprocess.run([exe_path], capture_output=True, text=True, timeout=10)
                                else:
                                    result = compile_res
                            
                            output = result.stdout if result.returncode == 0 else result.stderr
                            if not output: output = "Code executed successfully. No output."
                            
                            if result.returncode == 0:
                                st.code(output, language="bash")
                            else:
                                st.error(f"Error/Compilation Failed:\n{output}")
                                
                        except FileNotFoundError:
                            st.warning(f"Compiler for {language} is not installed or not found in system PATH.")
                        except subprocess.TimeoutExpired:
                            st.error("Execution Time Limit Exceeded (10s timeout).")
                        except Exception as e:
                            st.error(f"Execution Error: {str(e)}")

    else:
        auto_submit = False
        code = st.text_area("✍️ Your Answer", height=150)
        submit_answer = st.button("✅ Submit Answer", type="primary")

    if (submit_answer or auto_submit) and code:
        st.session_state.conversation.append(("You", code))

        if interview_type == "Technical":
            eval_prompt = coding_evaluation_prompt(
                job_role,
                st.session_state.current_question,
                code,
                language,
                difficulty
            )
        else:
            eval_prompt = f"""
You are an interview coach.

Evaluate the answer.

Provide:
1. Score out of 10
2. Strengths
3. Improvements
4. Improved sample answer
"""

        feedback = call_llm_with_retry(
            prompt=eval_prompt,
            purpose="performance"
        )

        feedback_text = feedback.text
        st.markdown("### 📊 Feedback")
        st.markdown(feedback_text)

        # Extract score securely using Regex
        score = 7
        # Look for explicit fractions like "8/10" or "8 out of 10"
        match = re.search(r'\b([0-9]|10)\s*(?:/|out\s*of)\s*10', feedback_text.lower())
        if match:
            score = int(match.group(1))
        else:
            # Fallback line-by-line parsing
            for line in feedback_text.splitlines():
                if "score" in line.lower():
                    # Remove list index prefixes (e.g. "1. " or "2. ") so we don't extract "2" from "2. Score"
                    clean_line = re.sub(r'^\s*\d+\.\s*', '', line)
                    nums = [int(s) for s in re.findall(r'\b\d+\b', clean_line)]
                    if nums:
                        score = min(10, nums[0]) # Cap at 10, extract first number
                        break

        st.session_state.scores.append(score)
        st.session_state.current_question = None
        st.rerun()

# ---------------- FINAL SCORECARD ----------------
if st.session_state.final_score:
    st.subheader("🏁 Final Interview Scorecard")

    total = len(st.session_state.scores)
    avg = sum(st.session_state.scores) / total

    st.metric("Questions Attempted", total)
    st.metric("Average Score", f"{avg:.1f}/10")

    if avg >= 8:
        st.success("🌟 Excellent – Interview Ready!")
    elif avg >= 6:
        st.warning("👍 Good – Needs minor improvement")
    else:
        st.error("📚 Needs more practice")

    st.markdown("### 📈 Per Question Scores")
    for i, s in enumerate(st.session_state.scores, 1):
        st.write(f"Question {i}: {s}/10")
        
    st.divider()
    
    st.subheader("🧐 Comprehensive Skill Gap Analysis")
    
    if st.session_state.skill_gap_analysis is None:
        if not st.session_state.conversation:
            st.info("No questions answered to analyze.")
        else:
            with st.spinner("Generating detailed Skill Gap Analysis based on your interview..."):
                history = "\n".join([f"{s}: {m}" for s, m in st.session_state.conversation])
                scores_str = ", ".join(map(str, st.session_state.scores))
                
                analysis_prompt = skill_gap_analysis_prompt(
                    job_role,
                    interview_type,
                    history,
                    scores_str
                )
                
                analysis_response = call_llm_with_retry(
                    prompt=analysis_prompt,
                    purpose="analysis"
                )
                
                st.session_state.skill_gap_analysis = analysis_response.text
                st.rerun()
                
    if st.session_state.skill_gap_analysis:
        st.markdown(st.session_state.skill_gap_analysis)

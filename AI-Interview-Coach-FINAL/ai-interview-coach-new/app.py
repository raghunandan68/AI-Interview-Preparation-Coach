import streamlit as st
import time
import sys
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
    behavioral_evaluation_prompt,
    skill_gap_analysis_prompt
)

# ════════════════════════════════════════════
#  PAGE CONFIG
# ════════════════════════════════════════════
st.set_page_config(
    page_title="AI Interview Coach",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ════════════════════════════════════════════
#  GLOBAL STYLES
# ════════════════════════════════════════════
st.markdown("""
<style>
/* ── App background ── */
.stApp { background-color: #0f1117; }

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #1a1f2e 0%, #0f1117 100%);
    border-right: 1px solid #2d3748;
}

/* ── Main header ── */
.main-header {
    background: linear-gradient(135deg, #1e3a5f 0%, #2d6a9f 50%, #1e3a5f 100%);
    border-radius: 16px;
    padding: 28px 36px;
    margin-bottom: 24px;
    border: 1px solid #2d6a9f;
    box-shadow: 0 4px 24px rgba(45, 106, 159, 0.25);
}
.main-header h1 { color: #ffffff; margin: 0; font-size: 2rem; font-weight: 700; }
.main-header p  { color: #cce0f0; margin: 6px 0 0 0; font-size: 0.95rem; }

/* ── Status badges ── */
.badge-active {
    display: inline-block;
    background: #0d4f2f;
    color: #4ade80;
    border: 1px solid #16a34a;
    border-radius: 20px;
    padding: 4px 14px;
    font-size: 0.8rem;
    font-weight: 600;
}
.badge-stopped {
    display: inline-block;
    background: #4a1942;
    color: #f472b6;
    border: 1px solid #9d174d;
    border-radius: 20px;
    padding: 4px 14px;
    font-size: 0.8rem;
    font-weight: 600;
}

/* ── Chat bubbles ── */
.chat-interviewer {
    background: #1e2d42;
    border: 1px solid #2d4a6b;
    border-radius: 0 14px 14px 14px;
    padding: 14px 18px;
    margin: 8px 60px 8px 0;
    color: #e2e8f0;
    font-size: 0.92rem;
    line-height: 1.6;
}
.chat-you {
    background: #1a2f1a;
    border: 1px solid #2d5a2d;
    border-radius: 14px 0 14px 14px;
    padding: 14px 18px;
    margin: 8px 0 8px 60px;
    color: #e2e8f0;
    font-size: 0.92rem;
    line-height: 1.6;
}
.chat-label-interviewer { color: #60a5fa; font-size: 0.78rem; font-weight: 600; margin-bottom: 4px; }
.chat-label-you         { color: #4ade80; font-size: 0.78rem; font-weight: 600; margin-bottom: 4px; text-align: right; }

/* ── Score card ── */
.score-card {
    background: #1a1f2e;
    border: 1px solid #2d3748;
    border-radius: 12px;
    padding: 16px;
    text-align: center;
}
.score-number { font-size: 2.2rem; font-weight: 800; }
.score-label  { color: #ffffff; font-size: 0.8rem; margin-top: 4px; }

/* ── Section headers ── */
.section-title {
    color: #60a5fa;
    font-size: 1.1rem;
    font-weight: 700;
    border-bottom: 2px solid #1e3a5f;
    padding-bottom: 8px;
    margin: 20px 0 14px 0;
}

/* ── Landing cards ── */
.feature-card {
    background: #1a1f2e;
    border: 1px solid #2d3748;
    border-radius: 12px;
    padding: 20px;
    height: 100%;
}
.feature-card h4 { color: #60a5fa; margin: 0 0 8px 0; font-size: 1rem; }
.feature-card p  { color: #ffffff; margin: 0; font-size: 0.87rem; line-height: 1.5; }

/* ── Provider pill ── */
.provider-pill {
    display: inline-block;
    background: #1e3a5f;
    color: #93c5fd;
    border: 1px solid #2d6a9f;
    border-radius: 20px;
    padding: 3px 12px;
    font-size: 0.78rem;
    font-weight: 600;
}

/* ── White text only on dark background areas ── */
.stApp .stMarkdown p,
.stApp .stMarkdown li,
.stApp .stMarkdown h1,
.stApp .stMarkdown h2,
.stApp .stMarkdown h3,
.stApp .stMarkdown h4,
.stApp .stMarkdown span,
.stApp .stMarkdown td,
.stApp .stMarkdown th {
    color: #ffffff !important;
}

/* Metric values and labels */
[data-testid="stMetricValue"],
[data-testid="stMetricLabel"],
[data-testid="stMetricDelta"] {
    color: #ffffff !important;
}

/* Sidebar labels and text only */
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] .stMarkdown p,
[data-testid="stSidebar"] .stMarkdown span {
    color: #ffffff !important;
}

/* Text area input — white text on dark bg */
.stTextArea textarea {
    color: #ffffff !important;
    background-color: #1a1f2e !important;
    border: 1px solid #2d3748 !important;
}

/* Slider label */
.stSlider label {
    color: #ffffff !important;
}

/* Intentional coloured elements */
.chat-label-interviewer { color: #60a5fa !important; }
.chat-label-you         { color: #4ade80 !important; }
.section-title          { color: #60a5fa !important; }
.feature-card h4        { color: #60a5fa !important; }
.badge-active           { color: #4ade80 !important; }
.main-header p          { color: #cce0f0 !important; }
a                       { color: #60a5fa !important; }

/* ── ALL buttons — white background, black text, visible ── */
.stButton > button {
    border-radius: 8px;
    font-weight: 600;
    transition: all 0.2s;
    background-color: #ffffff !important;
    color: #000000 !important;
    border: 1px solid #2d6a9f !important;
}
.stButton > button:hover {
    background-color: #dbeafe !important;
    color: #000000 !important;
}

/* ── Sidebar Reset button — dark blue override ── */
[data-testid="stSidebar"] .stButton > button {
    background-color: #1e3a5f !important;
    color: #ffffff !important;
    border: 1px solid #2d6a9f !important;
}
[data-testid="stSidebar"] .stButton > button:hover {
    background-color: #2d6a9f !important;
    color: #ffffff !important;
}

/* ── Metric container ── */
div[data-testid="metric-container"] {
    background: #1a1f2e;
    border: 1px solid #2d3748;
    border-radius: 10px;
    padding: 12px 16px;
}
div[data-testid="metric-container"] * {
    color: #ffffff !important;
}

/* ── Selectbox / dropdown — black text inside the white input box ── */
[data-testid="stSelectbox"] > div > div,
[data-testid="stSelectbox"] > div > div > div,
[data-testid="stSelectbox"] input,
.stSelectbox [class*="singleValue"],
.stSelectbox [class*="placeholder"],
div[data-baseweb="select"] span,
div[data-baseweb="select"] div {
    color: #000000 !important;
}

/* Dropdown menu list items */
[data-baseweb="popover"] li,
[data-baseweb="popover"] ul,
[data-baseweb="popover"] div,
[data-baseweb="menu"] div,
[data-baseweb="menu"] li {
    color: #000000 !important;
    background-color: #ffffff !important;
}

/* Highlighted / hovered option */
[data-baseweb="menu"] [aria-selected="true"],
[data-baseweb="menu"] li:hover {
    background-color: #e8f0fe !important;
    color: #000000 !important;
}

/* ── Hide Deploy button ── */
[data-testid="stToolbar"],
[data-testid="stDecoration"],
.stDeployButton,
button[kind="deployButton"],
[data-testid="stAppDeployButton"] {
    display: none !important;
    visibility: hidden !important;
}

/* Hide hamburger menu and footer */
#MainMenu { visibility: hidden !important; }
footer    { visibility: hidden !important; }

/* ── Hide __time_expired__ button by key ── */
[data-testid="stButton"]:has(button[data-testid="time_expired_btn"]) {
    display: none !important;
    visibility: hidden !important;
    height: 0 !important;
    overflow: hidden !important;
}
</style>
""", unsafe_allow_html=True)

# ════════════════════════════════════════════
#  SESSION STATE
# ════════════════════════════════════════════
defaults = {
    "question_number": 1,
    "conversation": [],
    "current_question": None,
    "scores": [],
    "start_time": None,
    "final_score": False,
    "interview_started": False,
    "interview_active": False,
    "skill_gap_analysis": None,
    "active_provider": "—"
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ════════════════════════════════════════════
#  API KEY VALIDATION & CLIENT SETUP
# ════════════════════════════════════════════
PLACEHOLDER_PATTERNS = {
    "", "your_gemini_key_here", "your_groq_key_here",
    "paste_your_groq_key_here", "paste_your_gemini_key_here"
}

def is_valid_key(key):
    return bool(key) and key.strip().lower() not in PLACEHOLDER_PATTERNS

gemini_key = st.secrets.get("GEMINI_API_KEY", "")
groq_key   = st.secrets.get("GROQ_API_KEY", "")

if not is_valid_key(gemini_key) and not is_valid_key(groq_key):
    st.error("⚠️ No valid API keys found. Please add GEMINI_API_KEY or GROQ_API_KEY to `.streamlit/secrets.toml`.")
    st.stop()

gemini_client = genai.Client(api_key=gemini_key) if is_valid_key(gemini_key) else None
groq_client   = Groq(api_key=groq_key)           if is_valid_key(groq_key)   else None

# ════════════════════════════════════════════
#  LLM CALL WITH RETRY + FALLBACK
# ════════════════════════════════════════════
def call_llm_with_retry(prompt, purpose="performance", max_retries=3):
    """
    Calls LLM with automatic role-based routing and provider fallback.
    purpose='analysis'    → Gemini first (better reasoning)
    purpose='performance' → Groq first (faster response)
    """
    if purpose == "analysis":
        providers = [("Gemini", "gemini-2.0-flash"), ("Groq", "llama-3.3-70b-versatile")]
    else:
        providers = [("Groq", "llama-3.3-70b-versatile"), ("Gemini", "gemini-2.0-flash")]

    for provider_name, model_name in providers:
        if provider_name == "Gemini" and not gemini_client:
            continue
        if provider_name == "Groq" and not groq_client:
            continue

        for attempt in range(max_retries):
            try:
                if provider_name == "Gemini":
                    response = gemini_client.models.generate_content(
                        model=model_name, contents=prompt
                    )
                    st.session_state.active_provider = f"Gemini ({model_name})"
                    return response

                elif provider_name == "Groq":
                    response = groq_client.chat.completions.create(
                        model=model_name,
                        messages=[{"role": "user", "content": prompt}]
                    )
                    class WrappedResponse:
                        def __init__(self, text): self.text = text
                    st.session_state.active_provider = f"Groq ({model_name})"
                    return WrappedResponse(response.choices[0].message.content)

            except Exception as e:
                error_msg = str(e).lower()
                is_rate_limit = any(x in error_msg for x in ["rate limit", "429", "quota", "resource_exhausted"])
                if is_rate_limit:
                    if attempt < max_retries - 1:
                        time.sleep((attempt + 1) * 2)
                    else:
                        break
                else:
                    st.error(f"🚨 {provider_name} API Error: {str(e)}")
                    st.stop()

    st.error("🚨 All API providers are rate-limited. Please wait 60 seconds and try again.")
    st.stop()

# ════════════════════════════════════════════
#  SIDEBAR
# ════════════════════════════════════════════
with st.sidebar:
    st.markdown("""
    <div style='text-align:center; padding: 16px 0 8px 0;'>
        <div style='font-size:2.2rem;'>🎯</div>
        <div style='color:#60a5fa; font-weight:700; font-size:1.05rem; margin-top:4px;'>Interview Coach</div>
        <div style='color:#cccccc; font-size:0.78rem;'>AI-Powered Preparation</div>
    </div>
    <hr style='border-color:#2d3748; margin: 12px 0;'>
    """, unsafe_allow_html=True)

    st.markdown("**⚙️ Interview Settings**")

    interview_active = st.session_state.get("interview_active", False)

    if interview_active:
        # Lock all settings during active interview
        st.markdown(f"""
        <div style='background:#1a1f2e; border:1px solid #f59e0b; border-radius:8px; padding:10px 14px; margin-bottom:12px;'>
            <span style='color:#f59e0b; font-size:0.8rem; font-weight:600;'>🔒 Settings locked during interview</span>
        </div>
        """, unsafe_allow_html=True)

        job_role       = st.session_state.get("locked_job_role", "—")
        interview_type = st.session_state.get("locked_interview_type", "HR")
        difficulty     = st.session_state.get("locked_difficulty", None)
        timer_limit    = st.session_state.get("locked_timer_limit", None)
        language       = st.session_state.get("locked_language", None)

        st.markdown(f"""
        <div style='background:#1a1f2e; border:1px solid #2d3748; border-radius:8px; padding:12px 14px;'>
            <div style='color:#60a5fa; font-size:0.78rem; margin-bottom:4px;'>Job Role</div>
            <div style='color:#ffffff; font-size:0.9rem; font-weight:600;'>{job_role}</div>
            <div style='color:#60a5fa; font-size:0.78rem; margin:8px 0 4px 0;'>Interview Type</div>
            <div style='color:#ffffff; font-size:0.9rem; font-weight:600;'>{interview_type}</div>
            {"<div style='color:#60a5fa; font-size:0.78rem; margin:8px 0 4px 0;'>Difficulty</div><div style='color:#ffffff; font-size:0.9rem; font-weight:600;'>" + str(difficulty) + "</div>" if difficulty else ""}
            {"<div style='color:#60a5fa; font-size:0.78rem; margin:8px 0 4px 0;'>Time Limit</div><div style='color:#ffffff; font-size:0.9rem; font-weight:600;'>" + str(timer_limit) + " min</div>" if timer_limit else ""}
        </div>
        """, unsafe_allow_html=True)

        if interview_type == "Technical":
            st.markdown("**💻 Programming Language**")
            language = st.selectbox(
                "Programming Language",
                ["Python", "C", "C++", "Java", "C#", "JavaScript"],
                index=["Python", "C", "C++", "Java", "C#", "JavaScript"].index(
                    st.session_state.get("locked_language", "Python")
                )
            )
            st.session_state.locked_language = language

    else:
        job_role = st.selectbox(
            "Job Role",
            ["Software Developer", "Cloud Engineer", "Data Scientist", "DevOps Engineer", "ML Engineer", "Custom"],
            help="Select the role you are preparing for"
        )
        if job_role == "Custom":
            job_role = st.text_input("Enter your Job Role", placeholder="e.g. Backend Engineer")
            if not job_role:
                st.warning("Please enter a job role to continue.")

        interview_type = st.selectbox(
            "Interview Type",
            ["HR", "Behavioral", "Technical"],
            help="HR: Background & motivation | Behavioral: Situational | Technical: DSA Coding"
        )

        difficulty = timer_limit = language = None

        if interview_type == "Technical":
            st.markdown("**🔧 Technical Settings**")
            difficulty   = st.selectbox("DSA Difficulty", ["Easy", "Medium", "Hard"])
            timer_limit  = st.slider("Time Limit (minutes)", 5, 45, 20)
            language     = st.selectbox(
                "Programming Language",
                ["Python", "C", "C++", "Java", "C#", "JavaScript"]
            )

    st.markdown("<hr style='border-color:#2d3748;'>", unsafe_allow_html=True)

    # Provider status
    provider_color = "#4ade80" if st.session_state.active_provider != "—" else "#ffffff"
    st.markdown(f"""
    <div style='margin-bottom:8px;'>
        <span style='color:#ffffff; font-size:0.8rem;'>🤖 Active Provider</span><br>
        <span style='color:{provider_color}; font-size:0.85rem; font-weight:600;'>
            {st.session_state.active_provider}
        </span>
    </div>
    """, unsafe_allow_html=True)

    # Interview progress
    q_done = len(st.session_state.scores)
    if q_done > 0:
        avg_so_far = sum(st.session_state.scores) / q_done
        st.markdown(f"""
        <div style='background:#1a1f2e; border:1px solid #2d3748; border-radius:8px; padding:12px; margin-bottom:12px;'>
            <div style='color:#ffffff; font-size:0.78rem;'>📊 Progress</div>
            <div style='color:#e2e8f0; font-size:1.1rem; font-weight:700;'>{q_done} questions answered</div>
            <div style='color:#60a5fa; font-size:0.85rem;'>Avg: {avg_so_far:.1f}/10</div>
        </div>
        """, unsafe_allow_html=True)

    if st.button("🔄 Reset Interview", use_container_width=True):
        for k in defaults:
            st.session_state[k] = defaults[k]
        st.rerun()

    st.markdown("<hr style='border-color:#2d3748;'>", unsafe_allow_html=True)
    st.markdown("""
    <div style='color:#ffffff; font-size:0.75rem; line-height:1.6;'>
        <b style='color:#cccccc;'>How it works</b><br>
        1. Set your role & interview type<br>
        2. Click <b>Start Interview</b><br>
        3. Click <b>Ask Next Question</b><br>
        4. Submit your answer for AI feedback<br>
        5. Click <b>Stop Interview</b> for scorecard
    </div>
    """, unsafe_allow_html=True)

# ════════════════════════════════════════════
#  MAIN HEADER
# ════════════════════════════════════════════
st.markdown("""
<div class='main-header'>
    <h1>🎯 AI Interview Preparation Coach</h1>
    <p>Real interview questions &nbsp;•&nbsp; Live code editor &nbsp;•&nbsp; AI feedback &nbsp;•&nbsp; Skill gap analysis</p>
</div>
""", unsafe_allow_html=True)

# ════════════════════════════════════════════
#  LANDING PAGE (not started)
# ════════════════════════════════════════════
if not st.session_state.interview_started and not st.session_state.final_score:

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
        <div class='feature-card'>
            <h4>🧠 Multi-Round Support</h4>
            <p>HR, Behavioral, and Technical (DSA) interview modes, each with tailored AI questioning.</p>
        </div>""", unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class='feature-card'>
            <h4>💻 Live Code Editor</h4>
            <p>Write and run code in 6 languages — Python, C, C++, Java, C#, and JavaScript.</p>
        </div>""", unsafe_allow_html=True)
    with col3:
        st.markdown("""
        <div class='feature-card'>
            <h4>📊 Skill Gap Analysis</h4>
            <p>Get a comprehensive post-interview analysis with an actionable improvement plan.</p>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)


    if st.button("🚀 Start Interview", use_container_width=True, type="primary"):
        if not job_role or job_role == "Custom":
            st.error("Please enter a job role before starting.")
        else:
            st.session_state.interview_started = True
            st.session_state.interview_active  = True
            st.session_state.locked_job_role       = job_role
            st.session_state.locked_interview_type = interview_type
            st.session_state.locked_difficulty      = difficulty
            st.session_state.locked_timer_limit     = timer_limit
            st.session_state.locked_language        = language
            st.rerun()

# ════════════════════════════════════════════
#  ACTIVE INTERVIEW
# ════════════════════════════════════════════
elif st.session_state.interview_active:

    # Status bar
    col_status, col_stop = st.columns([3, 1])
    with col_status:
        type_icon = {"HR": "🤝", "Behavioral": "💬", "Technical": "💻"}.get(interview_type, "📋")
        st.markdown(f"""
        <div style='display:flex; align-items:center; gap:12px; padding:8px 0;'>
            <span class='badge-active'>● LIVE</span>
            <span style='color:#ffffff; font-size:0.9rem;'>{type_icon} {interview_type} Interview &nbsp;|&nbsp; {job_role}</span>
            <span style='color:#cccccc; font-size:0.85rem;'>Q{st.session_state.question_number - 1 if st.session_state.question_number > 1 else "—"} completed: {len(st.session_state.scores)}</span>
        </div>
        """, unsafe_allow_html=True)
    with col_stop:
        if st.button("🛑 End Interview", use_container_width=True, type="primary"):
            if len(st.session_state.scores) == 0:
                st.error("⚠️ Submit at least one answer before ending the interview.")
            else:
                st.session_state.interview_active = False
                st.session_state.final_score      = True
                st.rerun()

    st.markdown("---")

    # ── ASK NEXT QUESTION ──
    if not st.session_state.current_question:
        if st.button("🧠 Ask Next Question", use_container_width=True):
            history = "\n".join([f"{s}: {m}" for s, m in st.session_state.conversation])

            if interview_type == "Technical":
                prompt = technical_coding_prompt(job_role, difficulty, st.session_state.question_number, history)
                st.session_state.start_time = time.time()
            else:
                prompt = interview_question_prompt(job_role, interview_type, st.session_state.question_number, history)

            with st.spinner("⏳ Generating your question..."):
                response = call_llm_with_retry(prompt=prompt, purpose="performance")
                question = response.text
                st.session_state.current_question = question
                st.session_state.conversation.append(("Interviewer", question))
                st.session_state.question_number += 1
                st.rerun()

    # ── CONVERSATION DISPLAY ──
    if st.session_state.conversation:
        st.markdown("<div class='section-title'>💬 Interview Conversation</div>", unsafe_allow_html=True)
        for speaker, msg in st.session_state.conversation:
            if speaker == "Interviewer":
                st.markdown(f"""
                <div class='chat-label-interviewer'>🤖 Interviewer</div>
                <div class='chat-interviewer'>{msg}</div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class='chat-label-you'>You 🧑</div>
                <div class='chat-you'>{msg}</div>
                """, unsafe_allow_html=True)

    # ── ANSWER INPUT ──
    if st.session_state.current_question:
        st.markdown("<div class='section-title'>✍️ Your Answer</div>", unsafe_allow_html=True)

        if interview_type == "Technical":
            # ── JS BROWSER TIMER (no page rerun) ──
            elapsed   = int(time.time() - st.session_state.start_time)
            remaining = max(0, timer_limit * 60 - elapsed)

            # Inject a pure JavaScript countdown — runs in browser, zero Streamlit reruns
            st.components.v1.html(f"""
            <div id="timer-box" style="
                background:#1a1f2e;
                border-radius:8px;
                padding:10px 20px;
                display:inline-block;
                margin-bottom:12px;
                border:2px solid #4ade80;
            ">
                <span id="timer-text" style="color:#4ade80; font-size:1.1rem; font-weight:700;">
                    ⏱ Calculating...
                </span>
            </div>

            <script>
                var remaining = {remaining};
                var box  = document.getElementById("timer-box");
                var text = document.getElementById("timer-text");

                function updateDisplay() {{
                    var m = Math.floor(remaining / 60);
                    var s = remaining % 60;
                    var timeStr = (m < 10 ? "0" : "") + m + ":" + (s < 10 ? "0" : "") + s;

                    if (remaining <= 60) {{
                        box.style.borderColor  = "#ef4444";
                        text.style.color       = "#ef4444";
                        text.innerHTML         = "⏱ " + timeStr + " remaining";
                    }} else if (remaining <= 180) {{
                        box.style.borderColor  = "#f59e0b";
                        text.style.color       = "#f59e0b";
                        text.innerHTML         = "⏱ " + timeStr + " remaining";
                    }} else {{
                        box.style.borderColor  = "#4ade80";
                        text.style.color       = "#4ade80";
                        text.innerHTML         = "⏱ " + timeStr + " remaining";
                    }}
                }}

                // Draw immediately on load
                updateDisplay();

                var interval = setInterval(function() {{
                    remaining--;
                    if (remaining <= 0) {{
                        clearInterval(interval);
                        box.style.borderColor = "#ef4444";
                        text.style.color      = "#ef4444";
                        text.innerHTML        = "⏰ Time is up! Your code is being submitted...";

                        // Click the hidden Streamlit time-expired button after 1s
                        // Trigger page rerun by navigating with a query param
                        setTimeout(function() {{
                            window.parent.location.href = window.parent.location.pathname + "?time_expired=1";
                        }}, 1000);;
                        return;
                    }}
                    updateDisplay();
                }}, 1000);
            </script>
            """, height=60)

            st.markdown("""
            <style>
            .st-ace { background-color: #1e2130 !important; border-radius: 8px !important; }
            </style>
            """, unsafe_allow_html=True)

            code = st_ace(
                language=language.lower(),
                theme="tomorrow_night",
                height=340,
                font_size=14,
                show_gutter=True,
                wrap=True,
                auto_update=False,
                placeholder=f"// Write your {language} solution here..."
            )

            # Save latest code to session state on every render
            if code:
                st.session_state["last_code_snapshot"] = code

            col1, col2 = st.columns(2)
            run_code      = col1.button("▶️ Run Code",      use_container_width=True)
            submit_answer = col2.button("✅ Submit Answer", use_container_width=True, type="primary")

            # ── TIME EXPIRED: auto-submit saved code ──
            time_expired_via_url = st.query_params.get("time_expired", "") == "1"
            if (time_expired_via_url or remaining == 0) and not st.session_state.get("time_expired_handled", False):
                st.session_state["time_expired_handled"] = True
                saved_code = st.session_state.get("last_code_snapshot", "# No code written before time expired")
                st.error("⏰ Time is up! Your code has been automatically submitted for evaluation.")
                st.session_state.conversation.append(("You", saved_code))
                eval_prompt = coding_evaluation_prompt(
                    job_role, st.session_state.current_question, saved_code, language, difficulty
                )
                with st.spinner("🤖 Auto-evaluating your submitted code..."):
                    feedback      = call_llm_with_retry(prompt=eval_prompt, purpose="performance")
                    feedback_text = feedback.text
                st.markdown("<div class='section-title'>📊 AI Feedback</div>", unsafe_allow_html=True)
                st.markdown(feedback_text)
                score = None
                match = re.search(r'\b([0-9]|10)\s*(?:/|out\s*of)\s*10', feedback_text.lower())
                if match:
                    score = int(match.group(1))
                else:
                    for line in feedback_text.splitlines():
                        if "score" in line.lower():
                            clean_line = re.sub(r'^\s*\d+\.\s*', '', line)
                            nums = [int(s) for s in re.findall(r'\b\d+\b', clean_line)]
                            if nums:
                                score = min(10, nums[0])
                                break
                if score is None:
                    score = 7
                st.session_state.scores.append(score)
                st.session_state.current_question   = None
                st.session_state["time_expired_handled"] = False
                st.session_state.pop("last_code_snapshot", None)
                st.query_params.clear()
                time.sleep(1)
                st.rerun()

            # ── CODE EXECUTION ──
            if run_code and code:
                st.markdown("<div class='section-title'>🖥️ Output Terminal</div>", unsafe_allow_html=True)
                with st.expander("Terminal Output", expanded=True):
                    with tempfile.TemporaryDirectory() as temp_dir:
                        try:
                            if language == "Python":
                                file_path = os.path.join(temp_dir, "main.py")
                                with open(file_path, "w") as f:
                                    f.write(code)
                                result = subprocess.run(
                                    [sys.executable, file_path],
                                    capture_output=True, text=True, timeout=10
                                )

                            elif language == "JavaScript":
                                file_path = os.path.join(temp_dir, "main.js")
                                with open(file_path, "w") as f: f.write(code)
                                result = subprocess.run(["node", file_path], capture_output=True, text=True, timeout=10)

                            elif language == "C":
                                file_path = os.path.join(temp_dir, "main.c")
                                exe_path  = os.path.join(temp_dir, "main_c")
                                with open(file_path, "w") as f: f.write(code)
                                compile_res = subprocess.run(["gcc", file_path, "-o", exe_path], capture_output=True, text=True)
                                result = subprocess.run([exe_path], capture_output=True, text=True, timeout=10) \
                                         if compile_res.returncode == 0 else compile_res

                            elif language == "C++":
                                file_path = os.path.join(temp_dir, "main.cpp")
                                exe_path  = os.path.join(temp_dir, "main_cpp")
                                with open(file_path, "w") as f: f.write(code)
                                compile_res = subprocess.run(["g++", file_path, "-o", exe_path], capture_output=True, text=True)
                                result = subprocess.run([exe_path], capture_output=True, text=True, timeout=10) \
                                         if compile_res.returncode == 0 else compile_res

                            elif language == "Java":
                                file_path = os.path.join(temp_dir, "Main.java")
                                with open(file_path, "w") as f: f.write(code)
                                compile_res = subprocess.run(["javac", file_path], capture_output=True, text=True)
                                result = subprocess.run(["java", "-cp", temp_dir, "Main"], capture_output=True, text=True, timeout=10) \
                                         if compile_res.returncode == 0 else compile_res

                            elif language == "C#":
                                file_path = os.path.join(temp_dir, "main.cs")
                                exe_path  = os.path.join(temp_dir, "main.exe")
                                with open(file_path, "w") as f: f.write(code)
                                compile_res = subprocess.run(["csc", "/nologo", f"/out:{exe_path}", file_path], capture_output=True, text=True)
                                result = subprocess.run([exe_path], capture_output=True, text=True, timeout=10) \
                                         if compile_res.returncode == 0 else compile_res

                            output = result.stdout if result.returncode == 0 else result.stderr
                            if not output:
                                output = "✅ Code executed successfully. No output produced."

                            if result.returncode == 0:
                                st.code(output, language="bash")
                            else:
                                st.error(f"❌ Compilation / Runtime Error:\n\n{output}")

                        except FileNotFoundError:
                            st.warning(f"⚠️ Compiler/interpreter for **{language}** is not installed or not in PATH.")
                        except subprocess.TimeoutExpired:
                            st.error("⏰ Execution timed out (10s limit).")
                        except Exception as e:
                            st.error(f"❌ Unexpected error: {str(e)}")

        else:
            # HR / Behavioral text answer
            code          = st.text_area("Your Answer", height=180, placeholder="Type your answer here...")
            submit_answer = st.button("✅ Submit Answer", use_container_width=True, type="primary")

        # ── EVALUATE ANSWER ──
        if submit_answer and code:
            st.session_state.conversation.append(("You", code))

            if interview_type == "Technical":
                eval_prompt = coding_evaluation_prompt(
                    job_role, st.session_state.current_question, code, language, difficulty
                )
            else:
                eval_prompt = behavioral_evaluation_prompt(
                    job_role, st.session_state.current_question, code
                )

            with st.spinner("🤖 Evaluating your answer..."):
                feedback      = call_llm_with_retry(prompt=eval_prompt, purpose="performance")
                feedback_text = feedback.text

            st.markdown("<div class='section-title'>📊 AI Feedback</div>", unsafe_allow_html=True)
            st.markdown(feedback_text)

            # ── SCORE EXTRACTION ──
            score = None
            match = re.search(r'\b([0-9]|10)\s*(?:/|out\s*of)\s*10', feedback_text.lower())
            if match:
                score = int(match.group(1))
            else:
                for line in feedback_text.splitlines():
                    if "score" in line.lower():
                        clean_line = re.sub(r'^\s*\d+\.\s*', '', line)
                        nums = [int(s) for s in re.findall(r'\b\d+\b', clean_line)]
                        if nums:
                            score = min(10, nums[0])
                            break

            if score is None:
                score = 7
                st.caption("⚠️ Score auto-detection failed — defaulting to 7/10.")

            st.session_state.scores.append(score)
            st.session_state.current_question = None
            time.sleep(1)
            st.rerun()

# ════════════════════════════════════════════
#  FINAL SCORECARD
# ════════════════════════════════════════════
if st.session_state.final_score:

    st.markdown("""
    <div style='background:linear-gradient(135deg,#0d4f2f,#14532d); border:1px solid #16a34a;
                border-radius:16px; padding:24px 32px; margin-bottom:24px;'>
        <div style='color:#4ade80; font-size:1.5rem; font-weight:800;'>🏁 Interview Complete!</div>
        <div style='color:#86efac; margin-top:4px;'>Here is your full performance scorecard and analysis.</div>
    </div>
    """, unsafe_allow_html=True)

    total = len(st.session_state.scores)
    avg   = sum(st.session_state.scores) / total

    # Metrics row
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Questions Attempted", total)
    with col2:
        st.metric("Average Score", f"{avg:.1f} / 10")
    with col3:
        verdict = "🌟 Excellent" if avg >= 8 else "👍 Good" if avg >= 6 else "📚 Needs Practice"
        st.metric("Verdict", verdict)

    # Readiness banner
    if avg >= 8:
        st.success("🌟 **Interview Ready!** — You performed excellently. Keep it up!")
    elif avg >= 6:
        st.warning("👍 **Almost Ready** — Good performance with room for improvement.")
    else:
        st.error("📚 **Keep Practicing** — Focus on the skill gaps identified below.")

    # Per-question scores
    st.markdown("<div class='section-title'>📈 Score Breakdown</div>", unsafe_allow_html=True)
    for i, s in enumerate(st.session_state.scores, 1):
        color = "#4ade80" if s >= 8 else "#f59e0b" if s >= 6 else "#ef4444"
        st.markdown(f"""
        <div style='display:flex; justify-content:space-between; align-items:center;
                    background:#1a1f2e; border:1px solid #2d3748; border-radius:8px;
                    padding:10px 18px; margin-bottom:8px;'>
            <span style='color:#ffffff; font-size:0.92rem; font-weight:500;'>Question {i}</span>
            <span style='color:{color}; font-weight:700; font-size:1.05rem;'>{s}/10</span>
        </div>
        """, unsafe_allow_html=True)

    st.divider()

    # ── SKILL GAP ANALYSIS ──
    st.markdown("<div class='section-title'>🧐 Comprehensive Skill Gap Analysis</div>", unsafe_allow_html=True)

    if st.session_state.skill_gap_analysis is None:
        if not st.session_state.conversation:
            st.info("No answered questions to analyze.")
        else:
            with st.spinner("🔍 Generating your personalised Skill Gap Analysis..."):
                history      = "\n".join([f"{s}: {m}" for s, m in st.session_state.conversation])
                scores_str   = ", ".join(map(str, st.session_state.scores))
                analysis_prompt = skill_gap_analysis_prompt(job_role, interview_type, history, scores_str)
                analysis_resp   = call_llm_with_retry(prompt=analysis_prompt, purpose="analysis")
                st.session_state.skill_gap_analysis = analysis_resp.text
                st.rerun()

    if st.session_state.skill_gap_analysis:
        st.markdown(st.session_state.skill_gap_analysis)

    st.divider()

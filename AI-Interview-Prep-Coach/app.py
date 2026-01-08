import streamlit as st
import time
from openai import OpenAI
from streamlit_ace import st_ace
from prompts import (
    interview_question_prompt,
    technical_coding_prompt,
    coding_evaluation_prompt
)

# ---------------- CONFIG ----------------
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

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
    "final_score": False
}

for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ---------------- SIDEBAR ----------------
st.sidebar.header("🛠 Interview Settings")

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

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "system", "content": prompt}]
    )

    question = response.choices[0].message.content
    st.session_state.current_question = question
    st.session_state.conversation.append(("Interviewer", question))
    st.session_state.question_number += 1

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
        st.warning(f"⏱ Time Remaining: {remaining//60}:{remaining%60:02d}")

        code = st_ace(
            language=language.lower(),
            theme="chrome",
            height=320,
            font_size=14,
            keybinding="vscode",
            show_gutter=True,
            wrap=True,
            auto_update=True
        )
    else:
        code = st.text_area("✍️ Your Answer", height=150)

    if st.button("✅ Submit Answer") and code:
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

        feedback = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "system", "content": eval_prompt}]
        )

        feedback_text = feedback.choices[0].message.content
        st.markdown("### 📊 Feedback")
        st.markdown(feedback_text)

        # Extract score
        score = 7
        for line in feedback_text.splitlines():
            if "score" in line.lower():
                nums = [int(c) for c in line if c.isdigit()]
                if nums:
                    score = nums[0]
                    break

        st.session_state.scores.append(score)
        st.session_state.current_question = None

# ---------------- FINAL SCORECARD ----------------
if st.session_state.scores and st.button("📊 End Interview & View Scorecard"):
    st.session_state.final_score = True

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

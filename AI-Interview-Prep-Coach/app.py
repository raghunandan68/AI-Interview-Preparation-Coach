import streamlit as st
from openai import OpenAI
from prompts import interview_prompt

# Initialize OpenAI client
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

st.set_page_config(page_title="AI Interview Coach", layout="centered")
st.title("🎯 AI Interview Preparation Coach")

# Session state
if "question_number" not in st.session_state:
    st.session_state.question_number = 1

if "messages" not in st.session_state:
    st.session_state.messages = []

# Sidebar
st.sidebar.header("Interview Settings")
role = st.sidebar.text_input("Job Role", "Cloud Engineer")
interview_type = st.sidebar.selectbox(
    "Interview Type",
    ["HR", "Technical", "Behavioral"]
)

# Ask question
if st.button("Ask Next Question"):
    prompt = interview_prompt(
        role,
        interview_type,
        st.session_state.question_number
    )

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": prompt}
        ]
    )

    question = response.choices[0].message.content
    st.session_state.messages.append(("AI", question))
    st.session_state.question_number += 1

# Display conversation
for speaker, msg in st.session_state.messages:
    if speaker == "AI":
        st.markdown(f"**🤖 Interviewer:** {msg}")
    else:
        st.markdown(f"**🧑 You:** {msg}")

# User answer
answer = st.text_area("Your Answer")

if st.button("Submit Answer") and answer:
    st.session_state.messages.append(("You", answer))

    feedback_prompt = f"""
You are an expert interview coach.
Evaluate the answer below.

Provide:
1. Score out of 10
2. Strengths
3. Areas to improve
4. Improved sample answer

Answer:
{answer}
"""

    feedback = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": feedback_prompt}
        ]
    )

    st.markdown("### 📊 Feedback")
    st.markdown(feedback.choices[0].message.content)

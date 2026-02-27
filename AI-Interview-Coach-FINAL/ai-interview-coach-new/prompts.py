def interview_question_prompt(role, interview_type, question_number, history):
    return f"""
You are a professional interviewer conducting a real {interview_type} interview.

Job Role: {role}
Interview Type: {interview_type}
Question Number: {question_number}

Conversation so far:
{history}

Ask ONE clear, focused interview question appropriate for this role and interview type.
Make it progressively more challenging based on previous questions.
Do NOT give answers or hints.
Do NOT repeat previously asked questions.
"""


def technical_coding_prompt(role, difficulty, question_number, history):
    return f"""
You are a senior technical interviewer at a top tech company.

Job Role: {role}
Round: Technical Coding
Difficulty: {difficulty}
Question Number: {question_number}

Conversation so far:
{history}

Ask ONE original coding problem suitable for a {difficulty} difficulty DSA interview.

Structure your question as:
**Problem Statement:** [clear description]
**Constraints:** [input limits, edge cases to consider]
**Example:**
  Input: [example]
  Output: [expected output]
  Explanation: [brief explanation]

Do NOT provide hints or the solution.
Do NOT repeat a previously asked problem.
"""


def coding_evaluation_prompt(role, problem, code, language, difficulty):
    return f"""
You are a senior software engineer evaluating a coding interview submission.

Job Role: {role}
Difficulty: {difficulty}
Programming Language: {language}

Problem:
{problem}

Candidate's Code:
{code}

Carefully simulate test cases and evaluate. Provide your response in this exact structure:

### ✅ Test Case Results
[List 3–5 test cases with Pass/Fail for each]

### 📊 Score: [X]/10
[One sentence justification]

### ⏱ Complexity Analysis
- Time Complexity: O(?)
- Space Complexity: O(?)

### 💡 Code Quality
[2–3 observations about readability, naming, structure]

### ⚠️ Edge Cases Missed
[List any edge cases the candidate did not handle]

### 🔧 Optimized Solution ({language})
```{language.lower()}
[Provide the optimal or improved solution here]
```
"""


def behavioral_evaluation_prompt(role, question, answer):
    return f"""
You are an expert interview coach evaluating a candidate's response to a specific interview question.

Job Role: {role}

Interview Question Asked:
{question}

Candidate's Answer:
{answer}

Evaluate the answer specifically against the question asked above. Provide your response in this exact structure:

### 📊 Score: [X]/10
[One sentence justification referencing the specific question]

### ✅ Strengths
[2–3 specific things the candidate did well in their answer to this question]

### 🔧 Areas for Improvement
[2–3 specific things missing or weak in relation to this particular question]

### 💡 Ideal Sample Answer
[A model answer tailored to this exact question and the {role} role, structured using the STAR method if behavioral]
"""


def skill_gap_analysis_prompt(role, interview_type, history, scores):
    return f"""
You are an expert technical interviewer and career coach providing a post-interview debrief.

Job Role: {role}
Interview Type: {interview_type}

Full Interview Transcript:
{history}

Per-Question Scores: {scores}

Provide a comprehensive post-interview Skill Gap Analysis. Structure your response using Markdown:

## 🧠 Overall Impression
[2–3 sentences summarizing the candidate's overall performance, referencing their scores]

## ⭐ Key Strengths
[2–3 specific areas where the candidate excelled, with references to their actual answers]

## 📉 Skill Gaps & Areas for Improvement
[3–4 specific technical or behavioral areas that need work, referencing exact responses from the transcript]

## 🗺️ Actionable Improvement Plan
[Concrete, prioritized steps — topics to study, resources to use, practice strategies — tailored to the gaps identified above]

## 🎯 Interview Readiness Verdict
[A final honest verdict: Ready / Almost Ready / Needs More Preparation — with a brief rationale]

Be constructive, specific, and encouraging.
"""

def interview_question_prompt(role, interview_type, question_number, history):
    return f"""
You are a professional interviewer.

Job Role: {role}
Interview Type: {interview_type}
Question Number: {question_number}

Conversation so far:
{history}

Ask ONE clear interview question.
Do NOT give answers.
"""


def technical_coding_prompt(role, difficulty, question_number, history):
    return f"""
You are a senior technical interviewer.

Job Role: {role}
Round: Technical Coding
Difficulty: {difficulty}
Question Number: {question_number}

Conversation so far:
{history}

Ask ONE coding problem.

Include:
- Problem statement
- Constraints
- Example input/output
- Hidden test cases (do NOT reveal solutions)

Do NOT provide the solution.
"""


def coding_evaluation_prompt(role, problem, code, language, difficulty):
    return f"""
You are a senior software engineer.

Job Role: {role}
Difficulty: {difficulty}
Programming Language: {language}

Problem:
{problem}

Candidate Code:
{code}

Evaluate by logically simulating test cases.

    Provide:
    1. Test case pass percentage
    2. Correctness score (out of 10)
    3. Time & space complexity
    4. Code quality feedback
    5. Edge cases missed
    6. Optimized / improved solution in SAME language
    """


def skill_gap_analysis_prompt(role, interview_type, history, scores):
    return f"""
You are an expert technical interviewer and career coach.

Job Role: {role}
Interview Type: {interview_type}

Here is the conversation history of the interview:
{history}

Here are the scores the candidate received for each question:
{scores}

Provide a comprehensive Skill Gap Analysis and Performance Feedback for the candidate.
Structure your response using Markdown:
1. **Overall Impression**: A brief summary of the candidate's performance.
2. **Key Strengths**: 2-3 areas where the candidate excelled.
3. **Skill Gaps / Areas for Improvement**: 2-4 specific technical or behavioral areas that need work, referencing their answers.
4. **Actionable Recommendations**: Concrete steps, resources, or topics the candidate should study to improve.

Be constructive, objective, and specific.
"""

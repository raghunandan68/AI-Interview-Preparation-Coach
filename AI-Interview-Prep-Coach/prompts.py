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

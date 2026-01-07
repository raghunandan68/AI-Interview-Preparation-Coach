def interview_prompt(role, interview_type, question_number):
    return f"""
You are an expert interview coach.

Role: {role}
Interview type: {interview_type}

Ask interview question number {question_number}.
Keep it realistic and professional.
"""

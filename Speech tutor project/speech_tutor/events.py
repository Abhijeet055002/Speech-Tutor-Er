# events.py — Event and flow handlers for VaakShakti AI

def handle_question_generation(choice_mode, current_question, topic, difficulty, model, handle_custom_question=None, fallback_generate=None):
    """
    Handles the logic of generating a question and ideal answer.
    If `handle_custom_question` is provided, it is used for custom question generation.
    """
    if handle_custom_question:
        return handle_custom_question(choice_mode, current_question, topic, difficulty, model)
    
    if choice_mode == "Enter custom topic" and current_question.strip():
        return current_question, "This is a custom question. No ideal answer reference is available."
    
    if fallback_generate:
        return fallback_generate(topic, difficulty, model)

    return "Sample Question?", "Sample Ideal Answer."


def enhanced_tutor_conversation(audio, question, ideal_answer, difficulty, model, user_id, topic, tutor_conversation_func, save_history_func, calculate_rating_func):
    """
    Processes audio input, evaluates performance, and logs the session.
    """
    if not audio:
        return "❌ No audio received", "", "", "", ideal_answer, 0.0, ""

    transcript, grammar, feedback, comparison = tutor_conversation_func(audio, question, ideal_answer, difficulty, model)
    rating = calculate_rating_func(transcript, grammar, feedback, comparison)
    save_history_func(user_id, topic, difficulty, question, transcript, grammar, feedback, comparison, rating)
    
    return transcript, grammar, feedback, comparison, ideal_answer, rating, ""


def format_interview_questions(topic, personality, skills, model, generator_func):
    """
    Generates interview questions based on user traits and skills.
    """
    if not topic or not personality or not skills:
        return "Please fill in all fields to generate interview questions."

    questions = generator_func(topic, personality, skills, model)
    formatted = f"## Interview Questions for: {topic}\n\n{questions}"
    return formatted


def format_history(user_id, load_history_func):
    """
    Formats the last 10 sessions for display in the history tab.
    """
    history = load_history_func(user_id)
    if not history["sessions"]:
        return "You haven't completed any practice sessions yet."

    sessions = history["sessions"][-10:][::-1]
    output = "# Your Practice History\n\n"
    for i, session in enumerate(sessions):
        output += f"## Session {i+1}: {session['timestamp']}\n"
        output += f"**Topic:** {session['topic']} | **Difficulty:** {session['difficulty']}\n"
        output += f"**Rating:** {session['rating']}/5.0 stars\n"
        output += f"**Question:** {session['question']}\n"
        output += f"**Your Answer:** {session['transcript'][:100]}...\n"
        output += f"**Key Feedback:** {session['grammar_feedback'][:100]}...\n\n---\n\n"

    return output


def update_current_topic(choice_mode, dropdown_value, custom_value):
    """
    Determines the active topic based on user selection mode.
    """
    topic = custom_value.strip() if choice_mode == "Enter custom topic" and custom_value else dropdown_value
    return topic, topic

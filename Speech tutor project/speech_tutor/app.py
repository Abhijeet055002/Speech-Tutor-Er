# Final version of app.py with enhanced layout, prompt fix, and gradient UI
import gradio as gr
from whisper_engine import transcribe
from grammar_corrector import get_corrected_grammar, get_speech_feedback, compare_answers
from llm_engine import call_ollama
from string import Template
# import HuggingFaceLogin as HFL
import json
import datetime
from pathlib import Path

# Import UI components
from ui import create_ui, calculate_rating, format_star_rating

# HFL.login_to_huggingface()

# --- Generate question + ideal answer ---
def generate_question_and_answer(topic, difficulty, model):
    # Add a random seed to prevent repetition
    import random
    random_seed = random.randint(1, 10000)
    
    prompt = Template("""
You are a professor and recognized expert in "$topic".

Create a concise, precise speaking prompt at a "$difficulty" level. Your task:

1. Generate a BRIEF, focused question about "$topic" that:
   - Is intellectually stimulating but CONCISE (max 1-2 sentences)
   - Requires critical thinking appropriate for the difficulty level
   - Avoids vague or overly broad phrasing
   - Is DIFFERENT from standard/common questions on this topic

2. Difficulty guidelines:
   - Easy: Clear, accessible language about familiar concepts
   - Medium: Focused questions on specific concepts requiring explanation
   - Hard: Precise questions on advanced concepts requiring structured argument

3. Question format requirements:
   - BREVITY is essential - questions should be direct and to the point
   - For medium/hard levels, focus on SPECIFIC aspects rather than broad topics
   - Include a clear focus that guides the speaker

Output format:
Question: <Your concise, focused question - NO MORE THAN 1-2 SENTENCES>
Ideal Answer: <A well-structured response showing appropriate depth for the difficulty level>

IMPORTANT: 
- Use random seed $random_seed to ensure question variety
- Questions MUST be brief and precise
- Avoid lengthy, multi-part questions
- Focus on quality over quantity in both question and answer
""").substitute(topic=topic, difficulty=difficulty, random_seed=random_seed)

    # First attempt
    response = call_ollama(prompt, model=model)
    try:
        question, ideal = response.split("Ideal Answer:")
        question_text = question.replace("Question:", "").strip()
        
        # Verify we don't have an empty or default question
        if question_text and not question_text.lower().startswith("what do you think about"):
            return question_text, ideal.strip()
    except:
        pass  # Continue to fallback if there's an exception
    
    # Fallback with a more specific question based on topic and difficulty
    fallback_prompts = {
        "Easy": f"How has {topic} influenced your personal experiences?",
        "Medium": f"What are the most significant developments in {topic} in recent years?",
        "Hard": f"Analyze the critical challenges facing {topic} and propose potential solutions."
    }
    
    fallback_question = fallback_prompts.get(difficulty, f"Discuss a specific aspect of {topic} that interests you most.")
    fallback_answer = f"This would require a thoughtful response about {topic} appropriate for {difficulty} difficulty level."
    
    # Try one more time with a simpler prompt
    retry_prompt = f"Generate a single, concise question about {topic} at {difficulty} difficulty level."
    retry_response = call_ollama(retry_prompt, model=model)
    
    if len(retry_response) > 10 and "?" in retry_response:
        # Use the retry response if it looks reasonable
        return retry_response.strip(), fallback_answer
    
    # Use our fallback if all else fails
    return fallback_question, fallback_answer

# --- Full agentic flow ---
def tutor_conversation(audio, question, ideal_answer, difficulty, model):
    if not audio:
        return "❌ No audio received", "", "", ""

    transcript, flagged_words = transcribe(audio)
    if not transcript:
        return "❌ No speech detected", "", "", ""

    grammar_output = get_corrected_grammar(transcript, question=question, model=model)
    feedback_output = get_speech_feedback(flagged_words, transcript=transcript, question=question, model=model)
    comparison = compare_answers(transcript, ideal_answer, model=model)

    return transcript, grammar_output, feedback_output, comparison

def resolve_topic(choice_mode, dropdown_value, custom_value):
    """
    Resolves which topic to use based on the input mode.
    This function is used by both the UI and backend to ensure consistent behavior.
    """
    return custom_value.strip() if choice_mode == "Enter custom topic" and custom_value else dropdown_value

def handle_custom_question(choice_mode, current_question, topic, difficulty, model):
    """
    Handles custom question input:
    - If in custom topic mode and question is already populated, use that question
    - Otherwise, generate a new question and ideal answer
    """
    if choice_mode == "Enter custom topic" and current_question.strip():
        # Return the existing question and a placeholder for ideal answer
        return current_question, "This is a custom question. No ideal answer reference is available."
    else:
        # Generate a new question and ideal answer
        return generate_question_and_answer(topic, difficulty, model)

# Function to generate interview questions
def generate_interview_questions(topic, personality_traits, technical_skills, model):
    prompt = f"""Generate 5 interview questions related to {topic} that would be appropriate for someone with the following traits:
    
Personality traits: {personality_traits}
Technical skills: {technical_skills}

For each question, provide:
1. The question itself (concise and clear)
2. A brief hint/guideline on how to approach answering it
3. Key points that should be included in a good answer

Format each question as:
Q: [Question text]
Hint: [Brief guidance on approaching the answer]
Key points: [Bullet points of important elements to include]

Make the questions varied in difficulty and approach.
"""
    
    response = call_ollama(prompt, model=model)
    return response

# Function to save user history
def save_history(user_id, topic, difficulty, question, transcript, grammar, feedback, comparison, rating):
    # Create history directory if it doesn't exist
    history_dir = Path("user_history")
    history_dir.mkdir(exist_ok=True)
    
    # Create user file if it doesn't exist
    user_file = history_dir / f"{user_id}.json"
    
    # Load existing history or create new
    if user_file.exists():
        with open(user_file, "r") as f:
            history = json.load(f)
    else:
        history = {"sessions": []}
    
    # Add new session
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    new_session = {
        "timestamp": timestamp,
        "topic": topic,
        "difficulty": difficulty,
        "question": question,
        "transcript": transcript,
        "grammar_feedback": grammar,
        "pronunciation_feedback": feedback,
        "comparison_feedback": comparison,
        "rating": rating
    }
    
    history["sessions"].append(new_session)
    
    # Save updated history
    with open(user_file, "w") as f:
        json.dump(history, f, indent=2)
    
    return history

# Function to load user history
def load_history(user_id):
    history_file = Path("user_history") / f"{user_id}.json"
    if history_file.exists():
        with open(history_file, "r") as f:
            return json.load(f)
    return {"sessions": []}

# Create the UI and launch the app
app = create_ui(
    generate_question_and_answer=generate_question_and_answer,
    tutor_conversation=tutor_conversation,
    generate_interview_questions=generate_interview_questions,
    load_history=load_history,
    save_history=save_history,
    handle_custom_question=handle_custom_question
)

if __name__ == "__main__":
    app.launch(server_port=7777, share=True)
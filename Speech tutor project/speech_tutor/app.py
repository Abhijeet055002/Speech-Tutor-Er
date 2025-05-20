# Final version of app.py with enhanced layout, prompt fix, and gradient UI
import gradio as gr
from whisper_engine import transcribe
from grammar_corrector import get_corrected_grammar, get_speech_feedback, compare_answers
from llm_engine import call_ollama
from string import Template

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
        return "❌ No audio received", "", "", "", ideal_answer

    transcript, flagged_words = transcribe(audio)
    if not transcript:
        return "❌ No speech detected", "", "", "", ideal_answer

    grammar_output = get_corrected_grammar(transcript, question=question, model=model)
    feedback_output = get_speech_feedback(flagged_words, transcript=transcript, question=question, model=model)
    comparison = compare_answers(transcript, ideal_answer, difficulty=difficulty, model=model)

    return transcript, grammar_output, feedback_output, comparison, ideal_answer

def resolve_topic(choice_mode, dropdown_value, custom_value):
    return custom_value.strip() if choice_mode == "Enter custom topic" and custom_value else dropdown_value

# --- Helper functions for new features ---
import json
import os
import datetime
import random
from pathlib import Path

# Function to calculate star rating based on feedback
def calculate_rating(transcript, grammar, feedback, comparison):
    # Simple algorithm to calculate rating between 1.0 and 5.0
    # This can be made more sophisticated later
    if not transcript:
        return 0
    
    # Base score
    score = 3.0
    
    # Add points for length (up to 0.5 points)
    words = len(transcript.split())
    if words > 50:
        score += 0.5
    elif words > 30:
        score += 0.3
    elif words > 15:
        score += 0.1
    
    # Check for grammar issues (subtract up to 0.7 points)
    if "no grammar issues" in grammar.lower() or "excellent grammar" in grammar.lower():
        score += 0.7
    elif "minor grammar issues" in grammar.lower():
        score += 0.3
    elif "several grammar issues" in grammar.lower():
        score -= 0.3
    else:
        score -= 0.5
    
    # Check pronunciation feedback (up to 0.5 points)
    if "excellent pronunciation" in feedback.lower() or "no pronunciation issues" in feedback.lower():
        score += 0.5
    elif "minor pronunciation issues" in feedback.lower():
        score += 0.2
    elif "several pronunciation issues" in feedback.lower():
        score -= 0.2
    else:
        score -= 0.4
    
    # Check comparison with ideal answer (up to 1.0 points)
    if "excellent response" in comparison.lower() or "outstanding answer" in comparison.lower():
        score += 1.0
    elif "good response" in comparison.lower() or "solid answer" in comparison.lower():
        score += 0.5
    elif "adequate response" in comparison.lower():
        score += 0.2
    elif "poor response" in comparison.lower():
        score -= 0.5
    
    # Ensure score is between 1.0 and 5.0
    score = max(1.0, min(5.0, score))
    
    # Round to one decimal place
    return round(score, 1)

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

# Function to display star rating as HTML
def format_star_rating(rating):
    full_stars = int(rating)
    half_star = rating - full_stars >= 0.5
    empty_stars = 5 - full_stars - (1 if half_star else 0)
    
    stars_html = ""
    # Full stars
    for _ in range(full_stars):
        stars_html += '<span style="color: gold; font-size: 24px;">★</span>'
    
    # Half star if needed
    if half_star:
        stars_html += '<span style="color: gold; font-size: 24px;">⯨</span>'
    
    # Empty stars
    for _ in range(empty_stars):
        stars_html += '<span style="color: #ccc; font-size: 24px;">☆</span>'
    
    return f'<div style="text-align: center;">{stars_html} <span style="font-size: 20px; vertical-align: middle; margin-left: 10px;">{rating}/5.0</span></div>'

# --- UI App with enhanced features ---
def create_custom_theme():
    return gr.themes.Soft(
        primary_hue="indigo",
        secondary_hue="blue",
        neutral_hue="slate",
        font=["Poppins", "ui-sans-serif", "system-ui", "sans-serif"],
    ).set(
        body_background_fill="linear-gradient(to right, #E0EAFC, #CFDEF3)",
        button_primary_background_fill="linear-gradient(90deg, #6366F1, #4F46E5)",
        button_primary_background_fill_hover="linear-gradient(90deg, #4F46E5, #4338CA)",
        button_secondary_background_fill="linear-gradient(90deg, #60A5FA, #3B82F6)",
        button_secondary_background_fill_hover="linear-gradient(90deg, #3B82F6, #2563EB)",
        block_title_text_color="#1E293B",
        block_label_text_color="#475569",
        input_background_fill="#F8FAFC",
        checkbox_background_color="#F8FAFC",
        checkbox_background_color_selected="#4F46E5",
        slider_color="#4F46E5",
        slider_color_dark="#4F46E5",
    )

with gr.Blocks(title="VaakShakti AI | Sanskrit-Inspired Speech Mastery", theme=create_custom_theme()) as app:
    # User ID for history tracking (simple implementation)
    user_id = gr.State(value=f"user_{random.randint(1000, 9999)}")
    current_topic = gr.State(value="")
    
    # Header with logo and tagline
    gr.HTML("""
    <div style="display: flex; justify-content: center; align-items: center; margin-bottom: 20px;">
        <img src="https://img.icons8.com/fluency/96/artificial-intelligence.png" alt="AI Logo" style="height: 80px; margin-right: 20px;">
        <div>
            <h1 style="text-align:center; font-size: 2.8em; background: linear-gradient(to right, #4F46E5, #2563EB); -webkit-background-clip: text; color: transparent; margin-bottom: 0;">VaakShakti AI</h1>
            <h3 style="text-align:center; margin-top: 5px; color: #475569; font-weight: 400;">Sanskrit-Inspired AI for Mastering the Art of Speech</h3>
        </div>
    </div>
    <div style="text-align: center; margin-bottom: 20px; padding: 10px; background: rgba(255, 255, 255, 0.7); border-radius: 10px;">
        <p style="margin: 0; color: #475569; font-style: italic;">"वाक्शक्ति (VaakShakti): The divine power of speech that transforms knowledge into wisdom"</p>
    </div>
    """)

    # Tabs for different features
    with gr.Tabs() as tabs:
        # Practice Tab
        with gr.TabItem("🎯 Practice Speaking", id="practice"):
            with gr.Row():
                with gr.Column(scale=1):
                    with gr.Box():
                        gr.Markdown("### 🔍 Topic Selection")
                        topic_choice = gr.Radio(
                            ["Select from list", "Enter custom topic"], 
                            value="Select from list", 
                            label="Topic Input Mode"
                        )
                        topic_dropdown = gr.Dropdown(
                            choices=["Hobbies", "Travel", "Finance", "Technology", "Career Goals", 
                                    "Education", "Leadership", "Innovation", "Sustainability", 
                                    "Cultural Diversity", "Digital Transformation"],
                            label="Choose a Topic", 
                            visible=True
                        )
                        custom_topic_box = gr.Textbox(
                            label="Custom Topic", 
                            placeholder="Type any topic...", 
                            visible=False
                        )
                        
                        difficulty_selector = gr.Radio(
                            choices=["Easy", "Medium", "Hard"],
                            value="Medium",
                            label="Difficulty Level",
                            info="Select the complexity level of questions"
                        )
                        
                        model_selector = gr.Dropdown(
                            choices=[
                                "mistral-small3.1", "gemma3:27b", "qwq:latest", "llama3.2:latest",
                                "phi4-mini:latest", "qwen3:4b", "qwen3:32b", "llama2:latest", "mistral:latest"
                            ],
                            value="mistral:latest",
                            label="AI Model"
                        )
                        generate_btn = gr.Button("🎲 Generate Question", variant="primary")

                    with gr.Box():
                        gr.Markdown("### 🎤 Your Speaking Task")
                        question_box = gr.Textbox(label="Your Question", interactive=False)
                        ideal_answer_box = gr.Textbox(label="Ideal Answer Reference", interactive=False, visible=False)
                        
                        audio_input = gr.Audio(source="microphone", type="filepath", label="Record Your Answer")
                        submit_btn = gr.Button("🚀 Analyze My Speech", variant="primary")

                with gr.Column(scale=1):
                    with gr.Box():
                        gr.Markdown("### � Performance Rating")
                        rating_display = gr.HTML(format_star_rating(0.0))
                    
                    with gr.Accordion("Transcript", open=True):
                        transcript_output = gr.Textbox(label="What You Said")
                    
                    with gr.Accordion("Grammar Feedback", open=True):
                        grammar_output = gr.Textbox(label="Grammar Analysis")
                    
                    with gr.Accordion("Pronunciation Feedback", open=True):
                        feedback_output = gr.Textbox(label="Pronunciation Tips")
                    
                    with gr.Accordion("Content Evaluation", open=True):
                        comparison_output = gr.Textbox(label="Content Analysis")
                    
                    with gr.Accordion("Ideal Answer Reference", open=False):
                        ideal_answer_display = gr.Textbox(label="AI Reference Answer")

        # Interview Prep Tab
        with gr.TabItem("🎭 Interview Prep", id="interview"):
            with gr.Row():
                with gr.Column(scale=1):
                    interview_topic = gr.Textbox(label="Interview Topic/Position", placeholder="e.g., Software Engineer, Data Scientist, Marketing Manager")
                    personality_traits = gr.Textbox(label="Your Personality Traits", placeholder="e.g., analytical, creative, detail-oriented, team player")
                    technical_skills = gr.Textbox(label="Your Technical Skills", placeholder="e.g., Python, SQL, data analysis, project management")
                    interview_model = gr.Dropdown(
                        choices=["mistral:latest", "llama3.2:latest", "qwen3:32b"],
                        value="mistral:latest",
                        label="AI Model"
                    )
                    generate_interview_btn = gr.Button("Generate Interview Questions", variant="primary")
                
                with gr.Column(scale=1):
                    interview_questions = gr.Markdown("Your interview questions will appear here...")

        # History Tab
        with gr.TabItem("📚 Your History", id="history"):
            with gr.Row():
                with gr.Column(scale=1):
                    refresh_history_btn = gr.Button("Refresh History", variant="secondary")
                    history_display = gr.Markdown("Your practice history will appear here...")

    # States for tracking
    question_state = gr.State()
    ideal_answer_state = gr.State()
    difficulty_state = gr.State()
    rating_state = gr.State(0.0)

    # Event handlers
    topic_choice.change(
        fn=lambda mode: (gr.update(visible=(mode == "Select from list")), gr.update(visible=(mode == "Enter custom topic"))),
        inputs=topic_choice,
        outputs=[topic_dropdown, custom_topic_box]
    )

    # Generate question flow
    def update_current_topic(choice_mode, dropdown_value, custom_value):
        topic = custom_value.strip() if choice_mode == "Enter custom topic" and custom_value else dropdown_value
        return topic, topic
    
    generate_btn.click(
        fn=update_current_topic,
        inputs=[topic_choice, topic_dropdown, custom_topic_box],
        outputs=[custom_topic_box, current_topic]
    ).then(
        fn=generate_question_and_answer,
        inputs=[custom_topic_box, difficulty_selector, model_selector],
        outputs=[question_box, ideal_answer_box]
    ).then(
        lambda q, a, d: (q, a, d),
        inputs=[question_box, ideal_answer_box, difficulty_selector],
        outputs=[question_state, ideal_answer_state, difficulty_state]
    ).then(
        lambda: gr.update(visible=False),
        inputs=None,
        outputs=ideal_answer_box
    ).then(
        lambda a: a,
        inputs=ideal_answer_box,
        outputs=ideal_answer_display
    )

    # Enhanced tutor conversation with rating
    def enhanced_tutor_conversation(audio, question, ideal_answer, difficulty, model, user_id, topic):
        if not audio:
            return "❌ No audio received", "", "", "", ideal_answer, 0.0, format_star_rating(0.0)

        transcript, flagged_words = transcribe(audio)
        if not transcript:
            return "❌ No speech detected", "", "", "", ideal_answer, 0.0, format_star_rating(0.0)

        grammar_output = get_corrected_grammar(transcript, question=question, model=model)
        feedback_output = get_speech_feedback(flagged_words, transcript=transcript, question=question, model=model)
        comparison = compare_answers(transcript, ideal_answer, difficulty=difficulty, model=model)
        
        # Calculate rating
        rating = calculate_rating(transcript, grammar_output, feedback_output, comparison)
        
        # Save history
        save_history(user_id, topic, difficulty, question, transcript, grammar_output, feedback_output, comparison, rating)
        
        return transcript, grammar_output, feedback_output, comparison, ideal_answer, rating, format_star_rating(rating)

    submit_btn.click(
        enhanced_tutor_conversation,
        inputs=[audio_input, question_state, ideal_answer_state, difficulty_state, model_selector, user_id, current_topic],
        outputs=[transcript_output, grammar_output, feedback_output, comparison_output, ideal_answer_box, rating_state, rating_display]
    ).then(
        lambda a: a,
        inputs=ideal_answer_box,
        outputs=ideal_answer_display
    )

    # Interview questions generation
    def format_interview_questions(topic, personality, skills, model):
        if not topic or not personality or not skills:
            return "Please fill in all fields to generate interview questions."
        
        questions = generate_interview_questions(topic, personality, skills, model)
        
        # Format the response with Markdown for better readability
        formatted = f"## Interview Questions for: {topic}\n\n"
        formatted += questions
        
        return formatted

    generate_interview_btn.click(
        fn=format_interview_questions,
        inputs=[interview_topic, personality_traits, technical_skills, interview_model],
        outputs=interview_questions
    )

    # History display
    def format_history(user_id):
        history = load_history(user_id)
        if not history["sessions"]:
            return "You haven't completed any practice sessions yet."
        
        sessions = history["sessions"]
        sessions.reverse()  # Most recent first
        
        formatted = "# Your Practice History\n\n"
        
        for i, session in enumerate(sessions[:10]):  # Show last 10 sessions
            formatted += f"## Session {i+1}: {session['timestamp']}\n"
            formatted += f"**Topic:** {session['topic']} | **Difficulty:** {session['difficulty']}\n"
            formatted += f"**Rating:** {session['rating']}/5.0 stars\n"
            formatted += f"**Question:** {session['question']}\n"
            formatted += f"**Your Answer:** {session['transcript'][:100]}...\n"
            formatted += f"**Key Feedback:** {session['grammar_feedback'][:100]}...\n\n"
            formatted += "---\n\n"
        
        if len(sessions) > 10:
            formatted += f"*{len(sessions) - 10} more sessions not shown*"
        
        return formatted

    refresh_history_btn.click(
        fn=format_history,
        inputs=user_id,
        outputs=history_display
    )

    # Initialize history on load
    app.load(
        fn=format_history,
        inputs=user_id,
        outputs=history_display
    )

app.launch(server_port=7777, share=True)
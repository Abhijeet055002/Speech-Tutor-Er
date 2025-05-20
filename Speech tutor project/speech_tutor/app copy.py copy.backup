# Final version of app.py with enhanced layout, prompt fix, and gradient UI
import gradio as gr
from whisper_engine import transcribe
from grammar_corrector import get_corrected_grammar, get_speech_feedback, compare_answers
from llm_engine import call_ollama
from string import Template

# --- Generate question + ideal answer ---
def generate_question_and_answer(topic, model):
    prompt = Template("""
You are a professor and expert in $topic.

Write a two-part speaking prompt that:
1. Asks a realistic and intellectually challenging question related to "$topic".
2. Follow it with a situation-based reflection or comparison element to encourage critical thinking.

Use this format:
Question: <question text>
Ideal Answer: <ideal, well-spoken, fluent sample answer>

Avoid markdown symbols like ** or formatting.
""").substitute(topic=topic)

    response = call_ollama(prompt, model=model)
    try:
        question, ideal = response.split("Ideal Answer:")
        return question.replace("Question:", "").strip(), ideal.strip()
    except:
        return "What do you think about this topic?", "I'm not sure, please retry."

# --- Full agentic flow ---
def tutor_conversation(audio, question, ideal_answer, model):
    if not audio:
        return "❌ No audio received", "", "", "", ideal_answer

    transcript, flagged_words = transcribe(audio)
    if not transcript:
        return "❌ No speech detected", "", "", "", ideal_answer

    grammar_output = get_corrected_grammar(transcript, question=question, model=model)
    feedback_output = get_speech_feedback(flagged_words, transcript=transcript, question=question, model=model)
    comparison = compare_answers(transcript, ideal_answer, model=model)

    return transcript, grammar_output, feedback_output, comparison, ideal_answer

def resolve_topic(choice_mode, dropdown_value, custom_value):
    return custom_value.strip() if choice_mode == "Enter custom topic" and custom_value else dropdown_value

# --- UI App ---
with gr.Blocks(title="Professor Rustom | Speaking Mentor", theme=gr.themes.Soft()) as app:
    gr.HTML("""
    <h1 style='text-align:center; font-size: 2.5em; background: linear-gradient(to right, #434343, #000000); -webkit-background-clip: text; color: transparent;'>Professor Rustom </h1>
    <h3 style='text-align:center; margin-top: -15px; color: #444;'>Your Mentor in Mastering the Art of Speaking</h3>
    <br>
    """)

    with gr.Row():
        with gr.Column(scale=1):
            topic_choice = gr.Radio(["Select from list", "Enter custom topic"], value="Select from list", label="🧭 Topic Input Mode")
            topic_dropdown = gr.Dropdown(choices=["Hobbies", "Travel", "Finance", "Technology", "Career Goals", "Education"], label="🎯 Choose a Topic", visible=True)
            custom_topic_box = gr.Textbox(label="📝 Custom Topic", placeholder="Type any topic...", visible=False)
            model_selector = gr.Dropdown(
                choices=[
                    "mistral-small3.1", "gemma3:27b", "qwq:latest", "llama3.2:latest",
                    "phi4-mini:latest", "qwen3:4b", "qwen3:32b", "llama2:latest", "mistral:latest"
                ],
                value="mistral:latest",
                label="🧠 Select Model"
            )
            generate_btn = gr.Button("🎲 Generate Question")

            question_box = gr.Textbox(label="🗨️ Expert-Generated Question", interactive=False)
            ideal_answer_box = gr.Textbox(label="✅ Ideal Answer (from AI)", interactive=False, visible=False)

            audio_input = gr.Audio(type="filepath", label="🎙️ Speak Your Answer")
            submit_btn = gr.Button("🚀 Analyze My Speech")

        with gr.Column(scale=1):
            gr.Markdown("### 👂 Agent 1: Transcript")
            transcript_output = gr.Textbox(label="Transcript")

            gr.Markdown("### ✍️ Agent 2: Grammar Correction")
            grammar_output = gr.Textbox(label="Corrected Sentence + Explanation")

            gr.Markdown("### 🗣️ Agent 3: Speech Feedback")
            feedback_output = gr.Textbox(label="Pronunciation Tips")

            gr.Markdown("### 📊 Agent 4: Comparison with Ideal Answer")
            comparison_output = gr.Textbox(label="Insights and Suggestions")

    question_state = gr.State()
    ideal_answer_state = gr.State()

    topic_choice.change(
        fn=lambda mode: (gr.update(visible=(mode == "Select from list")), gr.update(visible=(mode == "Enter custom topic"))),
        inputs=topic_choice,
        outputs=[topic_dropdown, custom_topic_box]
    )

    generate_btn.click(
        fn=resolve_topic,
        inputs=[topic_choice, topic_dropdown, custom_topic_box],
        outputs=custom_topic_box
    ).then(
        fn=generate_question_and_answer,
        inputs=[custom_topic_box, model_selector],
        outputs=[question_box, ideal_answer_box]
    ).then(
        lambda q, a: (q, a),
        inputs=[question_box, ideal_answer_box],
        outputs=[question_state, ideal_answer_state]
    ).then(
        lambda: gr.update(visible=False),
        inputs=None,
        outputs=ideal_answer_box
    )

    submit_btn.click(
        tutor_conversation,
        inputs=[audio_input, question_state, ideal_answer_state, model_selector],
        outputs=[transcript_output, grammar_output, feedback_output, comparison_output, ideal_answer_box]
    ).then(
        lambda: gr.update(visible=True),
        inputs=None,
        outputs=ideal_answer_box
    )

app.launch(server_name="localhost", server_port=7777)
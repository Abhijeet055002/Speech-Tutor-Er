# ui.py — Main entrypoint for VaakShakti AI UI

import gradio as gr
from theme import create_custom_theme, format_star_rating
from components import header_section, mic_wave_animation
from events import (
    handle_question_generation,
    enhanced_tutor_conversation,
    format_interview_questions,
    format_history,
    update_current_topic
)
from states import init_states
from rating import calculate_rating
from constants import TOPIC_CHOICES, MODEL_CHOICES, DIFFICULTY_LEVELS


def create_ui(generate_question_and_answer, tutor_conversation, generate_interview_questions, load_history, save_history, handle_custom_question=None):
    states = init_states()
    user_id = states["user_id"]
    current_topic = states["current_topic"]
    question_state = states["question_state"]
    ideal_answer_state = states["ideal_answer_state"]
    difficulty_state = states["difficulty_state"]
    rating_state = states["rating_state"]

    with gr.Blocks(title="VaakShakti AI | Sanskrit-Inspired Speech Mastery", theme=create_custom_theme()) as app:
        gr.HTML(header_section())

        with gr.Tabs() as tabs:
            with gr.TabItem("🎯 Practice Speaking", id="practice"):
                with gr.Row():
                    with gr.Column(scale=1):
                        with gr.Box():
                            gr.Markdown("### 🔍 Topic Selection")
                            gr.Markdown("&nbsp;")  # 👈 Dummy spacing to prevent fallback "Radio" label

                            topic_choice = gr.Radio(
                                ["Select from list", "Enter custom topic"],
                                value="Select from list",
                                label="Select Topic Mode"  # Explicitly no label
                            )

                            topic_dropdown = gr.Dropdown(
                                choices=TOPIC_CHOICES,
                                label="Choose a Topic",
                                visible=True
                            )
                            custom_topic_box = gr.Textbox(
                                label="Custom Topic",
                                placeholder="Type any topic or question...",
                                visible=False
                            )

                            difficulty_selector = gr.Radio(
                                choices=DIFFICULTY_LEVELS,
                                value="Medium",
                                label="Difficulty Level"
                            )
                            model_selector = gr.Dropdown(
                                choices=MODEL_CHOICES,
                                value="mistral:latest",
                                label="AI Model"
                            )
                            generate_btn = gr.Button("🎲 Generate Question", variant="primary")


                        with gr.Box():
                            gr.Markdown("### 🎤 Your Speaking Task")
                            question_box = gr.Textbox(label="Your Question", interactive=False, placeholder="Your question will appear here")
                            ideal_answer_box = gr.Textbox(label="Ideal Answer Reference", interactive=False, visible=False)
                            
                            with gr.Row():
                                with gr.Column(scale=1):
                                    audio_input = gr.Audio(source="microphone", type="filepath", label="Record from microphone", elem_classes="audio-input")
                                with gr.Column(scale=1):
                                    audio_upload = gr.Audio(source="upload", type="filepath", label="Upload audio file", elem_classes="audio-input")
                            
                            submit_btn = gr.Button("🚀 Analyze My Speech", variant="primary")

                    with gr.Column(scale=1):
                        with gr.Box():
                            gr.Markdown("### 🌟 Performance Rating")
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

            with gr.TabItem("🎭 Interview Prep", id="interview"):
                with gr.Row():
                    with gr.Column(scale=1):
                        interview_topic = gr.Textbox(label="Interview Topic/Position")
                        personality_traits = gr.Textbox(label="Your Personality Traits")
                        technical_skills = gr.Textbox(label="Your Technical Skills")
                        interview_model = gr.Dropdown(choices=["mistral:latest", "llama3.2:latest", "qwen3:32b"], value="mistral:latest", label="AI Model")
                        generate_interview_btn = gr.Button("Generate Interview Questions", variant="primary")

                    with gr.Column(scale=1):
                        interview_questions = gr.Markdown("Your interview questions will appear here...")

            with gr.TabItem("📚 Your History", id="history"):
                with gr.Row():
                    with gr.Column(scale=1):
                        refresh_history_btn = gr.Button("Refresh History", variant="secondary")
                        history_display = gr.Markdown("Your practice history will appear here...")

        # === Events ===
        topic_choice.change(
            fn=lambda mode: (
                gr.update(visible=(mode == "Select from list")),
                gr.update(visible=(mode == "Enter custom topic")),
                gr.update(interactive=(mode == "Enter custom topic"))
            ),
            inputs=topic_choice,
            outputs=[topic_dropdown, custom_topic_box, question_box]
        )

        generate_btn.click(
            fn=update_current_topic,
            inputs=[topic_choice, topic_dropdown, custom_topic_box],
            outputs=[custom_topic_box, current_topic]
        ).then(
            fn=lambda m, q, t, d, mo: handle_question_generation(m, q, t, d, mo, handle_custom_question, generate_question_and_answer),
            inputs=[topic_choice, question_box, custom_topic_box, difficulty_selector, model_selector],
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

        # Function to process audio from either microphone or uploaded file
        def process_audio(mic_input, upload_input, question, ideal_answer, difficulty, model, user_id, topic):
            # Use uploaded file if available, otherwise use microphone input
            audio_input_to_use = upload_input if upload_input else mic_input
            return enhanced_tutor_conversation(
                audio_input_to_use, question, ideal_answer, difficulty, model, 
                user_id, topic, tutor_conversation, save_history, calculate_rating
            )
            
        submit_btn.click(
            fn=process_audio,
            inputs=[
                audio_input, audio_upload, question_state, ideal_answer_state, 
                difficulty_state, model_selector, user_id, current_topic
            ],
            outputs=[transcript_output, grammar_output, feedback_output, comparison_output, ideal_answer_box, rating_state, rating_display]
        ).then(
            lambda a: a,
            inputs=ideal_answer_box,
            outputs=ideal_answer_display
        )

        generate_interview_btn.click(
            lambda t, p, s, m: format_interview_questions(t, p, s, m, generate_interview_questions),
            inputs=[interview_topic, personality_traits, technical_skills, interview_model],
            outputs=interview_questions
        )

        refresh_history_btn.click(
            lambda u: format_history(u, load_history),
            inputs=user_id,
            outputs=history_display
        )

        app.load(
            lambda u: format_history(u, load_history),
            inputs=user_id,
            outputs=history_display
        )

    return app

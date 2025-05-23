# states.py — Defines all Gradio state variables for session tracking

import gradio as gr
import random

def init_states():
    return {
        "user_id": gr.State(value=f"user_{random.randint(1000, 9999)}"),
        "current_topic": gr.State(value=""),
        "question_state": gr.State(),
        "ideal_answer_state": gr.State(),
        "difficulty_state": gr.State(),
        "rating_state": gr.State(0.0),
    }

from string import Template
from llm_engine import call_ollama

def get_corrected_grammar(transcript, question=None, model="mistral:latest"):
    if not transcript:
        return "⚠️ No transcript found to correct."

    with open("prompts/correction_prompt.txt") as f:
        prompt_template = Template(f.read())

    prompt = prompt_template.substitute(
        transcript=transcript,
        question=question or "No specific question provided."
    )

    return call_ollama(prompt, model=model)

def get_speech_feedback(flagged_words, transcript=None, question=None, model="mistral:latest"):
    if not flagged_words:
        return "✅ Your speech was clear!"

    flagged = "\n".join([
        f'- "{w.strip()}" ({round(p * 100)}%) — Pronunciation below clarity threshold'
        for w, p in flagged_words
    ])

    with open("prompts/feedback_prompt.txt") as f:
        prompt_template = Template(f.read())

    prompt = prompt_template.substitute(
        flagged_words=flagged,
        transcript=transcript or "Transcript not available.",
        question=question or "No question provided."
    )

    return call_ollama(prompt, model=model)

def compare_answers(user_answer, ideal_answer, model="mistral:latest"):
    prompt = f"""
You are an English communication evaluator.

Compare the student's answer to the ideal answer.

User's Spoken Answer:
{user_answer}

Ideal Answer:
{ideal_answer}

Evaluate based on:
- Relevance to the question
- Structure and fluency
- Grammar and vocabulary

Then provide:
1. A short comparison
2. 2 suggestions to improve
"""
    return call_ollama(prompt, model=model)

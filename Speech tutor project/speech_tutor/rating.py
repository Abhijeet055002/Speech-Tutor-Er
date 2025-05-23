# rating.py — Defines the algorithm for calculating a 1.0–5.0 star rating

def calculate_rating(transcript, grammar, feedback, comparison):
    """
    Simple scoring logic to evaluate user's spoken answer based on:
    - Transcript length
    - Grammar correctness
    - Pronunciation quality
    - Relevance to ideal answer
    """
    if not transcript:
        return 0.0

    score = 3.0

    # Word count bonus
    word_count = len(transcript.split())
    if word_count > 50:
        score += 0.5
    elif word_count > 30:
        score += 0.3
    elif word_count > 15:
        score += 0.1

    # Grammar check
    grammar_l = grammar.lower()
    if "no grammar issues" in grammar_l or "excellent grammar" in grammar_l:
        score += 0.7
    elif "minor grammar issues" in grammar_l:
        score += 0.3
    elif "several grammar issues" in grammar_l:
        score -= 0.3
    else:
        score -= 0.5

    # Pronunciation feedback
    feedback_l = feedback.lower()
    if "excellent pronunciation" in feedback_l or "no pronunciation issues" in feedback_l:
        score += 0.5
    elif "minor pronunciation issues" in feedback_l:
        score += 0.2
    elif "several pronunciation issues" in feedback_l:
        score -= 0.2
    else:
        score -= 0.4

    # Comparison to ideal answer
    comparison_l = comparison.lower()
    if "excellent response" in comparison_l or "outstanding answer" in comparison_l:
        score += 1.0
    elif "good response" in comparison_l or "solid answer" in comparison_l:
        score += 0.5
    elif "adequate response" in comparison_l:
        score += 0.2
    elif "poor response" in comparison_l:
        score -= 0.5

    # Bound and return
    score = max(1.0, min(5.0, score))
    return round(score, 1)

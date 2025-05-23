# theme.py — Contains the UI theme and rating visual formatter

import gradio as gr

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


def format_star_rating(rating):
    full_stars = int(rating)
    half_star = rating - full_stars >= 0.5
    empty_stars = 5 - full_stars - (1 if half_star else 0)

    stars_html = ""
    for _ in range(full_stars):
        stars_html += '<span style="color: gold; font-size: 24px;">★</span>'
    if half_star:
        stars_html += '<span style="color: gold; font-size: 24px;">⯨</span>'
    for _ in range(empty_stars):
        stars_html += '<span style="color: #ccc; font-size: 24px;">☆</span>'

    return f'<div style="text-align: center;">{stars_html} <span style="font-size: 20px; vertical-align: middle; margin-left: 10px;">{rating}/5.0</span></div>'

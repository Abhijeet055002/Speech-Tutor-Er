# components.py — Header HTML and mic animation visuals

def header_section():
    return """
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
    """

def mic_wave_animation():
    return """
    <style>
    @keyframes pulse {
        0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(79, 70, 229, 0.7); }
        70% { transform: scale(1); box-shadow: 0 0 0 15px rgba(79, 70, 229, 0); }
        100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(79, 70, 229, 0); }
    }
    .pulse-circle {
        background: rgba(79, 70, 229, 0.3);
        border-radius: 50%;
        height: 100px;
        width: 100px;
        margin: 0 auto;
        animation: pulse 2s infinite;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    .mic-icon {
        color: #4F46E5;
        font-size: 40px;
    }
    </style>
    <div style="text-align: center; margin-top: 10px;">
        <div class="pulse-circle">
            <div class="mic-icon">🎤</div>
        </div>
        <p style="font-style: italic; color: #4B5563; margin-top: 10px;">Click microphone to start/stop recording</p>
    </div>
    """

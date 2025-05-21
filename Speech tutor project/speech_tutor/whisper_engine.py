from faster_whisper import WhisperModel

# old (float16 on CPU)
# Option A: use float32 (full precision)
model = WhisperModel("base.en", device="cpu", compute_type="float32")



def transcribe(audio_path):
    print("⚙️ Received audio:", audio_path)
    segments, _ = model.transcribe(audio_path, beam_size=5, word_timestamps=True)

    result = ""
    flagged_words = []

    for segment in segments:
        print("🧠 Segment:", segment)
        if not segment.words:
            continue
        result += segment.text + " "
        for word in segment.words:
            print(f"🔍 Word: {word.word} — Prob: {word.probability}")
            if word.probability and word.probability < 0.85:
                flagged_words.append((word.word, word.probability))

    print("📋 Final transcript:", result.strip())
    print("🚩 Flagged words:", flagged_words)

    return result.strip(), flagged_words

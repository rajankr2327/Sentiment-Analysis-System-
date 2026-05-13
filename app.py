# Sentiment Analysis System - Advanced Version
# Internship Project - Built with Python

from textblob import TextBlob
import gradio as gr

def analyze_sentiment(text):
    if not text.strip():
        return "⚠️ Please enter some text.", "", "", "", ""

    blob = TextBlob(text)
    polarity = blob.sentiment.polarity
    subjectivity = blob.sentiment.subjectivity

    # Detect detailed emotion based on polarity + subjectivity
    if polarity >= 0.6:
        emotion = "🤩 ECSTATIC"
        emotion_desc = "Extremely happy and excited!"
    elif polarity >= 0.3:
        emotion = "😊 HAPPY"
        emotion_desc = "Positive and cheerful tone."
    elif polarity >= 0.1:
        emotion = "🙂 CONTENT"
        emotion_desc = "Mildly positive and satisfied."
    elif polarity > -0.1:
        if subjectivity < 0.3:
            emotion = "😐 NEUTRAL"
            emotion_desc = "Objective and factual tone."
        else:
            emotion = "😶 INDIFFERENT"
            emotion_desc = "No strong feeling detected."
    elif polarity >= -0.3:
        emotion = "😟 UNHAPPY"
        emotion_desc = "Mildly negative tone."
    elif polarity >= -0.6:
        emotion = "😠 ANGRY"
        emotion_desc = "Strong negative and frustrated tone."
    else:
        emotion = "😡 FURIOUS"
        emotion_desc = "Extremely negative and intense!"

    # Detect extra emotional traits
    traits = []
    if subjectivity > 0.7:
        traits.append("💭 Highly Opinionated")
    elif subjectivity < 0.3:
        traits.append("📰 Very Objective / Factual")

    if len(text.split()) < 5:
        traits.append("⚡ Very Short Text")
    if text.isupper():
        traits.append("🔊 ALL CAPS — Strong Emphasis")
    if "!" in text:
        traits.append("❗ Exclamation Detected — High Intensity")
    if "?" in text:
        traits.append("❓ Question Detected — Uncertainty")
    if any(word in text.lower() for word in ["love", "amazing", "fantastic", "excellent", "great"]):
        traits.append("💖 Strong Positive Words")
    if any(word in text.lower() for word in ["hate", "terrible", "awful", "horrible", "worst"]):
        traits.append("💢 Strong Negative Words")
    if any(word in text.lower() for word in ["sad", "cry", "depressed", "lonely", "miss"]):
        traits.append("😢 Sadness Detected")
    if any(word in text.lower() for word in ["scared", "afraid", "fear", "nervous", "anxious"]):
        traits.append("😨 Fear / Anxiety Detected")
    if any(word in text.lower() for word in ["surprise", "wow", "omg", "unbelievable", "shocked"]):
        traits.append("😲 Surprise Detected")

    traits_str = "\n".join(traits) if traits else "No special traits detected."
    polarity_str = f"{polarity:.2f}  (Scale: -1.0 Negative ← 0 → +1.0 Positive)"
    subjectivity_str = f"{subjectivity:.2f}  (0.0 = Fully Objective, 1.0 = Fully Subjective)"
    full_emotion = f"{emotion}\n{emotion_desc}"

    return full_emotion, polarity_str, subjectivity_str, traits_str


# Build the web interface
interface = gr.Interface(
    fn=analyze_sentiment,
    inputs=gr.Textbox(
        lines=6,
        placeholder="Type or paste any text here... (review, tweet, comment, sentence)",
        label="📝 Enter Your Text"
    ),
    outputs=[
        gr.Textbox(label="🎭 Detected Emotion"),
        gr.Textbox(label="📊 Polarity Score"),
        gr.Textbox(label="🧠 Subjectivity Score"),
        gr.Textbox(label="🔍 Emotional Traits"),
    ],
    title="🧠 AI Emotion & Sentiment Analysis System",
    description="Enter any text and the AI will detect detailed emotions, polarity, subjectivity and special traits!",
    examples=[
        ["I absolutely LOVE this product! It is AMAZING and exceeded all my expectations!!"],
        ["This is the worst experience I have ever had. Totally horrible and disgusting."],
        ["The report was submitted on Monday at 9am."],
        ["I am so scared and nervous about the exam tomorrow."],
        ["OMG I can't believe this happened! I am completely shocked!"],
        ["I miss my family so much, feeling very lonely today."],
        ["The movie was okay, nothing special but not bad either."],
        ["I HATE this!! Worst decision EVER!!!"],
    ],
    theme=gr.themes.Soft()
)

if __name__ == "__main__":
    interface.launch()
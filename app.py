# Sentiment Analysis System
# Internship Project - Built with Python

from textblob import TextBlob
import gradio as gr

def analyze_sentiment(text):
    """
    Analyzes the sentiment of the given text.
    Returns polarity, subjectivity, and a label.
    """
    if not text.strip():
        return "⚠️ Please enter some text.", "", ""

    blob = TextBlob(text)
    polarity = blob.sentiment.polarity        # -1 (negative) to +1 (positive)
    subjectivity = blob.sentiment.subjectivity  # 0 (objective) to 1 (subjective)

    # Determine sentiment label
    if polarity > 0.1:
        label = "😊 POSITIVE"
    elif polarity < -0.1:
        label = "😞 NEGATIVE"
    else:
        label = "😐 NEUTRAL"

    polarity_str = f"{polarity:.2f} (Range: -1 to +1)"
    subjectivity_str = f"{subjectivity:.2f} (0 = Objective, 1 = Subjective)"

    return label, polarity_str, subjectivity_str


# Build the web interface
interface = gr.Interface(
    fn=analyze_sentiment,
    inputs=gr.Textbox(
        lines=5,
        placeholder="Type or paste any text here... (e.g. a product review, tweet, etc.)",
        label="Enter Text"
    ),
    outputs=[
        gr.Textbox(label="Sentiment"),
        gr.Textbox(label="Polarity Score"),
        gr.Textbox(label="Subjectivity Score"),
    ],
    title="🧠 AI Sentiment Analysis System",
    description="Enter any text and the AI will detect if it's Positive, Negative, or Neutral.",
    examples=[
        ["I absolutely love this product! It works perfectly and exceeded my expectations."],
        ["This is the worst experience I have ever had. Totally disappointed."],
        ["The package was delivered on time."],
        ["The movie was okay, nothing special but not bad either."],
    ]
)

if __name__ == "__main__":
    interface.launch()
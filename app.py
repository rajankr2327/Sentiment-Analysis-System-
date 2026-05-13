# Sentiment Analysis System - ULTIMATE Version
# Internship Project - Built with Python

from textblob import TextBlob
import gradio as gr
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
from googletrans import Translator
import io
import tempfile
import os

translator = Translator()

def detect_emotion(polarity, subjectivity, text):
    traits = []

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

    if subjectivity > 0.7:
        traits.append("💭 Highly Opinionated")
    elif subjectivity < 0.3:
        traits.append("📰 Very Objective / Factual")
    if text.isupper():
        traits.append("🔊 ALL CAPS — Strong Emphasis")
    if "!" in text:
        traits.append("❗ High Intensity")
    if "?" in text:
        traits.append("❓ Uncertainty Detected")
    if any(w in text.lower() for w in ["love","amazing","fantastic","excellent","great"]):
        traits.append("💖 Strong Positive Words")
    if any(w in text.lower() for w in ["hate","terrible","awful","horrible","worst"]):
        traits.append("💢 Strong Negative Words")
    if any(w in text.lower() for w in ["sad","cry","depressed","lonely","miss"]):
        traits.append("😢 Sadness Detected")
    if any(w in text.lower() for w in ["scared","afraid","fear","nervous","anxious"]):
        traits.append("😨 Fear / Anxiety Detected")
    if any(w in text.lower() for w in ["surprise","wow","omg","unbelievable","shocked"]):
        traits.append("😲 Surprise Detected")

    return emotion, emotion_desc, traits


def make_chart(polarity, subjectivity):
    fig, axes = plt.subplots(1, 2, figsize=(10, 4))
    fig.patch.set_facecolor('#f9f9f9')

    # Polarity bar
    pol_color = '#4CAF50' if polarity >= 0.1 else ('#f44336' if polarity <= -0.1 else '#FF9800')
    axes[0].barh(['Polarity'], [polarity], color=pol_color, height=0.4)
    axes[0].set_xlim(-1, 1)
    axes[0].axvline(0, color='black', linewidth=0.8, linestyle='--')
    axes[0].set_title('Polarity Score', fontsize=13, fontweight='bold')
    axes[0].set_xlabel('Negative  ←  0  →  Positive')
    axes[0].text(polarity, 0, f'  {polarity:.2f}', va='center', fontweight='bold')

    # Subjectivity bar
    sub_color = '#2196F3' if subjectivity < 0.5 else '#9C27B0'
    axes[1].barh(['Subjectivity'], [subjectivity], color=sub_color, height=0.4)
    axes[1].set_xlim(0, 1)
    axes[1].set_title('Subjectivity Score', fontsize=13, fontweight='bold')
    axes[1].set_xlabel('Objective  ←  0.5  →  Subjective')
    axes[1].text(subjectivity, 0, f'  {subjectivity:.2f}', va='center', fontweight='bold')

    plt.tight_layout()
    return fig


def analyze_single(text, language):
    if not text.strip():
        return "⚠️ Please enter some text.", "", "", "", None

    # Translate if needed
    translated = text
    if language != "English":
        try:
            translated = translator.translate(text, dest='en').text
        except:
            translated = text

    blob = TextBlob(translated)
    polarity = blob.sentiment.polarity
    subjectivity = blob.sentiment.subjectivity

    emotion, emotion_desc, traits = detect_emotion(polarity, subjectivity, translated)
    traits_str = "\n".join(traits) if traits else "No special traits detected."
    full_emotion = f"{emotion}\n{emotion_desc}"
    polarity_str = f"{polarity:.2f}  (Scale: -1.0 Negative ← 0 → +1.0 Positive)"
    subjectivity_str = f"{subjectivity:.2f}  (0.0 = Fully Objective, 1.0 = Fully Subjective)"
    chart = make_chart(polarity, subjectivity)

    return full_emotion, polarity_str, subjectivity_str, traits_str, chart


def analyze_csv(file, language):
    if file is None:
        return None, None, "⚠️ Please upload a CSV file."

    try:
        df = pd.read_csv(file.name)
    except Exception as e:
        return None, None, f"❌ Error reading file: {e}"

    text_col = None
    for col in df.columns:
        if 'review' in col.lower() or 'text' in col.lower() or 'comment' in col.lower() or 'feedback' in col.lower():
            text_col = col
            break
    if text_col is None:
        text_col = df.columns[0]

    results = []
    emotion_counts = {}

    for idx, row in df.iterrows():
        text = str(row[text_col])
        translated = text
        if language != "English":
            try:
                translated = translator.translate(text, dest='en').text
            except:
                translated = text

        blob = TextBlob(translated)
        polarity = blob.sentiment.polarity
        subjectivity = blob.sentiment.subjectivity
        emotion, emotion_desc, traits = detect_emotion(polarity, subjectivity, translated)

        emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1
        results.append({
            "Original Text": text,
            "Emotion": emotion,
            "Emotion Description": emotion_desc,
            "Polarity": round(polarity, 2),
            "Subjectivity": round(subjectivity, 2),
            "Traits": ", ".join(traits) if traits else "None"
        })

    results_df = pd.DataFrame(results)

    # Save Excel
    with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp:
        excel_path = tmp.name
    results_df.to_excel(excel_path, index=False)

    # Emotion distribution chart
    fig, ax = plt.subplots(figsize=(10, 5))
    fig.patch.set_facecolor('#f9f9f9')
    colors = ['#4CAF50','#8BC34A','#CDDC39','#FF9800','#FF5722','#f44336','#9C27B0','#2196F3','#00BCD4','#795548']
    bars = ax.bar(list(emotion_counts.keys()), list(emotion_counts.values()),
                  color=colors[:len(emotion_counts)])
    ax.set_title('Emotion Distribution Across All Reviews', fontsize=14, fontweight='bold')
    ax.set_xlabel('Emotion')
    ax.set_ylabel('Count')
    plt.xticks(rotation=30, ha='right')
    for bar, count in zip(bars, emotion_counts.values()):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1,
                str(count), ha='center', fontweight='bold')
    plt.tight_layout()

    summary = f"✅ Analyzed {len(results)} reviews successfully!\n\n"
    summary += "📊 Emotion Breakdown:\n"
    for emotion, count in sorted(emotion_counts.items(), key=lambda x: -x[1]):
        summary += f"  {emotion}: {count} reviews\n"

    return fig, excel_path, summary


# ─── Build UI ───────────────────────────────────────────────────────

language_choices = [
    "English", "Hindi", "Spanish", "French",
    "German", "Arabic", "Portuguese", "Japanese", "Chinese"
]

with gr.Blocks(theme=gr.themes.Soft(), title="🧠 AI Emotion Analyzer") as app:

    gr.Markdown("# 🧠 AI Emotion & Sentiment Analysis System")
    gr.Markdown("Analyze emotions in **single text** or **bulk CSV files** with multi-language support!")

    with gr.Tabs():

        # ── Tab 1: Single Text ──────────────────────────────────────
        with gr.Tab("📝 Single Text Analysis"):
            with gr.Row():
                with gr.Column():
                    text_input = gr.Textbox(
                        lines=6,
                        placeholder="Type or paste any text here...",
                        label="Enter Your Text"
                    )
                    lang_input = gr.Dropdown(
                        choices=language_choices,
                        value="English",
                        label="🌍 Select Input Language"
                    )
                    analyze_btn = gr.Button("🔍 Analyze", variant="primary")

                with gr.Column():
                    emotion_out = gr.Textbox(label="🎭 Detected Emotion")
                    polarity_out = gr.Textbox(label="📊 Polarity Score")
                    subjectivity_out = gr.Textbox(label="🧠 Subjectivity Score")
                    traits_out = gr.Textbox(label="🔍 Emotional Traits", lines=5)

            chart_out = gr.Plot(label="📈 Score Visualization")

            analyze_btn.click(
                fn=analyze_single,
                inputs=[text_input, lang_input],
                outputs=[emotion_out, polarity_out, subjectivity_out, traits_out, chart_out]
            )

            gr.Examples(
                examples=[
                    ["I absolutely LOVE this product! It is AMAZING!!", "English"],
                    ["यह बहुत बुरा अनुभव था। मुझे बिल्कुल पसंद नहीं आया।", "Hindi"],
                    ["Este producto es increíble, lo recomiendo mucho!", "Spanish"],
                    ["I am so scared and nervous about the exam tomorrow.", "English"],
                    ["OMG I can't believe this! I am completely shocked!", "English"],
                ],
                inputs=[text_input, lang_input]
            )

        # ── Tab 2: CSV Bulk Analysis ────────────────────────────────
        with gr.Tab("📁 Bulk CSV Analysis"):
            gr.Markdown("### Upload a CSV file with a column named `review`, `text`, `comment`, or `feedback`")
            with gr.Row():
                with gr.Column():
                    csv_input = gr.File(label="📂 Upload CSV File", file_types=[".csv"])
                    csv_lang = gr.Dropdown(
                        choices=language_choices,
                        value="English",
                        label="🌍 Select Input Language"
                    )
                    csv_btn = gr.Button("🔍 Analyze CSV", variant="primary")

                with gr.Column():
                    csv_summary = gr.Textbox(label="📋 Analysis Summary", lines=10)
                    csv_download = gr.File(label="📥 Download Excel Results")

            csv_chart = gr.Plot(label="📊 Emotion Distribution Chart")

            csv_btn.click(
                fn=analyze_csv,
                inputs=[csv_input, csv_lang],
                outputs=[csv_chart, csv_download, csv_summary]
            )

if __name__ == "__main__":
    app.launch()
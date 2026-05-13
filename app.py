# Sentiment Analysis System - ULTIMATE PRO Version
# Internship Project - Built with Python

from textblob import TextBlob
import gradio as gr
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from deep_translator import GoogleTranslator
from wordcloud import WordCloud
import tempfile
import requests
from bs4 import BeautifulSoup

# ─── Core Functions ──────────────────────────────────────────────────

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


def get_ai_suggestion(emotion, polarity):
    suggestions = {
        "🤩 ECSTATIC": "🌟 You're on fire! Share this energy with your team. Great time to tackle big challenges!",
        "😊 HAPPY": "✅ Great mindset! This is a perfect time to be productive and creative.",
        "🙂 CONTENT": "👍 You're in a good place. Keep it up and stay consistent!",
        "😐 NEUTRAL": "📌 Try adding more emotion or detail to make your message more impactful.",
        "😶 INDIFFERENT": "💡 Consider being more specific about your feelings or opinions.",
        "😟 UNHAPPY": "🤝 It's okay to feel this way. Talk to someone you trust or take a short break.",
        "😠 ANGRY": "🧘 Take a deep breath before responding. Anger can cloud clear thinking.",
        "😡 FURIOUS": "⚠️ Very strong emotions detected. Step away and calm down before taking any action.",
    }
    return suggestions.get(emotion, "💬 Keep expressing yourself clearly and honestly!")


def make_chart(polarity, subjectivity):
    fig, axes = plt.subplots(1, 2, figsize=(10, 4))
    fig.patch.set_facecolor('#f9f9f9')

    pol_color = '#4CAF50' if polarity >= 0.1 else ('#f44336' if polarity <= -0.1 else '#FF9800')
    axes[0].barh(['Polarity'], [polarity], color=pol_color, height=0.4)
    axes[0].set_xlim(-1, 1)
    axes[0].axvline(0, color='black', linewidth=0.8, linestyle='--')
    axes[0].set_title('Polarity Score', fontsize=13, fontweight='bold')
    axes[0].set_xlabel('Negative  ←  0  →  Positive')
    axes[0].text(polarity, 0, f'  {polarity:.2f}', va='center', fontweight='bold')

    sub_color = '#2196F3' if subjectivity < 0.5 else '#9C27B0'
    axes[1].barh(['Subjectivity'], [subjectivity], color=sub_color, height=0.4)
    axes[1].set_xlim(0, 1)
    axes[1].set_title('Subjectivity Score', fontsize=13, fontweight='bold')
    axes[1].set_xlabel('Objective  ←  0.5  →  Subjective')
    axes[1].text(subjectivity, 0, f'  {subjectivity:.2f}', va='center', fontweight='bold')

    plt.tight_layout()
    return fig


# ─── Tab Functions ───────────────────────────────────────────────────

def analyze_single(text, language):
    if not text.strip():
        return "⚠️ Please enter some text.", "", "", "", "", None

    translated = text
    if language != "English":
        try:
            translated = GoogleTranslator(source='auto', target='en').translate(text)
        except:
            translated = text

    blob = TextBlob(translated)
    polarity = blob.sentiment.polarity
    subjectivity = blob.sentiment.subjectivity

    emotion, emotion_desc, traits = detect_emotion(polarity, subjectivity, translated)
    suggestion = get_ai_suggestion(emotion, polarity)
    traits_str = "\n".join(traits) if traits else "No special traits detected."
    full_emotion = f"{emotion}\n{emotion_desc}"
    polarity_str = f"{polarity:.2f}  (Scale: -1.0 Negative ← 0 → +1.0 Positive)"
    subjectivity_str = f"{subjectivity:.2f}  (0.0 = Fully Objective, 1.0 = Fully Subjective)"
    chart = make_chart(polarity, subjectivity)

    return full_emotion, polarity_str, subjectivity_str, traits_str, suggestion, chart


def analyze_url(url):
    if not url.strip():
        return "⚠️ Please enter a URL.", "", "", "", None

    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url.strip(), headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        paragraphs = soup.find_all('p')
        text = " ".join([p.get_text() for p in paragraphs[:20]])
        if not text.strip():
            return "❌ Could not extract text from this URL.", "", "", "", None
    except Exception as e:
        return f"❌ Error fetching URL: {e}", "", "", "", None

    blob = TextBlob(text)
    polarity = blob.sentiment.polarity
    subjectivity = blob.sentiment.subjectivity

    emotion, emotion_desc, traits = detect_emotion(polarity, subjectivity, text)
    suggestion = get_ai_suggestion(emotion, polarity)
    traits_str = "\n".join(traits) if traits else "No special traits."
    summary = f"🎭 Emotion: {emotion}\n📝 {emotion_desc}\n\n📊 Polarity: {polarity:.2f}\n🧠 Subjectivity: {subjectivity:.2f}\n\n🔍 Traits:\n{traits_str}\n\n🤖 AI Suggestion:\n{suggestion}"
    chart = make_chart(polarity, subjectivity)

    preview = text[:500] + "..." if len(text) > 500 else text

    return summary, preview, chart


def analyze_csv(file, language):
    if file is None:
        return None, None, None, "⚠️ Please upload a CSV file."

    try:
        df = pd.read_csv(file.name)
    except Exception as e:
        return None, None, None, f"❌ Error reading file: {e}"

    text_col = None
    for col in df.columns:
        if any(k in col.lower() for k in ['review','text','comment','feedback']):
            text_col = col
            break
    if text_col is None:
        text_col = df.columns[0]

    results = []
    emotion_counts = {}
    polarities = []
    all_text = ""

    for idx, row in df.iterrows():
        text = str(row[text_col])
        translated = text
        if language != "English":
            try:
                translated = GoogleTranslator(source='auto', target='en').translate(text)
            except:
                translated = text

        blob = TextBlob(translated)
        polarity = blob.sentiment.polarity
        subjectivity = blob.sentiment.subjectivity
        emotion, emotion_desc, traits = detect_emotion(polarity, subjectivity, translated)

        emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1
        polarities.append(polarity)
        all_text += " " + translated

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
    fig1, ax1 = plt.subplots(figsize=(10, 5))
    fig1.patch.set_facecolor('#f9f9f9')
    colors = ['#4CAF50','#8BC34A','#CDDC39','#FF9800','#FF5722','#f44336','#9C27B0','#2196F3','#00BCD4','#795548']
    bars = ax1.bar(list(emotion_counts.keys()), list(emotion_counts.values()), color=colors[:len(emotion_counts)])
    ax1.set_title('Emotion Distribution Across All Reviews', fontsize=14, fontweight='bold')
    ax1.set_xlabel('Emotion')
    ax1.set_ylabel('Count')
    plt.xticks(rotation=30, ha='right')
    for bar, count in zip(bars, emotion_counts.values()):
        ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1, str(count), ha='center', fontweight='bold')
    plt.tight_layout()

    # Sentiment trend line
    fig2, ax2 = plt.subplots(figsize=(10, 4))
    fig2.patch.set_facecolor('#f9f9f9')
    ax2.plot(range(1, len(polarities)+1), polarities, marker='o', color='#2196F3', linewidth=2, markersize=5)
    ax2.axhline(0, color='red', linestyle='--', linewidth=1)
    ax2.fill_between(range(1, len(polarities)+1), polarities, 0,
                     where=[p >= 0 for p in polarities], alpha=0.2, color='green', label='Positive')
    ax2.fill_between(range(1, len(polarities)+1), polarities, 0,
                     where=[p < 0 for p in polarities], alpha=0.2, color='red', label='Negative')
    ax2.set_title('Sentiment Trend Across Reviews', fontsize=14, fontweight='bold')
    ax2.set_xlabel('Review Number')
    ax2.set_ylabel('Polarity Score')
    ax2.legend()
    plt.tight_layout()

    # Word Cloud
    fig3, ax3 = plt.subplots(figsize=(10, 5))
    fig3.patch.set_facecolor('#f9f9f9')
    wc = WordCloud(width=800, height=400, background_color='white',
                   colormap='RdYlGn', max_words=100).generate(all_text)
    ax3.imshow(wc, interpolation='bilinear')
    ax3.axis('off')
    ax3.set_title('Word Cloud of All Reviews', fontsize=14, fontweight='bold')
    plt.tight_layout()

    summary = f"✅ Analyzed {len(results)} reviews!\n\n"
    summary += "📊 Emotion Breakdown:\n"
    for emotion, count in sorted(emotion_counts.items(), key=lambda x: -x[1]):
        summary += f"  {emotion}: {count}\n"
    avg_pol = sum(polarities) / len(polarities)
    summary += f"\n📈 Average Polarity: {avg_pol:.2f}"
    summary += f"\n🏆 Overall Mood: {'Positive 😊' if avg_pol > 0.1 else 'Negative 😞' if avg_pol < -0.1 else 'Neutral 😐'}"

    return fig1, fig2, fig3, excel_path, summary


# ─── Build UI ────────────────────────────────────────────────────────

language_choices = ["English","Hindi","Spanish","French","German","Arabic","Portuguese","Japanese","Chinese"]

with gr.Blocks(theme=gr.themes.Soft(), title="🧠 AI Emotion Analyzer Pro") as app:

    gr.Markdown("# 🧠 AI Emotion & Sentiment Analysis System — Pro")
    gr.Markdown("Analyze emotions from **text, voice, URLs, or bulk CSV files** with charts, word clouds & AI suggestions!")

    with gr.Tabs():

        # ── Tab 1: Single Text ──────────────────────────────────────
        with gr.Tab("📝 Single Text"):
            with gr.Row():
                with gr.Column():
                    text_input = gr.Textbox(lines=6, placeholder="Type or paste any text here...", label="Enter Your Text")
                    lang_input = gr.Dropdown(choices=language_choices, value="English", label="🌍 Language")
                    analyze_btn = gr.Button("🔍 Analyze", variant="primary")
                with gr.Column():
                    emotion_out = gr.Textbox(label="🎭 Detected Emotion")
                    polarity_out = gr.Textbox(label="📊 Polarity Score")
                    subjectivity_out = gr.Textbox(label="🧠 Subjectivity Score")
                    traits_out = gr.Textbox(label="🔍 Emotional Traits", lines=4)
                    suggestion_out = gr.Textbox(label="🤖 AI Suggestion", lines=3)
            chart_out = gr.Plot(label="📈 Score Visualization")

            analyze_btn.click(
                fn=analyze_single,
                inputs=[text_input, lang_input],
                outputs=[emotion_out, polarity_out, subjectivity_out, traits_out, suggestion_out, chart_out]
            )
            gr.Examples(
                examples=[
                    ["I absolutely LOVE this product! It is AMAZING!!", "English"],
                    ["यह बहुत बुरा अनुभव था। मुझे बिल्कुल पसंद नहीं आया।", "Hindi"],
                    ["Este producto es increíble!", "Spanish"],
                    ["I am so scared and nervous about tomorrow.", "English"],
                ],
                inputs=[text_input, lang_input]
            )

        # ── Tab 2: News URL ─────────────────────────────────────────
        with gr.Tab("📰 Analyze News URL"):
            gr.Markdown("### Paste any news article or blog URL to analyze its sentiment!")
            url_input = gr.Textbox(placeholder="https://example.com/news-article", label="🔗 Enter URL")
            url_btn = gr.Button("🔍 Analyze URL", variant="primary")
            url_summary = gr.Textbox(label="📋 Full Analysis", lines=12)
            url_preview = gr.Textbox(label="📄 Extracted Text Preview", lines=5)
            url_chart = gr.Plot(label="📊 Sentiment Chart")

            url_btn.click(
                fn=analyze_url,
                inputs=[url_input],
                outputs=[url_summary, url_preview, url_chart]
            )
            gr.Examples(
                examples=[
                    ["https://www.bbc.com/news"],
                    ["https://techcrunch.com"],
                ],
                inputs=[url_input]
            )

        # ── Tab 3: CSV Bulk ─────────────────────────────────────────
        with gr.Tab("📁 Bulk CSV Analysis"):
            gr.Markdown("### Upload CSV with a column named `review`, `text`, `comment`, or `feedback`")
            with gr.Row():
                with gr.Column():
                    csv_input = gr.File(label="📂 Upload CSV File", file_types=[".csv"])
                    csv_lang = gr.Dropdown(choices=language_choices, value="English", label="🌍 Language")
                    csv_btn = gr.Button("🔍 Analyze CSV", variant="primary")
                with gr.Column():
                    csv_summary = gr.Textbox(label="📋 Summary", lines=12)
                    csv_download = gr.File(label="📥 Download Excel Results")

            with gr.Row():
                csv_chart1 = gr.Plot(label="📊 Emotion Distribution")
                csv_chart2 = gr.Plot(label="📈 Sentiment Trend")
            csv_chart3 = gr.Plot(label="☁️ Word Cloud")

            csv_btn.click(
                fn=analyze_csv,
                inputs=[csv_input, csv_lang],
                outputs=[csv_chart1, csv_chart2, csv_chart3, csv_download, csv_summary]
            )

if __name__ == "__main__":
    app.launch()
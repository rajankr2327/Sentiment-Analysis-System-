<<<<<<< HEAD
# ============================================================
# 🧠 AI Sentiment & Emotion Analysis — ULTIMATE PRO MAX v3
# Features: Voice, Chatbot, Deep Learning, Mobile UI,
#           Dashboard, PDF, CSV, Compare, Toxicity, Fake News
# FIXED: Chatbot tuple→dict format, File type, PDF output
# ============================================================

from textblob import TextBlob
import gradio as gr
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from deep_translator import GoogleTranslator
from wordcloud import WordCloud
import tempfile, requests, os, emoji
from bs4 import BeautifulSoup
from fpdf import FPDF
import PyPDF2
from transformers import pipeline

# ─── Load Deep Learning Model ────────────────────────────────
print("⏳ Loading Deep Learning model...")
try:
    dl_sentiment = pipeline(
        "sentiment-analysis",
        model="distilbert-base-uncased-finetuned-sst-2-english",
        truncation=True, max_length=512
    )
    DL_AVAILABLE = True
    print("✅ Deep Learning model loaded!")
except Exception as e:
    DL_AVAILABLE = False
    print(f"⚠️ DL model unavailable: {e}")

# ─── History & Chat Store ────────────────────────────────────
history_store = []
chat_history   = []

language_choices = [
    "Auto Detect","English","Hindi","Spanish","French",
    "German","Arabic","Portuguese","Japanese","Chinese"
]

# ─── Core Functions ──────────────────────────────────────────
def detect_emotion(polarity, subjectivity, text):
    traits = []
    if polarity >= 0.6:     emotion, desc = "🤩 ECSTATIC",    "Extremely happy and excited!"
    elif polarity >= 0.3:   emotion, desc = "😊 HAPPY",        "Positive and cheerful tone."
    elif polarity >= 0.1:   emotion, desc = "🙂 CONTENT",      "Mildly positive and satisfied."
    elif polarity > -0.1:
        if subjectivity < 0.3: emotion, desc = "😐 NEUTRAL",   "Objective and factual tone."
        else:                   emotion, desc = "😶 INDIFFERENT","No strong feeling detected."
    elif polarity >= -0.3:  emotion, desc = "😟 UNHAPPY",      "Mildly negative tone."
    elif polarity >= -0.6:  emotion, desc = "😠 ANGRY",        "Strong negative and frustrated."
    else:                   emotion, desc = "😡 FURIOUS",       "Extremely negative and intense!"

    if subjectivity > 0.7:  traits.append("💭 Highly Opinionated")
    elif subjectivity < 0.3: traits.append("📰 Very Objective")
    if text.isupper():       traits.append("🔊 ALL CAPS — Strong Emphasis")
    if "!" in text:          traits.append("❗ High Intensity")
    if "?" in text:          traits.append("❓ Uncertainty Detected")
    for w in ["love","amazing","fantastic","excellent","great"]:
        if w in text.lower(): traits.append("💖 Strong Positive Words"); break
    for w in ["hate","terrible","awful","horrible","worst"]:
        if w in text.lower(): traits.append("💢 Strong Negative Words"); break
    for w in ["sad","cry","depressed","lonely","miss"]:
        if w in text.lower(): traits.append("😢 Sadness Detected"); break
    for w in ["scared","afraid","fear","nervous","anxious"]:
        if w in text.lower(): traits.append("😨 Fear/Anxiety Detected"); break
    for w in ["surprise","wow","omg","unbelievable","shocked"]:
        if w in text.lower(): traits.append("😲 Surprise Detected"); break

    emojis_found = [c for c in text if c in emoji.EMOJI_DATA]
    if emojis_found:
        traits.append(f"🎭 Emojis: {' '.join(emojis_found[:5])}")

    return emotion, desc, traits


def get_suggestion(emotion):
    s = {
        "🤩 ECSTATIC":    "🌟 You're on fire! Great time to tackle big challenges!",
        "😊 HAPPY":       "✅ Great mindset! Perfect time to be productive.",
        "🙂 CONTENT":     "👍 You're in a good place. Keep it up!",
        "😐 NEUTRAL":     "📌 Try adding more detail to be more impactful.",
        "😶 INDIFFERENT": "💡 Consider being more specific about your feelings.",
        "😟 UNHAPPY":     "🤝 Talk to someone you trust or take a short break.",
        "😠 ANGRY":       "🧘 Take a deep breath before responding.",
        "😡 FURIOUS":     "⚠️ Step away and calm down before taking action.",
    }
    return s.get(emotion, "💬 Keep expressing yourself clearly!")


def check_toxicity(text):
    toxic = ["kill","hate","stupid","idiot","dumb","loser","trash","worthless","shut up","die"]
    found = [w for w in toxic if w in text.lower()]
    return f"⚠️ Toxic language: {', '.join(found)}" if found else "✅ No toxic language detected."


def check_fake_news(text):
    signals = ["breaking","exclusive","shocking","you won't believe","share before deleted",
               "mainstream media won't tell","secret","hidden truth","guaranteed","100%"]
    found = [s for s in signals if s in text.lower()]
    if len(found) >= 2:   return f"🚨 Fake news signals: {', '.join(found)}"
    elif len(found) == 1: return f"⚠️ Mild clickbait: '{found[0]}'"
    return "✅ No fake news signals."


def make_bar_chart(polarity, subjectivity):
    bg = "#e8f5e9" if polarity >= 0.3 else "#fff9c4" if polarity > -0.1 else "#ffebee"
    fig, axes = plt.subplots(1, 2, figsize=(10, 4))
    fig.patch.set_facecolor(bg)
    pol_color = '#4CAF50' if polarity >= 0.1 else ('#f44336' if polarity <= -0.1 else '#FF9800')
    axes[0].barh(['Polarity'], [polarity], color=pol_color, height=0.4)
    axes[0].set_xlim(-1, 1); axes[0].axvline(0, color='black', linewidth=0.8, linestyle='--')
    axes[0].set_title('Polarity Score', fontweight='bold')
    axes[0].set_xlabel('Negative ← 0 → Positive')
    axes[0].text(polarity, 0, f'  {polarity:.2f}', va='center', fontweight='bold')
    sub_color = '#2196F3' if subjectivity < 0.5 else '#9C27B0'
    axes[1].barh(['Subjectivity'], [subjectivity], color=sub_color, height=0.4)
    axes[1].set_xlim(0, 1)
    axes[1].set_title('Subjectivity Score', fontweight='bold')
    axes[1].set_xlabel('Objective ← 0.5 → Subjective')
    axes[1].text(subjectivity, 0, f'  {subjectivity:.2f}', va='center', fontweight='bold')
    plt.tight_layout(); return fig


def make_pie_chart(emotion_counts):
    fig, ax = plt.subplots(figsize=(7, 7))
    colors = ['#4CAF50','#8BC34A','#CDDC39','#FF9800','#FF5722','#f44336','#9C27B0','#2196F3','#00BCD4']
    ax.pie(list(emotion_counts.values()), labels=list(emotion_counts.keys()),
           colors=colors[:len(emotion_counts)], autopct='%1.1f%%',
           startangle=140, textprops={'fontsize': 11})
    ax.set_title('Emotion Distribution', fontsize=14, fontweight='bold')
    plt.tight_layout(); return fig


# ─── Tab 1: Single Text ───────────────────────────────────────
def analyze_single(text, language):
    if not text.strip():
        return "⚠️ Enter text.", "", "", "", "", None

    translated = text
    if language == "Auto Detect" or language != "English":
        try: translated = GoogleTranslator(source='auto', target='en').translate(text)
        except: pass

    blob = TextBlob(translated)
    pol, sub = blob.sentiment.polarity, blob.sentiment.subjectivity
    emotion, desc, traits = detect_emotion(pol, sub, translated)

    # Deep Learning result
    dl_result = ""
    if DL_AVAILABLE:
        try:
            res = dl_sentiment(translated[:512])[0]
            dl_result = f"\n🧠 Deep Learning: {res['label']} (confidence: {res['score']:.2%})"
        except: pass

    suggestion  = get_suggestion(emotion)
    toxicity    = check_toxicity(translated)
    fake        = check_fake_news(translated)
    traits_str  = "\n".join(traits) if traits else "No special traits."
    pol_str     = f"{pol:.2f}  (-1.0 Negative ← 0 → +1.0 Positive)"
    sub_str     = f"{sub:.2f}  (0.0 Objective → 1.0 Subjective)"
    extra       = f"🤖 Suggestion: {suggestion}{dl_result}\n\n{toxicity}\n{fake}"

    history_store.append({
        "Text": text[:80] + "..." if len(text) > 80 else text,
        "Emotion": emotion, "Polarity": round(pol, 2), "Subjectivity": round(sub, 2)
    })

    return f"{emotion}\n{desc}", pol_str, sub_str, traits_str, extra, make_bar_chart(pol, sub)


# ─── Tab 2: Voice Analysis ───────────────────────────────────
def analyze_voice(audio):
    if audio is None:
        return "⚠️ Please record audio first.", "", "", "", None
    try:
        import speech_recognition as sr
        r = sr.Recognizer()
        with sr.AudioFile(audio) as source:
            audio_data = r.record(source)
        text = r.recognize_google(audio_data)
    except Exception as e:
        return f"❌ Could not process audio: {e}\n\nTip: Speak clearly and try again!", "", "", "", None

    blob = TextBlob(text)
    pol, sub = blob.sentiment.polarity, blob.sentiment.subjectivity
    emotion, desc, traits = detect_emotion(pol, sub, text)
    traits_str = "\n".join(traits) if traits else "No special traits."
    suggestion = get_suggestion(emotion)

    return (f"🎤 You said: {text}\n\n🎭 {emotion}\n{desc}",
            f"{pol:.2f}", f"{sub:.2f}", traits_str,
            make_bar_chart(pol, sub))


# ─── Tab 3: Compare Texts ─────────────────────────────────────
def compare_texts(text1, text2):
    out = []
    for t in [text1, text2]:
        if not t.strip():
            out.append(("⚠️ Empty","—","—","—")); continue
        blob = TextBlob(t)
        pol, sub = blob.sentiment.polarity, blob.sentiment.subjectivity
        emo, desc, traits = detect_emotion(pol, sub, t)
        out.append((f"{emo}\n{desc}", f"{pol:.2f}", f"{sub:.2f}", "\n".join(traits) or "None"))

    pol1 = TextBlob(text1).sentiment.polarity if text1.strip() else 0
    pol2 = TextBlob(text2).sentiment.polarity if text2.strip() else 0
    fig, ax = plt.subplots(figsize=(8, 4))
    bars = ax.bar(['Text 1','Text 2'], [pol1, pol2],
                  color=['#4CAF50' if p >= 0 else '#f44336' for p in [pol1, pol2]])
    ax.axhline(0, color='black', linewidth=0.8, linestyle='--')
    ax.set_title('Polarity Comparison', fontsize=14, fontweight='bold')
    ax.set_ylabel('Polarity Score')
    for i, v in enumerate([pol1, pol2]):
        ax.text(i, v + 0.02, f'{v:.2f}', ha='center', fontweight='bold')
    plt.tight_layout()

    return (*out[0], *out[1], fig)


# ─── Tab 4: PDF Analysis ─────────────────────────────────────
def analyze_pdf(file):
    if file is None: return "⚠️ Upload a PDF.", "", None
    try:
        reader = PyPDF2.PdfReader(file.name)
        text = "".join(p.extract_text() or "" for p in reader.pages)
        if not text.strip(): return "❌ No text found in PDF.", "", None
    except Exception as e:
        return f"❌ Error: {e}", "", None

    blob = TextBlob(text[:3000])
    pol, sub = blob.sentiment.polarity, blob.sentiment.subjectivity
    emotion, desc, traits = detect_emotion(pol, sub, text)
    traits_str = "\n".join(traits) if traits else "None"
    summary = (f"🎭 {emotion}\n📝 {desc}\n\n"
               f"📊 Polarity: {pol:.2f}\n🧠 Subjectivity: {sub:.2f}\n\n"
               f"🔍 Traits:\n{traits_str}\n\n"
               f"🤖 {get_suggestion(emotion)}\n\n{check_toxicity(text)}")
    return summary, text[:600] + "...", make_bar_chart(pol, sub)


# ─── Tab 5: Bulk CSV ─────────────────────────────────────────
def analyze_csv(file, language):
    if file is None: return None, None, None, None, "⚠️ Upload a CSV."
    try: df = pd.read_csv(file.name)
    except Exception as e: return None, None, None, None, f"❌ {e}"

    text_col = next((c for c in df.columns
                     if any(k in c.lower() for k in ['review','text','comment','feedback'])),
                    df.columns[0])
    results, emo_counts, polarities, all_text = [], {}, [], ""

    for _, row in df.iterrows():
        text = str(row[text_col])
        translated = text
        if language not in ("English","Auto Detect"):
            try: translated = GoogleTranslator(source='auto', target='en').translate(text)
            except: pass
        blob = TextBlob(translated)
        pol, sub = blob.sentiment.polarity, blob.sentiment.subjectivity
        emo, desc, traits = detect_emotion(pol, sub, translated)
        emo_counts[emo] = emo_counts.get(emo, 0) + 1
        polarities.append(pol); all_text += " " + translated
        results.append({"Text": text, "Emotion": emo,
                        "Polarity": round(pol,2), "Subjectivity": round(sub,2),
                        "Traits": ", ".join(traits) or "None"})

    results_df = pd.DataFrame(results)
    with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp:
        excel_path = tmp.name
    results_df.to_excel(excel_path, index=False)

    # Bar chart
    fig1, ax1 = plt.subplots(figsize=(10, 5))
    colors = ['#4CAF50','#8BC34A','#CDDC39','#FF9800','#FF5722','#f44336','#9C27B0','#2196F3']
    bars = ax1.bar(list(emo_counts.keys()), list(emo_counts.values()), color=colors[:len(emo_counts)])
    ax1.set_title('Emotion Distribution', fontsize=14, fontweight='bold')
    plt.xticks(rotation=30, ha='right')
    for bar, cnt in zip(bars, emo_counts.values()):
        ax1.text(bar.get_x()+bar.get_width()/2, bar.get_height()+0.1,
                 str(cnt), ha='center', fontweight='bold')
    plt.tight_layout()

    # Pie chart
    fig2 = make_pie_chart(emo_counts)

    # Trend line
    fig3, ax3 = plt.subplots(figsize=(10, 4))
    ax3.plot(range(1, len(polarities)+1), polarities, marker='o', color='#2196F3', linewidth=2)
    ax3.axhline(0, color='red', linestyle='--')
    ax3.fill_between(range(1, len(polarities)+1), polarities, 0,
                     where=[p >= 0 for p in polarities], alpha=0.2, color='green', label='Positive')
    ax3.fill_between(range(1, len(polarities)+1), polarities, 0,
                     where=[p < 0 for p in polarities], alpha=0.2, color='red', label='Negative')
    ax3.set_title('Sentiment Trend', fontsize=14, fontweight='bold')
    ax3.legend(); plt.tight_layout()

    avg = sum(polarities)/len(polarities)
    summary = (f"✅ {len(results)} reviews analyzed!\n\n📊 Breakdown:\n" +
               "\n".join(f"  {e}: {c}" for e,c in sorted(emo_counts.items(), key=lambda x:-x[1])) +
               f"\n\n📈 Avg Polarity: {avg:.2f}" +
               f"\n🏆 Overall: {'Positive 😊' if avg>0.1 else 'Negative 😞' if avg<-0.1 else 'Neutral 😐'}")

    return fig1, fig2, fig3, excel_path, summary


# ─── Tab 6: AI Chatbot ───────────────────────────────────────
# FIX: Use dict format {"role": ..., "content": ...} instead of tuples
def chatbot_response(user_msg, history):
    if not user_msg.strip():
        return history, ""

    blob = TextBlob(user_msg)
    pol, sub = blob.sentiment.polarity, blob.sentiment.subjectivity
    emotion, desc, traits = detect_emotion(pol, sub, user_msg)
    suggestion = get_suggestion(emotion)
    toxicity   = check_toxicity(user_msg)

    response = (f"I analyzed your message! Here's what I found:\n\n"
                f"🎭 Emotion: {emotion}\n"
                f"📝 {desc}\n"
                f"📊 Polarity: {pol:.2f}\n"
                f"🧠 Subjectivity: {sub:.2f}\n\n"
                f"🤖 My advice: {suggestion}\n"
                f"{toxicity}\n\n"
                f"Feel free to share another message and I'll analyze it! 😊")

    # ✅ FIXED: Append dicts with 'role' and 'content' keys
    history.append({"role": "user", "content": user_msg})
    history.append({"role": "assistant", "content": response})
    return history, ""


# ─── Tab 7: Dashboard ────────────────────────────────────────
def show_dashboard():
    if not history_store:
        return "📭 No analysis yet! Go analyze some text first.", None
    df = pd.DataFrame(history_store)
    most_common = df['Emotion'].value_counts().idxmax()
    avg_pol = df['Polarity'].mean()
    fig = make_pie_chart(df['Emotion'].value_counts().to_dict())
    summary = (f"📊 DASHBOARD ANALYTICS\n{'='*35}\n"
               f"📝 Total Analyzed   : {len(df)}\n"
               f"📈 Avg Polarity     : {avg_pol:.2f}\n"
               f"🏆 Top Emotion      : {most_common}\n"
               f"😊 Positive         : {len(df[df['Polarity']>0.1])}\n"
               f"😞 Negative         : {len(df[df['Polarity']<-0.1])}\n"
               f"😐 Neutral          : {len(df[(df['Polarity']>=-0.1)&(df['Polarity']<=0.1)])}\n\n"
               f"📋 RECENT HISTORY:\n{'='*35}\n")
    for _, row in df.tail(10).iterrows():
        summary += f"• {row['Text'][:50]}\n  → {row['Emotion']} | {row['Polarity']}\n\n"
    return summary, fig


# ─── Tab 8: PDF Report ───────────────────────────────────────
def generate_pdf_report(text, language):
    if not text.strip(): return None
    translated = text
    if language not in ("English","Auto Detect"):
        try: translated = GoogleTranslator(source='auto', target='en').translate(text)
        except: pass
    blob = TextBlob(translated)
    pol, sub = blob.sentiment.polarity, blob.sentiment.subjectivity
    emotion, desc, traits = detect_emotion(pol, sub, translated)

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial","B",16)
    pdf.cell(0,10,"AI Sentiment Analysis Report",ln=True,align="C")
    pdf.set_font("Arial","",12); pdf.ln(5)
    pdf.cell(0,8,f"Emotion   : {emotion.encode('latin-1','replace').decode('latin-1')}",ln=True)
    pdf.cell(0,8,f"Description: {desc}",ln=True)
    pdf.cell(0,8,f"Polarity  : {pol:.2f}",ln=True)
    pdf.cell(0,8,f"Subjectivity: {sub:.2f}",ln=True)
    pdf.ln(3); pdf.set_font("Arial","B",12)
    pdf.cell(0,8,"Traits:",ln=True); pdf.set_font("Arial","",11)
    for t in traits:
        pdf.cell(0,7,f"  - {t.encode('latin-1','replace').decode('latin-1')}",ln=True)
    pdf.ln(3); pdf.set_font("Arial","B",12)
    pdf.cell(0,8,"AI Suggestion:",ln=True); pdf.set_font("Arial","",11)
    pdf.multi_cell(0,7,get_suggestion(emotion))
    pdf.ln(3); pdf.set_font("Arial","B",12)
    pdf.cell(0,8,"Safety Check:",ln=True); pdf.set_font("Arial","",11)
    pdf.multi_cell(0,7,check_toxicity(translated).encode('latin-1','replace').decode('latin-1'))

    # ✅ FIXED: Save to a proper temp file and return path
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf', dir=tempfile.gettempdir()) as tmp:
        pdf_path = tmp.name
    pdf.output(pdf_path)
    return pdf_path


# ─── Build UI ─────────────────────────────────────────────────
css = """
body { font-family: 'Segoe UI', sans-serif; }
.gradio-container { max-width: 1100px !important; margin: auto; }
.gr-button-primary { background: linear-gradient(135deg,#667eea,#764ba2) !important; }
footer { display: none !important; }
@media (max-width: 600px) {
    .gradio-container { padding: 8px !important; }
    .gr-box { padding: 8px !important; }
}
"""

with gr.Blocks(theme=gr.themes.Soft(), css=css, title="🧠 AI Sentiment Pro Max") as app:

    gr.Markdown("""
    # 🧠 AI Emotion & Sentiment Analysis — Pro Max
    **12 Features** | Voice • Text • PDF • CSV • Chatbot • Deep Learning • Dashboard • Reports • Toxicity • Fake News • Emoji • Mobile Friendly
    """)

    with gr.Tabs():

        # ── Tab 1: Single Text ────────────────────────────────
        with gr.Tab("📝 Text Analysis"):
            with gr.Row():
                with gr.Column(scale=1):
                    t_text = gr.Textbox(lines=6, placeholder="Type or paste any text...", label="Enter Text")
                    t_lang = gr.Dropdown(choices=language_choices, value="Auto Detect", label="🌍 Language")
                    t_btn  = gr.Button("🔍 Analyze", variant="primary")
                with gr.Column(scale=1):
                    t_emo   = gr.Textbox(label="🎭 Emotion")
                    t_pol   = gr.Textbox(label="📊 Polarity")
                    t_sub   = gr.Textbox(label="🧠 Subjectivity")
                    t_trait = gr.Textbox(label="🔍 Traits", lines=3)
                    t_extra = gr.Textbox(label="🤖 AI Insights", lines=4)
            t_chart = gr.Plot(label="📈 Chart")
            t_btn.click(analyze_single, [t_text, t_lang],
                        [t_emo, t_pol, t_sub, t_trait, t_extra, t_chart])
            gr.Examples([
                ["I absolutely LOVE this! Amazing!! 😍🔥", "Auto Detect"],
                ["यह बहुत बुरा अनुभव था। 😢", "Auto Detect"],
                ["BREAKING: You won't BELIEVE this secret! Share before deleted!", "Auto Detect"],
                ["I am so scared and nervous 😰", "Auto Detect"],
            ], inputs=[t_text, t_lang])

        # ── Tab 2: Voice Analysis ─────────────────────────────
        with gr.Tab("🎤 Voice Analysis"):
            gr.Markdown("### 🎤 Record your voice and analyze its sentiment!")
            gr.Markdown("> 💡 Click the microphone button, speak clearly, then click **Analyze Voice**")
            v_audio = gr.Audio(sources=["microphone"], type="filepath", label="🎙️ Record Audio")
            v_btn   = gr.Button("🔍 Analyze Voice", variant="primary")
            v_result = gr.Textbox(label="🎭 Voice Analysis Result", lines=6)
            with gr.Row():
                v_pol   = gr.Textbox(label="📊 Polarity")
                v_sub   = gr.Textbox(label="🧠 Subjectivity")
            v_trait = gr.Textbox(label="🔍 Traits", lines=3)
            v_chart = gr.Plot(label="📈 Chart")
            v_btn.click(analyze_voice, [v_audio], [v_result, v_pol, v_sub, v_trait, v_chart])

        # ── Tab 3: Compare ────────────────────────────────────
        with gr.Tab("🔁 Compare Texts"):
            gr.Markdown("### Compare 2 texts side by side!")
            with gr.Row():
                c_t1 = gr.Textbox(lines=5, label="📄 Text 1")
                c_t2 = gr.Textbox(lines=5, label="📄 Text 2")
            c_btn = gr.Button("🔍 Compare", variant="primary")
            with gr.Row():
                with gr.Column():
                    gr.Markdown("### Text 1")
                    c1_emo   = gr.Textbox(label="🎭 Emotion")
                    c1_pol   = gr.Textbox(label="📊 Polarity")
                    c1_sub   = gr.Textbox(label="🧠 Subjectivity")
                    c1_trait = gr.Textbox(label="🔍 Traits", lines=3)
                with gr.Column():
                    gr.Markdown("### Text 2")
                    c2_emo   = gr.Textbox(label="🎭 Emotion")
                    c2_pol   = gr.Textbox(label="📊 Polarity")
                    c2_sub   = gr.Textbox(label="🧠 Subjectivity")
                    c2_trait = gr.Textbox(label="🔍 Traits", lines=3)
            c_chart = gr.Plot(label="📊 Comparison Chart")
            c_btn.click(compare_texts, [c_t1, c_t2],
                        [c1_emo, c1_pol, c1_sub, c1_trait,
                         c2_emo, c2_pol, c2_sub, c2_trait, c_chart])

        # ── Tab 4: PDF Analysis ───────────────────────────────
        with gr.Tab("📄 PDF Analysis"):
            gr.Markdown("### Upload any PDF and analyze its sentiment!")
            p_file  = gr.File(label="📂 Upload PDF", file_types=[".pdf"])
            p_btn   = gr.Button("🔍 Analyze PDF", variant="primary")
            p_sum   = gr.Textbox(label="📋 Analysis", lines=12)
            p_prev  = gr.Textbox(label="📄 Text Preview", lines=4)
            p_chart = gr.Plot(label="📊 Chart")
            p_btn.click(analyze_pdf, [p_file], [p_sum, p_prev, p_chart])

        # ── Tab 5: CSV ────────────────────────────────────────
        with gr.Tab("📁 Bulk CSV"):
            gr.Markdown("### Upload CSV with column: `review`, `text`, `comment`, or `feedback`")
            with gr.Row():
                with gr.Column():
                    csv_f    = gr.File(label="📂 Upload CSV", file_types=[".csv"])
                    csv_lang = gr.Dropdown(choices=language_choices, value="Auto Detect", label="🌍 Language")
                    csv_btn  = gr.Button("🔍 Analyze", variant="primary")
                with gr.Column():
                    csv_sum  = gr.Textbox(label="📋 Summary", lines=12)
                    csv_dl   = gr.File(label="📥 Download Excel")
            with gr.Row():
                csv_c1 = gr.Plot(label="📊 Bar Chart")
                csv_c2 = gr.Plot(label="🥧 Pie Chart")
            csv_c3 = gr.Plot(label="📈 Trend Line")
            csv_btn.click(analyze_csv, [csv_f, csv_lang],
                          [csv_c1, csv_c2, csv_c3, csv_dl, csv_sum])

        # ── Tab 6: AI Chatbot ─────────────────────────────────
        with gr.Tab("🤖 AI Chatbot"):
            gr.Markdown("### Chat with AI! It will analyze the sentiment of everything you say!")
            # ✅ FIXED: type="messages" for Gradio 4.x compatibility
            chatbot = gr.Chatbot(label="💬 Sentiment Chatbot", height=400, type="messages")
            with gr.Row():
                chat_input = gr.Textbox(placeholder="Type your message...", label="Your Message", scale=4)
                chat_btn   = gr.Button("Send 💬", variant="primary", scale=1)
            chat_clear = gr.Button("🗑️ Clear Chat")
            chat_btn.click(chatbot_response, [chat_input, chatbot], [chatbot, chat_input])
            chat_input.submit(chatbot_response, [chat_input, chatbot], [chatbot, chat_input])
            # ✅ FIXED: Clear returns empty list (works with dict format too)
            chat_clear.click(lambda: ([], ""), None, [chatbot, chat_input])

        # ── Tab 7: Dashboard ──────────────────────────────────
        with gr.Tab("📊 Dashboard"):
            gr.Markdown("### Your session analytics & history!")
            dash_btn = gr.Button("🔄 Refresh Dashboard", variant="primary")
            dash_sum = gr.Textbox(label="📋 Analytics", lines=20)
            dash_pie = gr.Plot(label="🥧 Emotion Pie Chart")
            dash_btn.click(show_dashboard, [], [dash_sum, dash_pie])

        # ── Tab 8: PDF Report ─────────────────────────────────
        with gr.Tab("📥 PDF Report"):
            gr.Markdown("### Generate a professional PDF report of your analysis!")
            r_text = gr.Textbox(lines=6, placeholder="Enter text to analyze...", label="Enter Text")
            r_lang = gr.Dropdown(choices=language_choices, value="Auto Detect", label="🌍 Language")
            r_btn  = gr.Button("📥 Generate PDF Report", variant="primary")
            # ✅ FIXED: type="filepath" so Gradio correctly serves the generated file
            r_file = gr.File(label="📄 Download Report", type="filepath")
            r_btn.click(generate_pdf_report, [r_text, r_lang], [r_file])

if __name__ == "__main__":
    app.launch()
=======
# ============================================================
# 🧠 AI Sentiment & Emotion Analysis — ULTIMATE PRO MAX v4
# FIXED FOR GRADIO 6.x:
#   - theme/css moved to app.launch()
#   - gr.Chatbot: removed unsupported type="messages"
#   - chatbot history uses tuples (user_msg, response)
#   - chat_clear returns ([], "")
#   - gr.File upload uses .name correctly
# ============================================================

from textblob import TextBlob
import gradio as gr
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from deep_translator import GoogleTranslator
from wordcloud import WordCloud
import tempfile, requests, os, emoji
from bs4 import BeautifulSoup
from fpdf import FPDF
import PyPDF2
from transformers import pipeline

# ─── Load Deep Learning Model ────────────────────────────────
print("⏳ Loading Deep Learning model...")
try:
    dl_sentiment = pipeline(
        "sentiment-analysis",
        model="distilbert-base-uncased-finetuned-sst-2-english",
        truncation=True, max_length=512
    )
    DL_AVAILABLE = True
    print("✅ Deep Learning model loaded!")
except Exception as e:
    DL_AVAILABLE = False
    print(f"⚠️ DL model unavailable: {e}")

# ─── History & Chat Store ────────────────────────────────────
history_store = []

language_choices = [
    "Auto Detect","English","Hindi","Spanish","French",
    "German","Arabic","Portuguese","Japanese","Chinese"
]

# ─── Core Functions ──────────────────────────────────────────
def detect_emotion(polarity, subjectivity, text):
    traits = []
    if polarity >= 0.6:     emotion, desc = "🤩 ECSTATIC",    "Extremely happy and excited!"
    elif polarity >= 0.3:   emotion, desc = "😊 HAPPY",        "Positive and cheerful tone."
    elif polarity >= 0.1:   emotion, desc = "🙂 CONTENT",      "Mildly positive and satisfied."
    elif polarity > -0.1:
        if subjectivity < 0.3: emotion, desc = "😐 NEUTRAL",   "Objective and factual tone."
        else:                   emotion, desc = "😶 INDIFFERENT","No strong feeling detected."
    elif polarity >= -0.3:  emotion, desc = "😟 UNHAPPY",      "Mildly negative tone."
    elif polarity >= -0.6:  emotion, desc = "😠 ANGRY",        "Strong negative and frustrated."
    else:                   emotion, desc = "😡 FURIOUS",       "Extremely negative and intense!"

    if subjectivity > 0.7:  traits.append("💭 Highly Opinionated")
    elif subjectivity < 0.3: traits.append("📰 Very Objective")
    if text.isupper():       traits.append("🔊 ALL CAPS — Strong Emphasis")
    if "!" in text:          traits.append("❗ High Intensity")
    if "?" in text:          traits.append("❓ Uncertainty Detected")
    for w in ["love","amazing","fantastic","excellent","great"]:
        if w in text.lower(): traits.append("💖 Strong Positive Words"); break
    for w in ["hate","terrible","awful","horrible","worst"]:
        if w in text.lower(): traits.append("💢 Strong Negative Words"); break
    for w in ["sad","cry","depressed","lonely","miss"]:
        if w in text.lower(): traits.append("😢 Sadness Detected"); break
    for w in ["scared","afraid","fear","nervous","anxious"]:
        if w in text.lower(): traits.append("😨 Fear/Anxiety Detected"); break
    for w in ["surprise","wow","omg","unbelievable","shocked"]:
        if w in text.lower(): traits.append("😲 Surprise Detected"); break

    emojis_found = [c for c in text if c in emoji.EMOJI_DATA]
    if emojis_found:
        traits.append(f"🎭 Emojis: {' '.join(emojis_found[:5])}")

    return emotion, desc, traits


def get_suggestion(emotion):
    s = {
        "🤩 ECSTATIC":    "🌟 You're on fire! Great time to tackle big challenges!",
        "😊 HAPPY":       "✅ Great mindset! Perfect time to be productive.",
        "🙂 CONTENT":     "👍 You're in a good place. Keep it up!",
        "😐 NEUTRAL":     "📌 Try adding more detail to be more impactful.",
        "😶 INDIFFERENT": "💡 Consider being more specific about your feelings.",
        "😟 UNHAPPY":     "🤝 Talk to someone you trust or take a short break.",
        "😠 ANGRY":       "🧘 Take a deep breath before responding.",
        "😡 FURIOUS":     "⚠️ Step away and calm down before taking action.",
    }
    return s.get(emotion, "💬 Keep expressing yourself clearly!")


def check_toxicity(text):
    toxic = ["kill","hate","stupid","idiot","dumb","loser","trash","worthless","shut up","die"]
    found = [w for w in toxic if w in text.lower()]
    return f"⚠️ Toxic language: {', '.join(found)}" if found else "✅ No toxic language detected."


def check_fake_news(text):
    signals = ["breaking","exclusive","shocking","you won't believe","share before deleted",
               "mainstream media won't tell","secret","hidden truth","guaranteed","100%"]
    found = [s for s in signals if s in text.lower()]
    if len(found) >= 2:   return f"🚨 Fake news signals: {', '.join(found)}"
    elif len(found) == 1: return f"⚠️ Mild clickbait: '{found[0]}'"
    return "✅ No fake news signals."


def make_bar_chart(polarity, subjectivity):
    bg = "#e8f5e9" if polarity >= 0.3 else "#fff9c4" if polarity > -0.1 else "#ffebee"
    fig, axes = plt.subplots(1, 2, figsize=(10, 4))
    fig.patch.set_facecolor(bg)
    pol_color = '#4CAF50' if polarity >= 0.1 else ('#f44336' if polarity <= -0.1 else '#FF9800')
    axes[0].barh(['Polarity'], [polarity], color=pol_color, height=0.4)
    axes[0].set_xlim(-1, 1)
    axes[0].axvline(0, color='black', linewidth=0.8, linestyle='--')
    axes[0].set_title('Polarity Score', fontweight='bold')
    axes[0].set_xlabel('Negative ← 0 → Positive')
    axes[0].text(polarity, 0, f'  {polarity:.2f}', va='center', fontweight='bold')
    sub_color = '#2196F3' if subjectivity < 0.5 else '#9C27B0'
    axes[1].barh(['Subjectivity'], [subjectivity], color=sub_color, height=0.4)
    axes[1].set_xlim(0, 1)
    axes[1].set_title('Subjectivity Score', fontweight='bold')
    axes[1].set_xlabel('Objective ← 0.5 → Subjective')
    axes[1].text(subjectivity, 0, f'  {subjectivity:.2f}', va='center', fontweight='bold')
    plt.tight_layout()
    return fig


def make_pie_chart(emotion_counts):
    fig, ax = plt.subplots(figsize=(7, 7))
    colors = ['#4CAF50','#8BC34A','#CDDC39','#FF9800','#FF5722','#f44336','#9C27B0','#2196F3','#00BCD4']
    ax.pie(list(emotion_counts.values()), labels=list(emotion_counts.keys()),
           colors=colors[:len(emotion_counts)], autopct='%1.1f%%',
           startangle=140, textprops={'fontsize': 11})
    ax.set_title('Emotion Distribution', fontsize=14, fontweight='bold')
    plt.tight_layout()
    return fig


# ─── Tab 1: Single Text ───────────────────────────────────────
def analyze_single(text, language):
    if not text.strip():
        return "⚠️ Enter text.", "", "", "", "", None

    translated = text
    if language == "Auto Detect" or language != "English":
        try:
            translated = GoogleTranslator(source='auto', target='en').translate(text)
        except:
            pass

    blob = TextBlob(translated)
    pol, sub = blob.sentiment.polarity, blob.sentiment.subjectivity
    emotion, desc, traits = detect_emotion(pol, sub, translated)

    dl_result = ""
    if DL_AVAILABLE:
        try:
            res = dl_sentiment(translated[:512])[0]
            dl_result = f"\n🧠 Deep Learning: {res['label']} (confidence: {res['score']:.2%})"
        except:
            pass

    suggestion  = get_suggestion(emotion)
    toxicity    = check_toxicity(translated)
    fake        = check_fake_news(translated)
    traits_str  = "\n".join(traits) if traits else "No special traits."
    pol_str     = f"{pol:.2f}  (-1.0 Negative ← 0 → +1.0 Positive)"
    sub_str     = f"{sub:.2f}  (0.0 Objective → 1.0 Subjective)"
    extra       = f"🤖 Suggestion: {suggestion}{dl_result}\n\n{toxicity}\n{fake}"

    history_store.append({
        "Text": text[:80] + "..." if len(text) > 80 else text,
        "Emotion": emotion,
        "Polarity": round(pol, 2),
        "Subjectivity": round(sub, 2)
    })

    return f"{emotion}\n{desc}", pol_str, sub_str, traits_str, extra, make_bar_chart(pol, sub)


# ─── Tab 2: Voice Analysis ───────────────────────────────────
def analyze_voice(audio):
    if audio is None:
        return "⚠️ Please record audio first.", "", "", "", None
    try:
        import speech_recognition as sr
        r = sr.Recognizer()
        with sr.AudioFile(audio) as source:
            audio_data = r.record(source)
        text = r.recognize_google(audio_data)
    except Exception as e:
        return f"❌ Could not process audio: {e}\n\nTip: Speak clearly and try again!", "", "", "", None

    blob = TextBlob(text)
    pol, sub = blob.sentiment.polarity, blob.sentiment.subjectivity
    emotion, desc, traits = detect_emotion(pol, sub, text)
    traits_str = "\n".join(traits) if traits else "No special traits."
    suggestion = get_suggestion(emotion)

    return (f"🎤 You said: {text}\n\n🎭 {emotion}\n{desc}",
            f"{pol:.2f}", f"{sub:.2f}", traits_str,
            make_bar_chart(pol, sub))


# ─── Tab 3: Compare Texts ─────────────────────────────────────
def compare_texts(text1, text2):
    out = []
    for t in [text1, text2]:
        if not t.strip():
            out.append(("⚠️ Empty", "—", "—", "—"))
            continue
        blob = TextBlob(t)
        pol, sub = blob.sentiment.polarity, blob.sentiment.subjectivity
        emo, desc, traits = detect_emotion(pol, sub, t)
        out.append((f"{emo}\n{desc}", f"{pol:.2f}", f"{sub:.2f}", "\n".join(traits) or "None"))

    pol1 = TextBlob(text1).sentiment.polarity if text1.strip() else 0
    pol2 = TextBlob(text2).sentiment.polarity if text2.strip() else 0
    fig, ax = plt.subplots(figsize=(8, 4))
    bars = ax.bar(['Text 1', 'Text 2'], [pol1, pol2],
                  color=['#4CAF50' if p >= 0 else '#f44336' for p in [pol1, pol2]])
    ax.axhline(0, color='black', linewidth=0.8, linestyle='--')
    ax.set_title('Polarity Comparison', fontsize=14, fontweight='bold')
    ax.set_ylabel('Polarity Score')
    for i, v in enumerate([pol1, pol2]):
        ax.text(i, v + 0.02, f'{v:.2f}', ha='center', fontweight='bold')
    plt.tight_layout()

    return (*out[0], *out[1], fig)


# ─── Tab 4: PDF Analysis ─────────────────────────────────────
def analyze_pdf(file):
    if file is None:
        return "⚠️ Upload a PDF.", "", None
    try:
        # Gradio 6.x passes file path as string directly
        file_path = file if isinstance(file, str) else file.name
        reader = PyPDF2.PdfReader(file_path)
        text = "".join(p.extract_text() or "" for p in reader.pages)
        if not text.strip():
            return "❌ No text found in PDF.", "", None
    except Exception as e:
        return f"❌ Error: {e}", "", None

    blob = TextBlob(text[:3000])
    pol, sub = blob.sentiment.polarity, blob.sentiment.subjectivity
    emotion, desc, traits = detect_emotion(pol, sub, text)
    traits_str = "\n".join(traits) if traits else "None"
    summary = (f"🎭 {emotion}\n📝 {desc}\n\n"
               f"📊 Polarity: {pol:.2f}\n🧠 Subjectivity: {sub:.2f}\n\n"
               f"🔍 Traits:\n{traits_str}\n\n"
               f"🤖 {get_suggestion(emotion)}\n\n{check_toxicity(text)}")
    return summary, text[:600] + "...", make_bar_chart(pol, sub)


# ─── Tab 5: Bulk CSV ─────────────────────────────────────────
def analyze_csv(file, language):
    if file is None:
        return None, None, None, None, "⚠️ Upload a CSV."
    try:
        # Gradio 6.x passes file path as string directly
        file_path = file if isinstance(file, str) else file.name
        df = pd.read_csv(file_path)
    except Exception as e:
        return None, None, None, None, f"❌ {e}"

    text_col = next((c for c in df.columns
                     if any(k in c.lower() for k in ['review', 'text', 'comment', 'feedback'])),
                    df.columns[0])
    results, emo_counts, polarities, all_text = [], {}, [], ""

    for _, row in df.iterrows():
        text = str(row[text_col])
        translated = text
        if language not in ("English", "Auto Detect"):
            try:
                translated = GoogleTranslator(source='auto', target='en').translate(text)
            except:
                pass
        blob = TextBlob(translated)
        pol, sub = blob.sentiment.polarity, blob.sentiment.subjectivity
        emo, desc, traits = detect_emotion(pol, sub, translated)
        emo_counts[emo] = emo_counts.get(emo, 0) + 1
        polarities.append(pol)
        all_text += " " + translated
        results.append({"Text": text, "Emotion": emo,
                        "Polarity": round(pol, 2), "Subjectivity": round(sub, 2),
                        "Traits": ", ".join(traits) or "None"})

    results_df = pd.DataFrame(results)
    with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp:
        excel_path = tmp.name
    results_df.to_excel(excel_path, index=False)

    # Bar chart
    fig1, ax1 = plt.subplots(figsize=(10, 5))
    colors = ['#4CAF50','#8BC34A','#CDDC39','#FF9800','#FF5722','#f44336','#9C27B0','#2196F3']
    bars = ax1.bar(list(emo_counts.keys()), list(emo_counts.values()), color=colors[:len(emo_counts)])
    ax1.set_title('Emotion Distribution', fontsize=14, fontweight='bold')
    plt.xticks(rotation=30, ha='right')
    for bar, cnt in zip(bars, emo_counts.values()):
        ax1.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.1,
                 str(cnt), ha='center', fontweight='bold')
    plt.tight_layout()

    # Pie chart
    fig2 = make_pie_chart(emo_counts)

    # Trend line
    fig3, ax3 = plt.subplots(figsize=(10, 4))
    ax3.plot(range(1, len(polarities) + 1), polarities, marker='o', color='#2196F3', linewidth=2)
    ax3.axhline(0, color='red', linestyle='--')
    ax3.fill_between(range(1, len(polarities) + 1), polarities, 0,
                     where=[p >= 0 for p in polarities], alpha=0.2, color='green', label='Positive')
    ax3.fill_between(range(1, len(polarities) + 1), polarities, 0,
                     where=[p < 0 for p in polarities], alpha=0.2, color='red', label='Negative')
    ax3.set_title('Sentiment Trend', fontsize=14, fontweight='bold')
    ax3.legend()
    plt.tight_layout()

    avg = sum(polarities) / len(polarities)
    summary = (f"✅ {len(results)} reviews analyzed!\n\n📊 Breakdown:\n" +
               "\n".join(f"  {e}: {c}" for e, c in sorted(emo_counts.items(), key=lambda x: -x[1])) +
               f"\n\n📈 Avg Polarity: {avg:.2f}" +
               f"\n🏆 Overall: {'Positive 😊' if avg > 0.1 else 'Negative 😞' if avg < -0.1 else 'Neutral 😐'}")

    return fig1, fig2, fig3, excel_path, summary


# ─── Tab 6: AI Chatbot ───────────────────────────────────────
# Uses TUPLE format (user_msg, response) — compatible with all Gradio versions
def chatbot_response(user_msg, history):
    if not user_msg.strip():
        return history, ""

    blob = TextBlob(user_msg)
    pol, sub = blob.sentiment.polarity, blob.sentiment.subjectivity
    emotion, desc, traits = detect_emotion(pol, sub, user_msg)
    suggestion = get_suggestion(emotion)
    toxicity   = check_toxicity(user_msg)

    response = (f"I analyzed your message! Here's what I found:\n\n"
                f"🎭 Emotion: {emotion}\n"
                f"📝 {desc}\n"
                f"📊 Polarity: {pol:.2f}\n"
                f"🧠 Subjectivity: {sub:.2f}\n\n"
                f"🤖 My advice: {suggestion}\n"
                f"{toxicity}\n\n"
                f"Feel free to share another message and I'll analyze it! 😊")

    # ✅ Tuple format — works with all Gradio versions
    history.append((user_msg, response))
    return history, ""


# ─── Tab 7: Dashboard ────────────────────────────────────────
def show_dashboard():
    if not history_store:
        return "📭 No analysis yet! Go analyze some text first.", None
    df = pd.DataFrame(history_store)
    most_common = df['Emotion'].value_counts().idxmax()
    avg_pol = df['Polarity'].mean()
    fig = make_pie_chart(df['Emotion'].value_counts().to_dict())
    summary = (f"📊 DASHBOARD ANALYTICS\n{'='*35}\n"
               f"📝 Total Analyzed   : {len(df)}\n"
               f"📈 Avg Polarity     : {avg_pol:.2f}\n"
               f"🏆 Top Emotion      : {most_common}\n"
               f"😊 Positive         : {len(df[df['Polarity'] > 0.1])}\n"
               f"😞 Negative         : {len(df[df['Polarity'] < -0.1])}\n"
               f"😐 Neutral          : {len(df[(df['Polarity'] >= -0.1) & (df['Polarity'] <= 0.1)])}\n\n"
               f"📋 RECENT HISTORY:\n{'='*35}\n")
    for _, row in df.tail(10).iterrows():
        summary += f"• {row['Text'][:50]}\n  → {row['Emotion']} | {row['Polarity']}\n\n"
    return summary, fig


# ─── Tab 8: PDF Report ───────────────────────────────────────
def generate_pdf_report(text, language):
    if not text.strip():
        return None
    translated = text
    if language not in ("English", "Auto Detect"):
        try:
            translated = GoogleTranslator(source='auto', target='en').translate(text)
        except:
            pass
    blob = TextBlob(translated)
    pol, sub = blob.sentiment.polarity, blob.sentiment.subjectivity
    emotion, desc, traits = detect_emotion(pol, sub, translated)

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "AI Sentiment Analysis Report", ln=True, align="C")
    pdf.set_font("Arial", "", 12)
    pdf.ln(5)
    pdf.cell(0, 8, f"Emotion   : {emotion.encode('latin-1','replace').decode('latin-1')}", ln=True)
    pdf.cell(0, 8, f"Description: {desc}", ln=True)
    pdf.cell(0, 8, f"Polarity  : {pol:.2f}", ln=True)
    pdf.cell(0, 8, f"Subjectivity: {sub:.2f}", ln=True)
    pdf.ln(3)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 8, "Traits:", ln=True)
    pdf.set_font("Arial", "", 11)
    for t in traits:
        pdf.cell(0, 7, f"  - {t.encode('latin-1','replace').decode('latin-1')}", ln=True)
    pdf.ln(3)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 8, "AI Suggestion:", ln=True)
    pdf.set_font("Arial", "", 11)
    pdf.multi_cell(0, 7, get_suggestion(emotion))
    pdf.ln(3)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 8, "Safety Check:", ln=True)
    pdf.set_font("Arial", "", 11)
    pdf.multi_cell(0, 7, check_toxicity(translated).encode('latin-1', 'replace').decode('latin-1'))

    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf', dir=tempfile.gettempdir()) as tmp:
        pdf_path = tmp.name
    pdf.output(pdf_path)
    return pdf_path


# ─── CSS ─────────────────────────────────────────────────────
css = """
body { font-family: 'Segoe UI', sans-serif; }
.gradio-container { max-width: 1100px !important; margin: auto; }
footer { display: none !important; }
@media (max-width: 600px) {
    .gradio-container { padding: 8px !important; }
    .gr-box { padding: 8px !important; }
}
"""

# ─── Build UI ─────────────────────────────────────────────────
# ✅ FIXED: theme and css removed from gr.Blocks() — passed to launch() instead
with gr.Blocks(title="🧠 AI Sentiment Pro Max") as app:

    gr.Markdown("""
    # 🧠 AI Emotion & Sentiment Analysis — Pro Max
    **12 Features** | Voice • Text • PDF • CSV • Chatbot • Deep Learning • Dashboard • Reports • Toxicity • Fake News • Emoji • Mobile Friendly
    """)

    with gr.Tabs():

        # ── Tab 1: Single Text ────────────────────────────────
        with gr.Tab("📝 Text Analysis"):
            with gr.Row():
                with gr.Column(scale=1):
                    t_text = gr.Textbox(lines=6, placeholder="Type or paste any text...", label="Enter Text")
                    t_lang = gr.Dropdown(choices=language_choices, value="Auto Detect", label="🌍 Language")
                    t_btn  = gr.Button("🔍 Analyze", variant="primary")
                with gr.Column(scale=1):
                    t_emo   = gr.Textbox(label="🎭 Emotion")
                    t_pol   = gr.Textbox(label="📊 Polarity")
                    t_sub   = gr.Textbox(label="🧠 Subjectivity")
                    t_trait = gr.Textbox(label="🔍 Traits", lines=3)
                    t_extra = gr.Textbox(label="🤖 AI Insights", lines=4)
            t_chart = gr.Plot(label="📈 Chart")
            t_btn.click(analyze_single, [t_text, t_lang],
                        [t_emo, t_pol, t_sub, t_trait, t_extra, t_chart])
            gr.Examples([
                ["I absolutely LOVE this! Amazing!! 😍🔥", "Auto Detect"],
                ["यह बहुत बुरा अनुभव था। 😢", "Auto Detect"],
                ["BREAKING: You won't BELIEVE this secret! Share before deleted!", "Auto Detect"],
                ["I am so scared and nervous 😰", "Auto Detect"],
            ], inputs=[t_text, t_lang])

        # ── Tab 2: Voice Analysis ─────────────────────────────
        with gr.Tab("🎤 Voice Analysis"):
            gr.Markdown("### 🎤 Record your voice and analyze its sentiment!")
            gr.Markdown("> 💡 Click the microphone button, speak clearly, then click **Analyze Voice**")
            v_audio  = gr.Audio(sources=["microphone"], type="filepath", label="🎙️ Record Audio")
            v_btn    = gr.Button("🔍 Analyze Voice", variant="primary")
            v_result = gr.Textbox(label="🎭 Voice Analysis Result", lines=6)
            with gr.Row():
                v_pol  = gr.Textbox(label="📊 Polarity")
                v_sub  = gr.Textbox(label="🧠 Subjectivity")
            v_trait = gr.Textbox(label="🔍 Traits", lines=3)
            v_chart = gr.Plot(label="📈 Chart")
            v_btn.click(analyze_voice, [v_audio], [v_result, v_pol, v_sub, v_trait, v_chart])

        # ── Tab 3: Compare ────────────────────────────────────
        with gr.Tab("🔁 Compare Texts"):
            gr.Markdown("### Compare 2 texts side by side!")
            with gr.Row():
                c_t1 = gr.Textbox(lines=5, label="📄 Text 1")
                c_t2 = gr.Textbox(lines=5, label="📄 Text 2")
            c_btn = gr.Button("🔍 Compare", variant="primary")
            with gr.Row():
                with gr.Column():
                    gr.Markdown("### Text 1")
                    c1_emo   = gr.Textbox(label="🎭 Emotion")
                    c1_pol   = gr.Textbox(label="📊 Polarity")
                    c1_sub   = gr.Textbox(label="🧠 Subjectivity")
                    c1_trait = gr.Textbox(label="🔍 Traits", lines=3)
                with gr.Column():
                    gr.Markdown("### Text 2")
                    c2_emo   = gr.Textbox(label="🎭 Emotion")
                    c2_pol   = gr.Textbox(label="📊 Polarity")
                    c2_sub   = gr.Textbox(label="🧠 Subjectivity")
                    c2_trait = gr.Textbox(label="🔍 Traits", lines=3)
            c_chart = gr.Plot(label="📊 Comparison Chart")
            c_btn.click(compare_texts, [c_t1, c_t2],
                        [c1_emo, c1_pol, c1_sub, c1_trait,
                         c2_emo, c2_pol, c2_sub, c2_trait, c_chart])

        # ── Tab 4: PDF Analysis ───────────────────────────────
        with gr.Tab("📄 PDF Analysis"):
            gr.Markdown("### Upload any PDF and analyze its sentiment!")
            p_file  = gr.File(label="📂 Upload PDF", file_types=[".pdf"])
            p_btn   = gr.Button("🔍 Analyze PDF", variant="primary")
            p_sum   = gr.Textbox(label="📋 Analysis", lines=12)
            p_prev  = gr.Textbox(label="📄 Text Preview", lines=4)
            p_chart = gr.Plot(label="📊 Chart")
            p_btn.click(analyze_pdf, [p_file], [p_sum, p_prev, p_chart])

        # ── Tab 5: CSV ────────────────────────────────────────
        with gr.Tab("📁 Bulk CSV"):
            gr.Markdown("### Upload CSV with column: `review`, `text`, `comment`, or `feedback`")
            with gr.Row():
                with gr.Column():
                    csv_f    = gr.File(label="📂 Upload CSV", file_types=[".csv"])
                    csv_lang = gr.Dropdown(choices=language_choices, value="Auto Detect", label="🌍 Language")
                    csv_btn  = gr.Button("🔍 Analyze", variant="primary")
                with gr.Column():
                    csv_sum  = gr.Textbox(label="📋 Summary", lines=12)
                    csv_dl   = gr.File(label="📥 Download Excel")
            with gr.Row():
                csv_c1 = gr.Plot(label="📊 Bar Chart")
                csv_c2 = gr.Plot(label="🥧 Pie Chart")
            csv_c3 = gr.Plot(label="📈 Trend Line")
            csv_btn.click(analyze_csv, [csv_f, csv_lang],
                          [csv_c1, csv_c2, csv_c3, csv_dl, csv_sum])

        # ── Tab 6: AI Chatbot ─────────────────────────────────
        with gr.Tab("🤖 AI Chatbot"):
            gr.Markdown("### Chat with AI! It will analyze the sentiment of everything you say!")
            # ✅ FIXED: Removed type="messages" — uses default tuple format
            chatbot = gr.Chatbot(label="💬 Sentiment Chatbot", height=400)
            with gr.Row():
                chat_input = gr.Textbox(placeholder="Type your message...", label="Your Message", scale=4)
                chat_btn   = gr.Button("Send 💬", variant="primary", scale=1)
            chat_clear = gr.Button("🗑️ Clear Chat")
            chat_btn.click(chatbot_response, [chat_input, chatbot], [chatbot, chat_input])
            chat_input.submit(chatbot_response, [chat_input, chatbot], [chatbot, chat_input])
            # ✅ FIXED: Returns ([], "") to clear both chatbot and input
            chat_clear.click(lambda: ([], ""), None, [chatbot, chat_input])

        # ── Tab 7: Dashboard ──────────────────────────────────
        with gr.Tab("📊 Dashboard"):
            gr.Markdown("### Your session analytics & history!")
            dash_btn = gr.Button("🔄 Refresh Dashboard", variant="primary")
            dash_sum = gr.Textbox(label="📋 Analytics", lines=20)
            dash_pie = gr.Plot(label="🥧 Emotion Pie Chart")
            dash_btn.click(show_dashboard, [], [dash_sum, dash_pie])

        # ── Tab 8: PDF Report ─────────────────────────────────
        with gr.Tab("📥 PDF Report"):
            gr.Markdown("### Generate a professional PDF report of your analysis!")
            r_text = gr.Textbox(lines=6, placeholder="Enter text to analyze...", label="Enter Text")
            r_lang = gr.Dropdown(choices=language_choices, value="Auto Detect", label="🌍 Language")
            r_btn  = gr.Button("📥 Generate PDF Report", variant="primary")
            # ✅ FIXED: type="filepath" so Gradio correctly serves the generated file
            r_file = gr.File(label="📄 Download Report", type="filepath")
            r_btn.click(generate_pdf_report, [r_text, r_lang], [r_file])

if __name__ == "__main__":
    # ✅ FIXED: theme and css passed here (Gradio 6.x requirement)
    app.launch(
        theme=gr.themes.Soft(),
        css=css
    )
>>>>>>> a2619b96a9e7068603542fb3b94fcf330280ab82

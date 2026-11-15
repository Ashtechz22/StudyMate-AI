import os
from io import BytesIO

import streamlit as st
from dotenv import load_dotenv
from pypdf import PdfReader
from google import genai

load_dotenv()

# -------------------- PAGE SETTINGS --------------------
st.set_page_config(
    page_title="StudyMate AI",
    page_icon="📘",
    layout="wide",
)

# -------------------- SIMPLE DESIGN --------------------
st.markdown("""
<style>
    .main {background-color: #f7f9fc;}
    .block-container {padding-top: 2rem; max-width: 1100px;}
    .hero {
        padding: 24px;
        border-radius: 18px;
        background: linear-gradient(110deg, #173b70, #3677c8);
        color: white;
        margin-bottom: 20px;
    }
    .hero h1 {color: white; margin-bottom: 5px;}
    .hero p {color: #e8f1ff; margin-bottom: 0;}
    div[data-testid="stMetric"] {
        background: white;
        border: 1px solid #e7edf5;
        padding: 12px;
        border-radius: 12px;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero">
    <h1>📘 StudyMate AI</h1>
    <p>Your simple AI study partner — summarize notes, ask questions, and practise for exams.</p>
</div>
""", unsafe_allow_html=True)

# -------------------- API CONFIGURATION --------------------
api_key = os.getenv("GEMINI_API_KEY", "").strip()
model_name = os.getenv("GEMINI_MODEL", "gemini-2.5-flash").strip()

if not api_key:
    st.error("Gemini API key is missing.")
    st.info("Open the .env file, add your key, and restart the application.")
    st.code("GEMINI_API_KEY=your_api_key_here\nGEMINI_MODEL=gemini-2.5-flash")
    st.markdown("Get an API key from [Google AI Studio](https://aistudio.google.com/apikey).")
    st.stop()

client = genai.Client(api_key=api_key)


# -------------------- HELPER FUNCTIONS --------------------
def read_pdf(uploaded_file):
    """Return a list containing the extracted text of each PDF page."""
    reader = PdfReader(BytesIO(uploaded_file.getvalue()))
    page_texts = []

    for page_number, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""
        if text.strip():
            page_texts.append({
                "page": page_number,
                "text": text.strip()
            })

    return page_texts


def call_ai(prompt):
    """Send a prompt to Gemini and return its text response."""
    response = client.models.generate_content(
        model=model_name,
        contents=prompt
    )
    return response.text or "Sorry, no response was generated."


def make_document_context(page_texts, max_chars=45000):
    """Build a page-labelled context while keeping the request manageable."""
    sections = []
    used = 0

    for item in page_texts:
        section = f"[Page {item['page']}]\n{item['text']}"
        remaining = max_chars - used
        if remaining <= 0:
            break
        sections.append(section[:remaining])
        used += len(section)

    return "\n\n".join(sections)


# -------------------- SIDEBAR --------------------
with st.sidebar:
    st.header("📚 StudyMate AI")
    st.write("**How to use:**")
    st.write("1. Upload your notes in PDF format.")
    st.write("2. Select a study tool.")
    st.write("3. Generate notes or practise questions.")
    st.divider()
    st.caption("Mini project built using Python, Streamlit and Gemini API.")
    st.caption("Only upload documents you are allowed to share with the AI service.")

# -------------------- PDF UPLOAD --------------------
uploaded_pdf = st.file_uploader(
    "📄 Upload your study material",
    type=["pdf"],
    help="Choose a PDF containing selectable text."
)

if uploaded_pdf:
    try:
        with st.spinner("Reading your PDF..."):
            pages = read_pdf(uploaded_pdf)
    except Exception as error:
        st.error(f"Unable to read this PDF: {error}")
        st.stop()

    if not pages:
        st.warning("No selectable text was found. This app does not currently read scanned PDFs.")
        st.stop()

    document_text = make_document_context(pages)

    st.success(f"Successfully loaded: {uploaded_pdf.name}")

    metric1, metric2, metric3 = st.columns(3)
    metric1.metric("PDF pages with text", len(pages))
    metric2.metric("Extracted characters", f"{sum(len(p['text']) for p in pages):,}")
    metric3.metric("Study tools", "4")

    st.divider()

    summary_tab, ask_tab, quiz_tab, keypoints_tab = st.tabs([
        "📝 Summary",
        "💬 Ask your notes",
        "🧠 Practice quiz",
        "⭐ Important points"
    ])

    # -------------------- SUMMARY --------------------
    with summary_tab:
        st.subheader("Make revision notes")
        summary_type = st.radio(
            "Choose summary type",
            ["Quick summary", "Detailed summary", "Exam revision notes"],
            horizontal=True
        )

        if st.button("Generate summary", type="primary", use_container_width=True):
            prompt = f"""
You are a helpful college study assistant.
Create {summary_type.lower()} from the study material below.
Use simple English, clear headings and bullet points.
Keep definitions and important concepts accurate.
Use only the uploaded material. Do not invent information.

STUDY MATERIAL:
{document_text}
"""
            with st.spinner("Preparing your summary..."):
                try:
                    answer = call_ai(prompt)
                    st.markdown(answer)
                    st.download_button(
                        "⬇️ Download summary",
                        data=answer,
                        file_name="studymate_summary.md",
                        mime="text/markdown"
                    )
                except Exception as error:
                    st.error(f"AI request failed: {error}")

    # -------------------- ASK QUESTIONS --------------------
    with ask_tab:
        st.subheader("Ask questions from your PDF")
        st.caption("Answers are based on the text extracted from your uploaded PDF.")

        question = st.text_area(
            "Your question",
            placeholder="Example: What is supervised learning? Explain with an example.",
            height=90
        )

        if st.button("Get answer", type="primary", use_container_width=True):
            if not question.strip():
                st.warning("Please enter a question first.")
            else:
                prompt = f"""
You are a college study assistant.
Answer the student's question using ONLY the uploaded study material.
Explain in simple English.
If the answer is not present, say: "I could not find this answer in the uploaded PDF."
When possible, mention the page number shown in the source labels.
Do not make up page numbers or facts.

UPLOADED STUDY MATERIAL:
{document_text}

STUDENT QUESTION:
{question}
"""
                with st.spinner("Finding an answer..."):
                    try:
                        st.markdown(call_ai(prompt))
                    except Exception as error:
                        st.error(f"AI request failed: {error}")

    # -------------------- QUIZ --------------------
    with quiz_tab:
        st.subheader("Test your understanding")
        col1, col2 = st.columns(2)
        with col1:
            question_count = st.selectbox("Number of questions", [5, 10], index=0)
        with col2:
            difficulty = st.selectbox("Difficulty", ["Easy", "Medium", "Hard"])

        if st.button("Create practice quiz", type="primary", use_container_width=True):
            prompt = f"""
Create {question_count} {difficulty.lower()} multiple-choice questions
using ONLY the study material below.

For every question:
- Give four options labelled A, B, C and D.
- Clearly show the correct answer.
- Give one short explanation.
- Use simple language.

STUDY MATERIAL:
{document_text}
"""
            with st.spinner("Creating your quiz..."):
                try:
                    quiz = call_ai(prompt)
                    st.markdown(quiz)
                    st.download_button(
                        "⬇️ Download quiz",
                        data=quiz,
                        file_name="studymate_practice_quiz.md",
                        mime="text/markdown"
                    )
                except Exception as error:
                    st.error(f"AI request failed: {error}")

    # -------------------- KEY POINTS --------------------
    with keypoints_tab:
        st.subheader("Important points to remember")
        if st.button("Find important points", type="primary", use_container_width=True):
            prompt = f"""
Read the study material and list the 10 most important points
a college student should remember for an exam.
Use short bullet points and simple English.
Use ONLY the provided material.

STUDY MATERIAL:
{document_text}
"""
            with st.spinner("Finding important points..."):
                try:
                    st.markdown(call_ai(prompt))
                except Exception as error:
                    st.error(f"AI request failed: {error}")

else:
    st.info("👆 Upload a PDF above to start studying.")
    st.subheader("What can StudyMate AI do?")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        **📝 Create summaries**
        - Quick revision notes
        - Detailed summaries
        - Exam-focused notes

        **💬 Ask questions**
        - Ask about concepts
        - Get simple explanations
        - Find answers in your notes
        """)
    with col2:
        st.markdown("""
        **🧠 Practise**
        - Generate MCQs
        - Choose quiz difficulty
        - Download practice questions

        **⭐ Revise**
        - Extract important points
        - Prepare for exams
        """)

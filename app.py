
import os
import time
import random
from io import BytesIO

import streamlit as st
from dotenv import load_dotenv
from pypdf import PdfReader
from google import genai

# ==========================================
# 1. CONFIGURATION
# ==========================================

load_dotenv()

st.set_page_config(
    page_title="StudyMate AI",
    page_icon="📘",
    layout="wide"
)

# Get API settings from .env or Streamlit Cloud Secrets
try:
    api_key = os.getenv("GEMINI_API_KEY") or st.secrets.get("GEMINI_API_KEY", "")
    model_name = os.getenv("GEMINI_MODEL") or st.secrets.get(
        "GEMINI_MODEL", "gemini-3.8-flash"
    )
except Exception:
    api_key = os.getenv("GEMINI_API_KEY", "")
    model_name = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")

api_key = api_key.strip()
model_name = model_name.strip()

# ==========================================
# 2. PAGE DESIGN
# ==========================================

st.markdown("""
<style>
    .block-container {
        max-width: 1100px;
        padding-top: 2rem;
    }

    .hero {
        padding: 25px;
        border-radius: 16px;
        background: linear-gradient(110deg, #173b70, #3677c8);
        color: white;
        margin-bottom: 25px;
    }

    .hero h1 {
        color: white;
        margin: 0;
    }

    .hero p {
        color: #e8f1ff;
        margin-top: 8px;
    }

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
    <p>Your personal AI study partner.
    Summarize notes, ask questions and prepare for exams.</p>
</div>
""", unsafe_allow_html=True)

# ==========================================
# 3. API CONNECTION
# ==========================================

if not api_key:
    st.error("Gemini API key is missing.")

    st.info("Create a .env file and add your Gemini API key.")

    st.code("""
GEMINI_API_KEY=your_actual_api_key
GEMINI_MODEL=gemini-3.8-flash
""")

    st.markdown(
        "[Get your Gemini API key](https://aistudio.google.com/apikey)"
    )

    st.stop()

client = genai.Client(api_key=api_key)

# ==========================================
# 4. AI RESPONSE FUNCTION
# ==========================================

def call_ai(prompt, attempts=3):

    for attempt in range(attempts):

        try:

            response = client.models.generate_content(
                model=model_name,
                contents=prompt
            )

            if response.text:
                return response.text

            raise RuntimeError("AI returned an empty response.")

        except Exception as error:

            error_message = str(error).upper()

            temporary_errors = [
                "503",
                "UNAVAILABLE",
                "429",
                "RESOURCE_EXHAUSTED",
                "500",
                "502",
                "504",
                "INTERNAL"
            ]

            is_temporary = any(
                code in error_message
                for code in temporary_errors
            )

            if not is_temporary or attempt == attempts - 1:
                raise error

            wait_time = (2 ** (attempt + 1)) + random.uniform(0, 0.5)

            time.sleep(wait_time)

    raise RuntimeError("Unable to get an AI response.")


# ==========================================
# 5. ERROR HANDLING
# ==========================================

def show_error(error):

    message = str(error).upper()

    if "503" in message or "UNAVAILABLE" in message:

        st.error(
            "Gemini is temporarily busy. "
            "Automatic retries were attempted. "
            "Please wait and try again."
        )

    elif "429" in message or "RESOURCE_EXHAUSTED" in message:

        st.error(
            "Gemini API usage limit reached. "
            "Check your Google AI Studio quota."
        )

    elif "404" in message or "NOT_FOUND" in message:

        st.error(
            f"Model '{model_name}' is unavailable. "
            "Check your Gemini model name and API access."
        )

    elif "401" in message or "403" in message:

        st.error(
            "API key authentication failed. "
            "Check your Gemini API key."
        )

    else:

        st.error(f"Something went wrong: {error}")


# ==========================================
# 6. PDF TEXT EXTRACTION
# ==========================================

def extract_pdf(uploaded_file):

    reader = PdfReader(BytesIO(uploaded_file.getvalue()))

    pages = []

    for page_number, page in enumerate(reader.pages, start=1):

        text = page.extract_text() or ""

        if text.strip():

            pages.append({
                "page": page_number,
                "text": text.strip()
            })

    return pages


def prepare_document(pages, max_chars=45000):

    document = []
    total_chars = 0

    for page in pages:

        page_text = (
            f"[Page {page['page']}]\n"
            f"{page['text']}"
        )

        remaining = max_chars - total_chars

        if remaining <= 0:
            break

        document.append(page_text[:remaining])

        total_chars += min(len(page_text), remaining)

    return "\n\n".join(document)


# ==========================================
# 7. SIDEBAR
# ==========================================

with st.sidebar:

    st.title("📚 StudyMate AI")

    st.markdown("### How to use")

    st.write("1. Upload your study notes.")

    st.write("2. Select a study tool.")

    st.write("3. Generate notes or practise questions.")

    st.divider()

    st.caption(
        "College mini project built using "
        "Python, Streamlit and Gemini API."
    )

    st.caption(
        "Uploaded PDF text is sent to Gemini for processing. "
        "Avoid uploading confidential documents."
    )


# ==========================================
# 8. PDF UPLOAD
# ==========================================

uploaded_file = st.file_uploader(
    "📄 Upload your study material",
    type=["pdf"]
)

if uploaded_file:

    try:

        with st.spinner("Reading your PDF..."):

            pages = extract_pdf(uploaded_file)

    except Exception as error:

        st.error(f"Unable to read PDF: {error}")

        st.stop()

    if not pages:

        st.warning(
            "No selectable text found. "
            "Scanned PDFs are not supported in this version."
        )

        st.stop()

    document_text = prepare_document(pages)

    st.success(
        f"Successfully loaded: {uploaded_file.name}"
    )

    # ======================================
    # 9. PDF INFORMATION
    # ======================================

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "PDF pages with text",
        len(pages)
    )

    col2.metric(
        "Extracted characters",
        f"{sum(len(p['text']) for p in pages):,}"
    )

    col3.metric(
        "Study tools",
        "4"
    )

    st.divider()

    # ======================================
    # 10. STUDY TABS
    # ======================================

    summary_tab, question_tab, quiz_tab, points_tab = st.tabs([
        "📝 Summary",
        "💬 Ask your notes",
        "🧠 Practice quiz",
        "⭐ Important points"
    ])

    # ======================================
    # TAB 1: SUMMARY
    # ======================================

    with summary_tab:

        st.subheader("Make revision notes")

        summary_type = st.radio(
            "Choose summary type",

            [
                "Quick summary",
                "Detailed summary",
                "Exam revision notes"
            ],

            horizontal=True
        )

        if st.button(
            "Generate summary",
            type="primary",
            use_container_width=True
        ):

            prompt = f"""
You are a helpful college study assistant.

Create {summary_type} from the uploaded study material.

Instructions:
- Use simple English.
- Use headings and bullet points.
- Explain important concepts.
- Include definitions and examples when present.
- Do not invent information.
- Use only the uploaded material.

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

                    show_error(error)

    # ======================================
    # TAB 2: ASK QUESTIONS
    # ======================================

    with question_tab:

        st.subheader("Ask questions from your PDF")

        st.caption(
            "Ask anything related to your uploaded study material."
        )

        question = st.text_area(
            "Enter your question",

            placeholder=(
                "Example: Explain supervised learning "
                "in simple English."
            ),

            height=100
        )

        if st.button(
            "Get answer",
            type="primary",
            use_container_width=True
        ):

            if not question.strip():

                st.warning("Please enter a question.")

            else:

                prompt = f"""
You are a helpful college study assistant.

Answer the student's question using ONLY the
uploaded study material.

Instructions:
- Use simple English.
- Explain step by step.
- Give examples if present in the notes.
- Mention relevant page numbers when possible.
- Do not invent facts.

If the answer is not available, say:

"I could not find this answer in the uploaded PDF."

STUDY MATERIAL:

{document_text}

STUDENT QUESTION:

{question}
"""

                with st.spinner("Finding your answer..."):

                    try:

                        answer = call_ai(prompt)

                        st.subheader("AI Answer")

                        st.markdown(answer)

                    except Exception as error:

                        show_error(error)

    # ======================================
    # TAB 3: QUIZ GENERATOR
    # ======================================

    with quiz_tab:

        st.subheader("Test your knowledge")

        col1, col2 = st.columns(2)

        with col1:

            number_of_questions = st.selectbox(
                "Number of questions",
                [5, 10]
            )

        with col2:

            difficulty = st.selectbox(
                "Difficulty",
                ["Easy", "Medium", "Hard"]
            )

        if st.button(
            "Generate quiz",
            type="primary",
            use_container_width=True
        ):

            prompt = f"""
Create {number_of_questions} {difficulty} level
multiple-choice questions using ONLY the
uploaded study material.

For every question:

1. Write the question.
2. Give four options A, B, C and D.
3. Show the correct answer.
4. Give a short explanation.

Use simple English.

Do not include information outside the notes.

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

                        file_name="studymate_quiz.md",

                        mime="text/markdown"
                    )

                except Exception as error:

                    show_error(error)

    # ======================================
    # TAB 4: IMPORTANT POINTS
    # ======================================

    with points_tab:

        st.subheader("Important exam points")

        if st.button(
            "Find important points",
            type="primary",
            use_container_width=True
        ):

            prompt = f"""
Read the uploaded study material.

Find the 10 most important points
for a college examination.

Instructions:
- Use short bullet points.
- Use simple English.
- Focus on important definitions and concepts.
- Use only the uploaded material.
- Do not invent information.

STUDY MATERIAL:

{document_text}
"""

            with st.spinner("Finding important points..."):

                try:

                    answer = call_ai(prompt)

                    st.markdown(answer)

                except Exception as error:

                    show_error(error)


# ==========================================
# 11. HOME SCREEN
# ==========================================

else:

    st.info(
        "👆 Upload a PDF above to start studying."
    )

    st.subheader("What can StudyMate AI do?")

    col1, col2 = st.columns(2)

    with col1:

        st.markdown("""
        ### 📝 Create summaries

        - Quick revision notes
        - Detailed summaries
        - Exam-focused notes

        ### 💬 Ask questions

        - Ask about concepts
        - Get simple explanations
        - Understand difficult topics
        """)

    with col2:

        st.markdown("""
        ### 🧠 Practise

        - Generate MCQs
        - Choose quiz difficulty
        - Download practice questions

        ### ⭐ Revise

        - Extract important points
        - Prepare for examinations
        """)

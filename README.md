# StudyMate AI – College Mini Project

StudyMate AI is a beginner-friendly AI study assistant made with Python and Streamlit.

## Features

1. Upload study notes in PDF format.
2. Generate quick summaries, detailed summaries, or exam revision notes.
3. Ask questions about the uploaded PDF.
4. Generate multiple-choice practice quizzes.
5. Extract important exam points.
6. Download generated summaries and quizzes.

## Technologies

- Python
- Streamlit
- Google Gemini API
- PyPDF
- python-dotenv

## Installation

### Step 1: Open the project folder in VS Code

### Step 2: Create a virtual environment

macOS:
```bash
python3 -m venv .venv
source .venv/bin/activate
```

Windows:
```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
```

### Step 3: Install requirements

```bash
pip install -r requirements.txt
```

### Step 4: Add your Gemini API key

Copy `.env.example` and rename the copy to `.env`.
Put your key in the file:

```env
GEMINI_API_KEY=your_actual_api_key
GEMINI_MODEL=gemini-2.5-flash
```

Get a key from https://aistudio.google.com/apikey.

Never share your API key or upload `.env` to GitHub.

### Step 5: Run the project

```bash
streamlit run app.py
```

The app normally opens at http://localhost:8501.

## How it works

1. The student uploads a PDF.
2. PyPDF extracts text page by page.
3. The student chooses a feature.
4. The app sends the extracted text and instruction to Gemini.
5. Gemini creates a response.
6. Streamlit displays the result.

## Limitations

- Supports PDF files with selectable text.
- Scanned/image-only PDFs are not supported.
- The app sends extracted PDF text to the Gemini API.
- The app includes a context-size limit, so very long PDFs may be shortened.
- AI answers may contain mistakes. Check important information against the original notes.

## Future improvements

- Add support for DOCX files.
- Save previous summaries and quiz results.
- Add a simple quiz score calculator.
- Add OCR for scanned PDFs.

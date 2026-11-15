# StudyMate AI – Project Report

## 1. Introduction
StudyMate AI is a simple AI-powered study assistant. It helps students understand and revise their study material using a PDF upload feature.

## 2. Problem Statement
Students often need to read lengthy notes and textbooks to prepare for examinations. Finding important topics and creating revision questions can take time. StudyMate AI provides basic tools to make this process easier.

## 3. Objectives
- Upload PDF study material.
- Generate summaries.
- Answer questions based on uploaded notes.
- Generate multiple-choice questions.
- Extract important points for revision.

## 4. Technologies Used
- Python: main programming language.
- Streamlit: web interface.
- Google Gemini API: AI text generation.
- PyPDF: PDF text extraction.
- python-dotenv: API key configuration.

## 5. Modules
1. PDF Upload Module
2. Summary Generation Module
3. Question Answering Module
4. Quiz Generation Module
5. Important Points Module

## 6. Working
The student uploads a PDF. PyPDF extracts its text. When the student selects a feature, the application sends the extracted text and the student's instruction to the Gemini API. The generated response is displayed in the Streamlit application.

## 7. Advantages
- Easy to use.
- Saves time during revision.
- Helps students practise questions.
- Supports learning from personal notes.

## 8. Limitations
- Requires internet access and a working API key.
- Scanned PDFs are not supported.
- AI-generated answers should be checked for accuracy.

## 9. Future Scope
- Add DOCX support.
- Add OCR.
- Save student history.
- Add quiz scoring.
- Add more languages.

## 10. Conclusion
StudyMate AI demonstrates how Python, a web application framework, PDF processing and a generative AI API can be combined to create a useful student-focused application.

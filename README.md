# 🤖 Virtual HR Interview Q&A Prediction App

The **Virtual HR Interview Q&A Predictor** is an AI-powered web application that generates personalized HR interview 
questions and answers based on a user's resume. Built using **Flask**, **Python**, and **Google Gemini AI**, the app provides
an interactive mock interview experience with voice output, difficulty level selection, and a clean, modern UI.

---

## 🚀 Features

- Upload resume in `.pdf` or `.docx` format.
- Automatically extracts text from the resume.
- Choose difficulty level: Easy 🟢, Medium 🟡, Hard 🔴.
- Generates **10 personalized HR questions and sample answers** using Google Gemini AI.
- Typewriter-style display with **Text-to-Speech** for a real interview feel.
- "Next" button navigation and option to view full Q&A list.
- Responsive and stylish UI with animated elements and voice interaction.
- Supports both DOCX and PDF resumes.
- Automatically handles invalid resumes or empty files.

---

## 🛠️ Tech Stack

- **Frontend**: HTML5, TailwindCSS, JavaScript (with Web Speech API)
- **Backend**: Python, Flask
- **AI Model**: Google Gemini 1.5 Flash (via `google-generativeai`)
- **Resume Parsing**: `PyPDF2`, `python-docx`
- **Templating & Data Binding**: Jinja2 (via Flask)
- **Text-to-Speech**: JavaScript `SpeechSynthesis` API

---
Project Architecture
Virtual-HR-Interview-QnA/
│
├── app.py             # Main Flask application
└── templates/
    └── resume.html    # HTML template for resume upload and interview UI


---
📜 Resume Format Guidelines
Upload a .pdf or .docx file that includes your educational background, skills, and experience. The AI will generate interview questions based on the extracted content.

Valid Formats:

.pdf

.docx
---
🔐 Google Gemini API Setup
To use Gemini AI:

Visit Google AI Studio to generate your API key.

Replace the placeholder key in your code:

genai.configure(api_key="YOUR_API_KEY")
🎤 Using Voice Interaction
The app uses your browser's built-in SpeechSynthesis API to read questions aloud. Ensure that:

Your browser supports Web Speech API (Chrome recommended).

Audio is enabled on your device.
---
📋 Sample Use Case
Enter your name.

Upload your resume.

Choose difficulty.

Click Start Interview.

View & listen to one question at a time or see all Q&As at the end.
---
✅ Dependencies (requirements.txt)
Flask==2.3.3
Werkzeug==2.3.7
python-docx==1.1.0
PyPDF2==3.0.1
google-generativeai==0.3.2






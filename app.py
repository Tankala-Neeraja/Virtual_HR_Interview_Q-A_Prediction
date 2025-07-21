from flask import Flask, request, render_template_string
import os
from werkzeug.utils import secure_filename
from docx import Document
import PyPDF2
import google.generativeai as genai
import re
import random

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# ✅ Configure Gemini API Key
genai.configure(api_key="AIzaSyBZ7yEoHQDtcicboCpULLmYA9bxcbCdKEQ")  # Replace with your actual Gemini API key

def extract_text_from_pdf(file_path):
    text = ''
    with open(file_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        for page in reader.pages:
            text += page.extract_text() or ''
    return text

def extract_text_from_docx(file_path):
    doc = Document(file_path)
    return '\n'.join([para.text for para in doc.paragraphs])

def generate_questions_and_answers(resume_text, difficulty):
    resume_text = resume_text[:2000]
    if not resume_text.strip():
        return "Error: Empty resume text. Please upload a valid file."
    seed = random.randint(10000, 99999)
    prompt = (
        f"Given the following resume content, generate 10 short HR interview questions "
        f"that a friendly virtual robot might ask, each followed by a short example answer. "
        f"Tailor the question difficulty to be '{difficulty}'. "
        f"Make sure the questions are unique for seed {seed}.\n\n"
        f"{resume_text}\n\n"
        "Format the output as:\n"
        "Q1: question?\nA1: answer\nQ2: question?\nA2: answer\n... up to Q10/A10."
    )
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt)
        if hasattr(response, 'text') and response.text:
            return response.text.strip()
        return "Error: Gemini API returned no content."
    except Exception as e:
        return f"Error: Could not generate questions and answers. {str(e)}"

@app.route('/', methods=['GET'])
def index():
    return render_template_string('''
<!DOCTYPE html>
<html lang="en">
<head>
  <title>Upload Resume</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <style>
    body { font-family: 'Segoe UI', sans-serif; }
  </style>
</head>
<body class="bg-gradient-to-br from-[#0f0c29] via-[#302b63] to-[#24243e] min-h-screen flex items-center justify-center p-4">
  <div class="backdrop-blur-md bg-white/10 border border-white/20 rounded-2xl p-10 max-w-2xl w-full text-center shadow-2xl">
    <h2 class="text-4xl font-extrabold mb-8 text-cyan-300 animate-pulse">🚀 Virtual HR Interview Questions</h2>
    <form method="POST" action="/upload" enctype="multipart/form-data" class="space-y-6 text-white">
      <input type="text" name="fullname" placeholder="Enter your full name"
        class="w-full p-4 rounded-lg bg-white/20 text-white placeholder-gray-300 focus:outline-none focus:ring-2 focus:ring-cyan-400" required>

      <input type="file" name="resume" accept=".pdf,.docx"
        class="w-full p-4 rounded-lg bg-white/20 text-white placeholder-gray-300 focus:outline-none focus:ring-2 focus:ring-cyan-400" required>

      <select name="difficulty" required
        class="w-full p-4 rounded-lg bg-white/20 text-cyan-200 focus:outline-none focus:ring-2 focus:ring-cyan-400">
        <option value="">Select Difficulty</option>
        <option value="easy">🟢 Easy</option>
        <option value="medium">🟡 Medium</option>
        <option value="hard">🔴 Hard</option>
      </select>

      <button type="submit"
        class="w-full py-4 rounded-lg bg-cyan-400 text-black text-lg font-semibold hover:bg-cyan-300 transition duration-300">
        🎤 Start Interview
      </button>
    </form>
  </div>
</body>
</html>
''')

@app.route('/upload', methods=['POST'])
def upload_resume():
    fullname = request.form['fullname']
    difficulty = request.form['difficulty']
    file = request.files['resume']

    if file:
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        if filename.endswith('.pdf'):
            resume_text = extract_text_from_pdf(file_path)
        elif filename.endswith('.docx'):
            resume_text = extract_text_from_docx(file_path)
        else:
            return "Unsupported file format. Please upload a .pdf or .docx file."

        qna_text = generate_questions_and_answers(resume_text, difficulty)

        if qna_text.startswith("Error"):
            return render_template_string('<p style="color:red;">{{ error_msg }}</p><a href="/">Go Back</a>', error_msg=qna_text)

        # ✅ Improved regex for Q&A extraction
        pattern = r"Q\d+:\s*(.+?)\s*A\d+:\s*(.+?)(?=\s*Q\d+:|$)"
        matches = re.findall(pattern, qna_text, re.DOTALL)
        qna_pairs = [{"question": q.strip(), "answer": a.strip()} for q, a in matches]

        if not qna_pairs:
            qna_pairs.append({"question": "Sorry, no valid questions generated.", "answer": "Try uploading again."})

        return render_template_string('''
<!DOCTYPE html>
<html lang="en">
<head>
  <title>Virtual HR Interview</title>
  <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gradient-to-br from-[#0f0c29] via-[#302b63] to-[#24243e] min-h-screen flex flex-col items-center justify-center text-white p-6">
  <div class="w-full max-w-3xl p-8 backdrop-blur-lg bg-white/10 border border-white/20 rounded-2xl shadow-xl text-center">
    <img src="https://ik.imagekit.io/qa6pqsoex/6862967_28638.jpg?updatedAt=1751336210370" class="w-32 mx-auto mb-6 animate-pulse" alt="Robot AI">
    <h2 id="greeting" class="text-3xl font-bold text-cyan-300 mb-6 animate-pulse">Hello {{ name }}, your {{ diff }} interview is ready!</h2>
    <div class="min-h-[120px]" id="typewriter"></div>
    <div class="answer hidden mt-4 text-green-200"></div>
    <div class="flex flex-col sm:flex-row gap-4 mt-6 justify-center">
      <button id="continue-btn" class="px-6 py-2 bg-cyan-400 text-black font-bold rounded hover:bg-cyan-300">Continue</button>
      <button id="next-btn" style="display:none;" class="px-6 py-2 bg-cyan-400 text-black font-bold rounded hover:bg-cyan-300">Next</button>
      <button id="show-list-btn" style="display:none;" class="px-6 py-2 bg-cyan-400 text-black font-bold rounded hover:bg-cyan-300">Show All Q&A</button>
    </div>
    <a href="/" id="back-home" style="display:none;" class="mt-6 inline-block px-6 py-2 bg-cyan-400 text-black font-bold rounded hover:bg-cyan-300">← Back Home</a>
  </div>
<script>
const qna = {{ qna_pairs|tojson }};
const container = document.getElementById('typewriter');
const nextBtn = document.getElementById('next-btn');
const continueBtn = document.getElementById('continue-btn');
const showListBtn = document.getElementById('show-list-btn');
const backHomeBtn = document.getElementById('back-home');
const greeting = document.getElementById('greeting');
let index = 0;
let busy = false;

function speak(text) {
  speechSynthesis.cancel();
  return new Promise(resolve => {
    let utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = 'en-US'; utterance.pitch = 1.2; utterance.rate = 1;
    utterance.volume = 1; utterance.onend = resolve;
    speechSynthesis.speak(utterance);
  });
}

function typeWriterEffect(text) {
  return new Promise(resolve => {
    let i = 0;
    container.innerHTML = "";
    function type() {
      if (i < text.length) {
        container.innerHTML += text.charAt(i);
        i++;
        setTimeout(type, 40);
      } else resolve();
    }
    type();
  });
}

async function showQnA(i) {
  if (busy) return;
  busy = true;
  greeting.style.display = "none";
  container.innerHTML = "";
  document.querySelector('.answer').classList.add('hidden');
  document.querySelector('.answer').innerHTML = "";

  if (i >= qna.length) {
    container.innerHTML = "<p class='text-cyan-200'>That's all. Thank you!</p>";
    nextBtn.style.display = "none";
    showListBtn.style.display = "inline-block";
    busy = false;
    return;
  }

  nextBtn.disabled = true;
  await typeWriterEffect("Q: " + qna[i].question);
  await speak("Question: " + qna[i].question);

  let btn = document.createElement('button');
  btn.id = "see-answer-btn";
  btn.innerText = "Show Answer";
  btn.className = "mt-4 mx-auto block px-6 py-2 bg-cyan-500 text-black font-bold rounded hover:bg-cyan-400 transition";
  btn.onclick = () => {
    document.querySelector('.answer').innerHTML = "A: " + qna[i].answer;
    document.querySelector('.answer').classList.remove('hidden');
    btn.style.display = "none";
  };
  container.appendChild(btn);

  nextBtn.style.display = "inline-block";
  nextBtn.disabled = false;
  busy = false;
}

continueBtn.onclick = () => { continueBtn.style.display = "none"; showQnA(index); };
nextBtn.onclick = () => { if (!busy) { index++; showQnA(index); } };
showListBtn.onclick = () => {
  speechSynthesis.cancel();
  let listHTML = "<h3 class='text-cyan-300 font-bold text-xl mb-4'>Full List of Q&A</h3>";
  qna.forEach((pair, i) => {
    listHTML += `<div class="mb-4"><div class="font-bold">Q${i+1}: ${pair.question}</div><div>A${i+1}: ${pair.answer}</div></div>`;
  });
  container.innerHTML = listHTML;
  showListBtn.style.display = "none";
  backHomeBtn.style.display = "inline-block";
};
</script>
</body>
</html>
''', name=fullname, diff=difficulty, qna_pairs=qna_pairs)

    return "No file uploaded."

if __name__ == '__main__':
    app.run(debug=True)

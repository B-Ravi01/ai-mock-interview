AI Mock Interview Platform

An AI-powered mock interview system built with Flask that simulates real interview scenarios. The platform extracts information from a student’s resume, generates tailored interview questions based on the company and job role, asks questions via voice, collects spoken answers, and provides feedback to improve performance.

🚀 Features

📄 Resume Parsing – Upload a PDF resume and extract key details.

🎯 Customized Interview Questions – Generates 10 job-specific questions using AI APIs.

🎙 Voice Interaction – Questions are asked via text-to-speech, and student responses are recorded.

✍ Speech-to-Text Conversion – Converts answers into text for analysis.

📊 AI Response Analysis – Evaluates answers and suggests improvements.

🌐 Web-based Interface – Easy-to-use UI for students.

🛠 Tech Stack

Backend: Flask (Python)

Frontend: HTML, CSS, JavaScript

AI/ML: Hugging Face / Gemini / ChatGPT APIs (for question generation & answer analysis)

Speech Processing: gTTS / pyttsx3 (Text-to-Speech), SpeechRecognition / Whisper (Speech-to-Text)

Resume Parsing: PyPDF2 / pdfminer

📂 Project Structure
ai-mock-interview/
│── app.py              # Flask backend
│── static/             # CSS, JS, images
│── templates/          # HTML templates (index.html, interview.html, result.html)
│── requirements.txt    # Python dependencies
│── README.md           # Project documentation

⚙️ Installation & Setup

Clone the repo

git clone https://github.com/B-Ravi01/ai-mock-interview.git
cd ai-mock-interview


Create virtual environment & activate

python -m venv venv
source venv/bin/activate   # Linux/Mac
venv\Scripts\activate      # Windows


Install dependencies

pip install -r requirements.txt


Set up environment variables

Add your API keys (e.g., Hugging Face, Gemini, or OpenAI).

Run the application

flask run


Open in browser:

http://127.0.0.1:5000/

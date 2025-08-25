from flask import Flask, request, jsonify, render_template
import os
import PyPDF2
from werkzeug.utils import secure_filename
from openai import OpenAI
from dotenv import load_dotenv

# 1. Load environment variables
# ===================================
load_dotenv()  # loads .env file

# 2. Initialize the Flask Application
# ===================================
app = Flask(__name__)

# 3. Configuration
# =================================
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024

# 4. API Key and Base URL from .env
# =================================
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
BASE_URL = os.getenv("BASE_URL")

if not OPENROUTER_API_KEY or not BASE_URL:
    raise ValueError("Missing OPENROUTER_API_KEY or BASE_URL in .env file")

# Initialize the OpenAI client to point to OpenRouter
client = OpenAI(
    base_url=BASE_URL,
    api_key=OPENROUTER_API_KEY,
)

# 5. Helper Functions
# =================================
def extract_text_from_pdf(pdf_path):
    """Extracts text from a given PDF file."""
    try:
        with open(pdf_path, 'rb') as pdf_file:
            reader = PyPDF2.PdfReader(pdf_file)
            text = "".join(page.extract_text() or "" for page in reader.pages)
        return text
    except Exception as e:
        print(f"Error extracting text from PDF: {e}")
        return None


def generate_interview_questions(resume_text, student_name, company_name, job_role):
    """Generates interview questions using the OpenRouter AI API."""

    prompt = f"""
    You are an expert technical recruiter creating a tailored interview.
    Your task is to generate exactly 10 interview questions for a candidate named {student_name}, 
    who is applying for the position of {job_role} at {company_name}.

    **CRITICAL INSTRUCTION:** You MUST base the majority of the questions (at least 6 of the 10) 
    directly on the specific skills, projects, and experiences listed in the candidate's resume below.

    --- CANDIDATE'S RESUME TEXT ---
    {resume_text[:2500]}
    --- END OF RESUME ---

    The remaining questions can be behavioral or standard technical questions relevant to the {job_role} role.
    Return the questions as a numbered list.
    """
    try:
        completion = client.chat.completions.create(
            model="mistralai/mistral-7b-instruct:free",
            messages=[
                {"role": "system",
                 "content": "You are an expert interviewer creating highly specific, resume-based questions."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.6,
        )
        questions_text = completion.choices[0].message.content
        return [q.strip() for q in questions_text.split('\n') if q.strip() and len(q) > 5]
    except Exception as e:
        print(f"API Request Error (Questions): {e}")
        return {"error": f"Failed to generate questions: {e}"}


# 6. Application Routes
# =================================
@app.route('/')
def index():
    return render_template('index.html')


@app.route('/interview-session')
def interview_session():
    return render_template('interview.html')


@app.route('/interview', methods=['POST'])
def handle_interview_setup():
    try:
        student_name = request.form.get('student-name')
        company_name = request.form.get('company-name')
        job_role = request.form.get('job-role')

        if 'resume-upload' not in request.files or request.files['resume-upload'].filename == '':
            return jsonify({"error": "No resume file provided"}), 400

        resume_file = request.files['resume-upload']
        filename = secure_filename(resume_file.filename)
        resume_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        resume_file.save(resume_path)

        resume_text = extract_text_from_pdf(resume_path)
        os.remove(resume_path)

        if resume_text is None:
            return jsonify({"error": "Could not read text from PDF."}), 500

        questions = generate_interview_questions(resume_text, student_name, company_name, job_role)

        if isinstance(questions, dict) and "error" in questions:
            return jsonify(questions), 500

        return jsonify({
            "message": "Questions generated successfully!",
            "questions": questions,
            "studentName": student_name
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/feedback', methods=['POST'])
def get_feedback():
    data = request.get_json()
    if not data or 'interviewData' not in data:
        return jsonify({"error": "Missing interview data"}), 400

    interview_log = data['interviewData']
    student_name = data.get('studentName', 'the candidate')

    transcript = "".join(f"Q: {item['question']}\nA: {item['answer']}\n\n" for item in interview_log)

    prompt = f"""
    You are an expert career coach providing feedback for a mock interview for {student_name}.
    Based on the following transcript, provide constructive feedback. 
    Identify strengths and provide specific, actionable advice on areas for improvement.

    --- TRANSCRIPT ---
    {transcript}
    ---
    """
    try:
        completion = client.chat.completions.create(
            model="mistralai/mistral-7b-instruct:free",
            messages=[
                {"role": "system", "content": "You are an expert career coach."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.6,
        )
        feedback_text = completion.choices[0].message.content
        return jsonify({"feedback": feedback_text})
    except Exception as e:
        print(f"API Request Error (Feedback): {e}")
        return jsonify({"error": f"Failed to generate feedback: {e}"}), 500


# 7. Run the Application
# ==========================
if __name__ == '__main__':
    app.run(debug=True)

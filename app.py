import os
import fitz  # PyMuPDF
from flask import Flask, request, render_template, send_file
from werkzeug.utils import secure_filename
from pdf2image import convert_from_path
from PIL import Image
import pytesseract
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import subprocess

# Explicit path for tesseract
pytesseract.pytesseract.tesseract_cmd = "/usr/bin/tesseract"

UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'outputs'
ALLOWED_EXTENSIONS = {'pdf', 'jpg', 'jpeg'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

KEYWORDS = ['invoice', 'total', 'date', 'amount', 'paid', 'AUTOSAR', 'shiva']

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_text_from_pdf(pdf_path):
    # Your existing code here
    return "Dummy text for now"  # placeholder for testing

def extract_text_from_image(image_path):
    # Your existing code here
    return "Dummy text for now"

def extract_keywords(text, keywords):
    # Your existing code here
    return text

def generate_pdf(text, output_path):
    # Your existing code here
    pass

@app.route('/check')
def check_tools():
    try:
        poppler_check = subprocess.run(["pdftoppm", "-v"], capture_output=True, text=True)
        poppler_installed = "✔️ Installed" if poppler_check.returncode == 0 else "❌ Not installed"

        tesseract_check = subprocess.run(["tesseract", "--version"], capture_output=True, text=True)
        tesseract_installed = "✔️ Installed" if tesseract_check.returncode == 0 else "❌ Not installed"

        result = f"""
        <h2>Tools Check</h2>
        <p>Poppler (pdftoppm): {poppler_installed}</p>
        <pre>{poppler_check.stdout}</pre>
        <p>Tesseract OCR: {tesseract_installed}</p>
        <pre>{tesseract_check.stdout}</pre>
        """
        return result
    except Exception as e:
        return f"<p>❌ Error checking tools: {e}</p>"

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    # Your existing code here
    return "Upload page placeholder"

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port, debug=True)

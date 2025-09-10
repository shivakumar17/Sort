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

# Detect environment by checking if binaries exist
if os.path.exists('/usr/bin/tesseract'):
    pytesseract.pytesseract.tesseract_cmd = '/usr/bin/tesseract'
    print("Running on Linux, using Tesseract from:", pytesseract.pytesseract.tesseract_cmd)
else:
    # Fallback for Windows
    pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    print("Running on Windows, using Tesseract from:", pytesseract.pytesseract.tesseract_cmd)

if os.path.exists('/usr/bin/pdftoppm'):
    POPPLER_PATH = '/usr/bin'
    print("Poppler found at /usr/bin")
else:
    POPPLER_PATH = r"C:\poppler\Library\bin"
    print("Poppler fallback path:", POPPLER_PATH)

UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'outputs'
ALLOWED_EXTENSIONS = {'pdf', 'jpg', 'jpeg'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

KEYWORDS = ['invoice', 'total', 'date', 'amount', 'paid', 'AUTOSAR', 'telugu', 'mother', 'Aadhaar']

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_text_from_pdf(pdf_path):
    text = ""
    try:
        doc = fitz.open(pdf_path)
    except Exception as e:
        print(f"Error opening PDF: {e}")
        return "[Error opening PDF]"

    for i in range(len(doc)):
        try:
            page = doc[i]
            page_text = page.get_text().strip()
            if page_text:
                text += page_text + "\n"

            try:
                images = convert_from_path(pdf_path, first_page=i+1, last_page=i+1, poppler_path=POPPLER_PATH)
                for image in images:
                    ocr_text = pytesseract.image_to_string(image, lang='eng+tel')
                    print(f"OCR page {i+1} content:\n{ocr_text}")
                    if ocr_text.strip():
                        text += ocr_text + "\n"
            except Exception as ocr_error:
                print(f"OCR failed on page {i+1}: {ocr_error}")
                text += f"[OCR error on page {i+1}]\n"

        except Exception as page_error:
            print(f"Error reading page {i+1}: {page_error}")
            text += f"[Error reading page {i+1}]\n"
    return text

def extract_text_from_image(image_path):
    try:
        image = Image.open(image_path)
        ocr_text = pytesseract.image_to_string(image, lang='eng+tel')
        print(f"OCR image content:\n{ocr_text}")
        return ocr_text
    except Exception as e:
        print(f"OCR failed on image {image_path}: {e}")
        return "[OCR error on image]"

def extract_keywords(text, keywords):
    found = []
    for line in text.splitlines():
        for word in keywords:
            if word.lower() in line.lower():
                found.append(line)
                break
    return "\n".join(found) if found else "No keywords found."

def generate_pdf(text, output_path):
    try:
        c = canvas.Canvas(output_path, pagesize=letter)
        width, height = letter
        y = height - 50
        lines = text.split('\n') or ["No content extracted."]
        for line in lines:
            if y < 50:
                c.showPage()
                y = height - 50
            c.drawString(50, y, line.strip())
            y -= 15
        c.save()
    except Exception as e:
        print(f"PDF generation failed: {e}")

@app.route('/check')
def check_tools():
    try:
        poppler_check = subprocess.run([os.path.join(POPPLER_PATH, "pdftoppm"), "-v"], capture_output=True, text=True)
        poppler_installed = "✔️ Installed" if poppler_check.returncode == 0 else "❌ Not installed"

        tesseract_check = subprocess.run([pytesseract.pytesseract.tesseract_cmd, "--version"], capture_output=True, text=True)
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

@app.route('/', methods=['GET',]()

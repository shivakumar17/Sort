import os
import fitz  # PyMuPDF
from flask import Flask, request, render_template, send_file
from werkzeug.utils import secure_filename
from pdf2image import convert_from_path
from PIL import Image
import pytesseract
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'outputs'
ALLOWED_EXTENSIONS = {'pdf', 'jpg', 'jpeg'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Keywords to look for
KEYWORDS = ['invoice', 'total', 'date', 'amount', 'paid', 'AUTOSAR', 'shiva']


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def extract_text_from_pdf(pdf_path):
    text = ""
    try:
        doc = fitz.open(pdf_path)
    except Exception as e:
        print(f"Error opening PDF: {e}")
        return "[Error opening PDF]"

    for i, page in enumerate(doc):
        try:
            page_text = page.get_text().strip()
            if page_text:
                text += page_text + "\n"
            else:
                try:
                images = convert_from_path(pdf_path, first_page=i+1, last_page=i+1)
                for image in images:
                    ocr_text = pytesseract.image_to_string(image)
                    print(f"OCR page {i+1} content:\n{ocr_text}")
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
        return pytesseract.image_to_string(image)
    except Exception as e:
        print(f"Image OCR failed: {e}")
        return "[Error extracting text from image]"


def extract_keywords(text, keywords):
    found = []
    for line in text.splitlines():
        for word in keywords:
            if word.lower() in line.lower():
                found.append(line)
                break
    return "\n".join(found)


def generate_pdf(text, output_path):
    try:
        c = canvas.Canvas(output_path, pagesize=letter)
        width, height = letter
        y = height - 50
        for line in text.split('\n'):
            if y < 50:
                c.showPage()
                y = height - 50
            c.drawString(50, y, line)
            y -= 15
        c.save()
    except Exception as e:
        print(f"PDF generation failed: {e}")


@app.route('/', methods=['GET', 'POST'])
def upload_file():
    try:
        if request.method == 'POST':
            uploaded_file = request.files['file']
            if uploaded_file and allowed_file(uploaded_file.filename):
                filename = secure_filename(uploaded_file.filename)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                uploaded_file.save(file_path)

                ext = filename.rsplit('.', 1)[1].lower()
                if ext == 'pdf':
                    text = extract_text_from_pdf(file_path)
                else:
                    text = extract_text_from_image(file_path)

                filtered_text = extract_keywords(text, KEYWORDS)
                output_pdf_path = os.path.join(app.config['OUTPUT_FOLDER'], f'output_{filename}.pdf')
                generate_pdf(filtered_text, output_pdf_path)

                return send_file(output_pdf_path, as_attachment=True)

            return "Invalid file type. Only .pdf and .jpg are allowed."
        return render_template('upload.html')

    except Exception as e:
        print(f"🔥 Internal Server Error: {e}")
        return "Internal Server Error. Please check server logs.", 500


if __name__ == '__main__':
    app.run(debug=True)

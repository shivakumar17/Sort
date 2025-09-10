# Use official Python image as base
FROM python:3.11-slim

# Install tesseract, language packs, and poppler-utils
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-eng \
    tesseract-ocr-tel \
    poppler-utils \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy all files
COPY . /app

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose port 10000
EXPOSE 10000

# Run the application
CMD ["python", "app.py"]

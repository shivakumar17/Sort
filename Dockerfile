# Use official Python image as base
FROM python:3.11-slim

# Install tesseract and poppler-utils
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    poppler-utils \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy all files
COPY . /app

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose port 10000 (or whatever your app uses)
EXPOSE 10000

# Command to run the app
CMD ["python", "app.py"]

FROM python:3.10-slim

WORKDIR /app

# Install system dependencies for PyMuPDF
RUN apt-get update && apt-get install -y \
    build-essential \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Install dependencies
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install --default-timeout=100 --retries=10 -r requirements.txt \
    -f https://download.pytorch.org/whl/torch_stable.html

# Copy your project files
COPY . /app

CMD ["python", "main.py"]

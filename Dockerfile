# ===== 1. Base Python Image =====
FROM python:3.9-slim

# ===== 2. Set working directory =====
WORKDIR /app

# ==== Copy code ====
COPY . /app

# ===== Install OS dependencies =====
RUN apt-get update && apt-get install -y \
    build-essential \
    libglib2.0-0 \
    libgl1-mesa-glx \
    && rm -rf /var/lib/apt/lists/*

# ===== 5. Install Python packages (cached!) =====
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# ===== Download NLTK punkt only once (cached) =====
RUN python -c "import nltk; nltk.download('punkt')"

EXPOSE 8501

# ==== Set entrypoint ====
CMD ["python3", "-m", "streamlit", "run", "frontend/app.py"]

# ===== 1. Base Python Image =====
FROM python:3.9-slim

# ===== 2. Set working directory =====
WORKDIR /app

# ===== 3. Install OS dependencies =====
RUN apt-get update && apt-get install -y \
    build-essential \
    libglib2.0-0 \
    libgl1-mesa-glx \
    && rm -rf /var/lib/apt/lists/*

# ===== 4. Copy only requirements.txt to install dependencies =====
COPY requirements.txt ./

# ===== 5. Install Python packages (cached!) =====
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# ===== 6. Download NLTK punkt only once (cached) =====
RUN python -c "import nltk; nltk.download('punkt')"

# ===== 7. CMD chỉ định sẵn, không copy source nữa =====
CMD ["python3", "-m", "streamlit", "run", "frontend/app.py"]

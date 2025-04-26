# 🚀 EM AI Chatbot

This project is a **Streamlit-based chatbot** powered by **RAG (Retrieval-Augmented Generation)**, supporting document uploads (PDF, TXT), Google Sheets integration, and real-time traffic control based on RAM/CPU usage.  
The app is designed to run inside a **Docker container** for easy deployment.

---

## 🔑 Environment Variables

You must create a `.env` file at the **project root** with the following content:

```env
# OpenAI API
OPENAI_API_KEY=your_openai_api_key


# Firebase credentials, Google Cloud API, Google Sheet Token, ... 
=> Check .env for more details

# Other configs
PROJECT_NAME=EM_AI_Chatbot
✅ The src/utils/config.py will automatically load these values at runtime using python-dotenv.
```

⚙️ How to Run Locally (Without Docker)
## 🚀 How to Run Locally (Without Docker)

### Clone the repository
```bash
git clone https://github.com/DucBox/OLB_Chatbot.git
cd OLB_Chatbot
```

### Install Python packages
```bash
pip install -r requirements.txt
```

### Create `.env` file
Create a `.env` file in the project root and set your credentials as shown [here](#-environment-variables).

### Run the app
```bash
streamlit run frontend/app.py
```

---

## 🐳 How to Build and Run with Docker

### Make sure you have Docker installed

### Build the Docker image
```bash
docker build -t em-ai-chatbot .
```

### Run the container
```bash
docker run --env-file .env -p 8501:8501 em-ai-chatbot
```

- `--env-file .env`: Pass environment variables into the container.

The app will be accessible at:
👉 http://localhost:8501

Real-time Streaming:
Chat response is streamed gradually for better user experience.

✨ Features
🔐 User login/register system with Firebase

📚 Upload & Embed PDF, TXT documents

📊 Import Google Sheet content

🧠 Chat with documents using OpenAI

🚦 Traffic management by RAM/CPU usage

📈 Admin panel to view traffic queue and document database

🐳 Easy Docker deployment

🤝 Acknowledgments
Special thanks to Educational Missions - "Dự Án Cho EM" for inspiring this chatbot project. ❤️

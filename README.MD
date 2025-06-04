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
🤝 Acknowledgments
Special thanks to Educational Missions - "Dự Án Cho EM" for inspiring this chatbot project. ❤️

---

## 📜 License & Author
- 📌 **Author:** Ngo Quang Duc
- 📌 **Contact:** quangducngo0811@gmail.com
# 💾 BackupTalk AI — Backup Error Assistant

**BackupTalk AI** is an intelligent assistant designed for Backup Administrators.  
It analyzes backup logs, identifies errors, and provides AI-powered troubleshooting insights — all through an interactive chat and real-time dashboard.

> 🚀 Built with **Streamlit**, **LangChain**, **FAISS**, and **PyTorch**.

---

## 🌟 Features

- 📁 Upload Backup Logs (`PDF`, `TXT`, `CSV`, `DOCX`, `XLSX`)
- 💬 Chat with your logs using a GenAI-powered assistant
- 📊 Backup Health Dashboard (Success Rate, Failures, Volume)
- 💾 Detailed error diagnostics and recommendations
- 🔐 Secure API handling using local config file (`app/config.py`)

---

## 🧠 Tech Stack

| Category | Tools Used |
|-----------|-------------|
| Frontend UI | Streamlit |
| LLM Framework | LangChain |
| Vector Store | FAISS |
| AI Engine | PyTorch |
| Data Processing | Pandas, Matplotlib |
| Deployment | Streamlit Cloud / GitHub |

---

## 🧩 Project Structure

BACKUP-ERROR-ASSISTANT/
│
├── app/
│ ├── init.py
│ ├── chat_utils.py
│ ├── config.py
│ ├── files_utils.py
│ ├── ui.py
│ ├── vectorstore_utils.py
│
├── main.py
├── requirements.txt
├── .gitignore
├── README.md


---

## ⚙️ Installation & Usage

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/<your-username>/BackupTalk-AI.git
cd BackupTalk-AI

pip install -r requirements.txt

streamlit run main.py

Configure Your API Key

You can set your EURI API key either:

Inside app/config.py

Or as an environment variable:

export EURI_API_KEY="your_api_key_here"

🧠 Example Features
💬 Chat Assistant

Ask AI questions about your backup logs, e.g.:

"What caused this connection refused error?"
"How many backup jobs failed last week?"

📊 Backup Dashboard

Success rate visualization

Failed job analytics

Backup volume tracking (GB per client)

🧑‍💻 Author

Anuj Sharma
Backup Engineer | Python & Automation Enthusiast | Learning GenAI
🌐 LinkedIn
 (optional link)

🏷️ GitHub Topics
streamlit, langchain, genai, backup, ai-assistant, pytorch, faiss, automation, data-analytics

📜 License

MIT License © 2025 Anuj Sharma
import os
import time
import re
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

from app.ui import pdf_uploader
from app.files_utils import (
    extract_text_from_pdf,
    extract_text_from_csv,
    extract_text_from_docx,
    extract_text_from_excel,
    extract_text_from_txt
)
from app.vectorstore_utils import create_faiss_index, retrive_relevant_docs
from app.chat_utils import get_chat_model, ask_chat_model
from langchain_text_splitters import RecursiveCharacterTextSplitter

# Securely load API key
EURI_API_KEY = st.secrets.get("EURI_API_KEY") or os.getenv("EURI_API_KEY")





st.set_page_config(
    page_title="BackupTalk AI ",
    page_icon="💾",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    /* --- Modern Streamlit Theme for BackupTalk AI --- */
    .main {
        background-color: #0F111A;
        color: #E5E7EB;
    }
    h1, h2, h3 {
        font-family: 'Poppins', sans-serif;
    }
    .app-header {
        text-align: center;
        padding: 2rem 0;
    }
    .app-header h1 {
        background: linear-gradient(90deg, #FF4D4D, #5E17EB);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 3rem;
        font-weight: 800;
        margin-bottom: 0.3rem;
    }
    .app-header p {
        color: #9CA3AF;
        font-size: 1.1rem;
    }
    [data-testid="stSidebar"] {
        background-color: #1A1C27;
    }
    .upload-section {
        background-color: #181A23;
        padding: 1rem;
        border-radius: 0.75rem;
        margin-bottom: 1rem;
        border: 1px dashed #5E17EB;
    }
    .stChatMessage[data-testid="user"] {
        background-color: #FF4D4D33 !important;
        color: white;
        border-radius: 0.75rem;
    }
    .stChatMessage[data-testid="assistant"] {
        background-color: #181A23 !important;
        color: #E5E7EB;
        border-radius: 0.75rem;
    }
    .stButton > button {
        background: linear-gradient(90deg, #FF4D4D, #5E17EB);
        color: white;
        border: none;
        padding: 0.6rem 1.2rem;
        border-radius: 0.5rem;
        font-weight: bold;
        transition: all 0.3s ease-in-out;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        opacity: 0.9;
    }
    .footer {
        text-align: center;
        color: #9CA3AF;
        font-size: 0.9rem;
        padding-top: 1.5rem;
        border-top: 1px solid #2E323D;
        margin-top: 2rem;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<style>
/* ===== Sticky Chat Footer ===== */
.chat-footer {
    position: fixed;
    bottom: 0;
    left: 280px;  /* adjust for sidebar width */
    right: 0;
    background-color: #0F111A;
    border-top: 1px solid #2E323D;
    padding: 0.75rem 1rem;
    z-index: 100;
}

.chat-footer input {
    width: 85%;
    padding: 0.7rem;
    border-radius: 0.5rem 0 0 0.5rem;
    border: 1px solid #FF4D4D;
    background-color: #1A1C27;
    color: #E5E7EB;
    outline: none;
}

.chat-footer button {
    width: 10%;
    background: linear-gradient(90deg, #FF4D4D, #5E17EB);
    border: none;
    border-radius: 0 0.5rem 0.5rem 0;
    color: white;
    font-weight: bold;
    cursor: pointer;
    transition: all 0.3s ease-in-out;
}

.chat-footer button:hover {
    opacity: 0.9;
    transform: translateY(-2px);
}
</style>
""", unsafe_allow_html=True)



if "messages" not in st.session_state:
    st.session_state.messages = []
if "vectorstore" not in st.session_state:
    st.session_state.vectorstore = None
if "chat_model" not in st.session_state:
    st.session_state.chat_model = None


st.markdown("""
<div class="app-header">
    <h1>💾 BackupTalk AI</h1>
    <p>Your AI Assistant for Smarter Backup Insights</p>
</div>
""", unsafe_allow_html=True)



# Sidebar for document upload
with st.sidebar:
    st.markdown("### 📁 Document Upload")
    st.markdown("Upload your documents to start chatting!")
    
    uploaded_files = pdf_uploader()
    
    if uploaded_files:
        st.success(f"📄 {len(uploaded_files)} document(s) uploaded")
        
        # Process documents
        if st.button("🚀 Process Documents", type="primary"):
            with st.spinner("Processing your documents..."):
                # Extract text from all PDFs
                all_texts = []
                for file in uploaded_files:
                    text = extract_text_from_pdf(file)
                    all_texts.append(text)
                
                # Split texts into chunks
                text_splitter = RecursiveCharacterTextSplitter(
                    chunk_size=1000,
                    chunk_overlap=200,
                    length_function=len,
                )
                
                chunks = []
                for text in all_texts:
                    chunks.extend(text_splitter.split_text(text))
                
                # Create FAISS index
                vectorstore = create_faiss_index(chunks)
                st.session_state.vectorstore = vectorstore
                
                # Initialize chat model
                chat_model = get_chat_model(EURI_API_KEY)
                st.session_state.chat_model = chat_model
                
                st.success("✅ Documents processed successfully!")
                st.balloons()

# ===============================
# 🧩 Tabs: Chat System + Dashboard
# ===============================

tab1, tab2 = st.tabs(["💬 Chat Assistant", "📊 Backup Health Dashboard"])

# -------------------------------
# 💬 TAB 1 – Chat Assistant
# -------------------------------
with tab1:
    st.markdown("""
    <div style="background-color:#1A1C27; padding: 1rem; border-radius: 0.75rem; margin-top:1rem;">
    <h3 style="color:#FF4D4D;">💬 Talk to Your Data</h3>
    <p style="color:#9CA3AF;">Ask BackupTalk AI to summarize, diagnose, or explain your backup logs.</p>
    </div>
    """, unsafe_allow_html=True)

    # Display previous messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            st.caption(message["timestamp"])

    # Chat input
    if prompt := st.chat_input("Ask anything about your backup logs..."):
        timestamp = time.strftime("%H:%M")
        st.session_state.messages.append({
            "role": "user", 
            "content": prompt, 
            "timestamp": timestamp
        })
        
        with st.chat_message("user"):
            st.markdown(prompt)
            st.caption(timestamp)
        
        # Generate AI response
        if st.session_state.vectorstore and st.session_state.chat_model:
            with st.chat_message("assistant"):
                with st.spinner("🔍 Analyzing backup logs..."):
                    relevant_docs = retrive_relevant_docs(st.session_state.vectorstore, prompt)
                    context = "\n\n".join([doc.page_content for doc in relevant_docs])
                    
                    system_prompt = f"""
                    You are BackupTalk AI, an intelligent assistant specialized in backup error analysis.
                    Based on the following logs, provide detailed insights, causes, and suggestions.
                    If data is missing, clearly mention that.

                    Backup Logs:
                    {context}

                    User Question: {prompt}

                    Answer:
                    """
                    response = ask_chat_model(st.session_state.chat_model, system_prompt)

                st.markdown(response)
                st.caption(timestamp)
                
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": response, 
                    "timestamp": timestamp
                })
        else:
            with st.chat_message("assistant"):
                st.error("⚠️ Please upload and process documents first.")
                st.caption(timestamp)

# -------------------------------
# 📊 TAB 2 – Backup Health Dashboard
# -------------------------------
with tab2:
    st.markdown("""
    <div style="background-color:#1A1C27; padding: 1rem; border-radius: 0.75rem; margin-top:1rem;">
    <h3 style="color:#FF4D4D;">📊 Backup Health Dashboard</h3>
    <p style="color:#9CA3AF;">Visual overview of backup performance, failed jobs, and backup volume.</p>
    </div>
    """, unsafe_allow_html=True)

    if st.session_state.vectorstore:
        combined_text = ""
        for file in uploaded_files:
            if file.name.endswith(".pdf"):
                combined_text += extract_text_from_pdf(file)
            elif file.name.endswith(".txt"):
                combined_text += extract_text_from_txt(file)
            elif file.name.endswith(".csv"):
                combined_text += extract_text_from_csv(file)
            elif file.name.endswith(".docx"):
                combined_text += extract_text_from_docx(file)
            elif file.name.endswith(".xlsx"):
                combined_text += extract_text_from_excel(file)

        import re, pandas as pd, matplotlib.pyplot as plt, numpy as np

        # Parse logs
        pattern_success = re.compile(r"(\w+Server\d+).*succeeded.*?(\d+)\s*GB", re.IGNORECASE)
        pattern_failed = re.compile(r"(\w+Server\d+).*failed.*?(?:error|code|reason)?.*?(\d+)?", re.IGNORECASE)

        success_entries = pattern_success.findall(combined_text)
        failed_entries = pattern_failed.findall(combined_text)

        client_names = list(set([s[0] for s in success_entries + failed_entries]))
        data = []

        for client in client_names:
            client_success = [int(s[1]) for s in success_entries if s[0] == client]
            client_failed = [f for f in failed_entries if f[0] == client]
            total_gb = sum(client_success)
            success_rate = 100 if (len(client_failed) == 0 and client_success) else max(50, 100 - (len(client_failed) * 10))
            data.append({
                "Client": client,
                "TotalSizeGB": total_gb,
                "SuccessJobs": len(client_success),
                "FailedJobs": len(client_failed),
                "SuccessRate": success_rate
            })

        df = pd.DataFrame(data)

        if not df.empty:
            avg_success = np.mean(df["SuccessRate"])
            total_failed = np.sum(df["FailedJobs"])
            total_size = np.sum(df["TotalSizeGB"])

            st.success(f"✅ Average Success Rate: **{avg_success:.1f}%**")
            st.warning(f"⚠️ Total Failed Jobs: **{total_failed}**")
            st.info(f"💾 Total Backup Volume: **{total_size:.1f} GB**")

            col1, col2 = st.columns(2)
            with col1:
                fig1, ax1 = plt.subplots()
                ax1.bar(df["Client"], df["SuccessRate"], color="#22C55E")
                ax1.set_title("Backup Success Rate (%)")
                ax1.set_ylim(0, 100)
                for i, v in enumerate(df["SuccessRate"]):
                    ax1.text(i, v + 2, f"{v:.0f}%", ha='center', fontsize=9)
                st.pyplot(fig1)

            with col2:
                fig2, ax2 = plt.subplots()
                ax2.bar(df["Client"], df["FailedJobs"], color="#FF4D4D")
                ax2.set_title("Failed Jobs per Client")
                for i, v in enumerate(df["FailedJobs"]):
                    ax2.text(i, v + 0.1, f"{v}", ha='center', fontsize=9)
                st.pyplot(fig2)

            st.markdown("### 💽 Backup Volume by Client (GB)")
            fig3, ax3 = plt.subplots()
            ax3.plot(df["Client"], df["TotalSizeGB"], marker='o', color="#5E17EB")
            ax3.set_ylabel("Backup Size (GB)")
            ax3.set_title("Backup Volume by Client")
            st.pyplot(fig3)
        else:
            st.warning("⚠️ No valid backup log entries found in uploaded documents.")
    else:
        st.info("ℹ️ Please upload and process your backup log files to generate a live dashboard.")


# Footer
st.markdown("""
<div class="footer">
    💾 <strong>BackupTalk AI</strong> — Your AI Assistant for Smarter Backup Insights<br>
    Powered by <strong>Euri AI</strong> ⚙ LangChain | Designed for Backup Teams 🧠
</div>
""", unsafe_allow_html=True)






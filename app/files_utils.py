#from pypdf import pdf, PdfReader
from pypdf import PdfReader, PdfWriter
from typing import List, Optional
from io import BytesIO
import pandas as pd
from docx import Document

'''def extract_text_from_pdf(file):
    reader = PdfReader(file)
    text = ' '
    for page in reader.pages:
        text = text + page.extract_text() or ''
    return text '''

# --- PDF ---
def extract_text_from_pdf(file) -> str:
    reader = PdfReader(file)
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    return text.strip()

# --- CSV ---
def extract_text_from_csv(file) -> str:
    df = pd.read_csv(file)
    return df.to_string(index=False)

# --- Excel ---
def extract_text_from_excel(file) -> str:
    df = pd.read_excel(file)
    return df.to_string(index=False)

# --- TXT ---
def extract_text_from_txt(file) -> str:
    return file.read().decode("utf-8")

# --- Word (DOCX) ---
def extract_text_from_docx(file) -> str:
    doc = Document(file)
    return "\n".join([para.text for para in doc.paragraphs if para.text.strip()])

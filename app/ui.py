import streamlit as st

def pdf_uploader():
    return st.file_uploader("Upload a file", type=["pdf", "csv", "xlsx", "xls", "txt", "docx"],accept_multiple_files=True,
                            help="Upload one or more files to process.")

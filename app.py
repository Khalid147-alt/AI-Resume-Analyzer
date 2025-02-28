import streamlit as st
import fitz 
import docx
import spacy
import matplotlib.pyplot as plt

# Load NLP model
model_name = "en_core_web_sm"
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    st.error("The 'en_core_web_sm' model is not installed. Please install it using the command: python -m spacy download en_core_web_sm")

st.title("🧾 AI Powered Resume Analyzer")

# File uploader
uploaded_file = st.file_uploader("Upload your resume (PDF or DOCX)", type=["pdf","docx"])

def extract_text_from_pdf(pdf_file):
    """Extracts text from a PDF file."""
    doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text()
    return text

def extract_text_from_docx(docx_file):
    """Extracts text from a DOCX file."""
    doc = docx.Document(docx_file)
    text = "\n".join([para.text for para in doc.paragraphs])
    return text

resume_text = ""  # Initialize to avoid errors if file is not uploaded

if uploaded_file:
    file_type = uploaded_file.name.split(".")[-1]
    if file_type == "pdf":
        resume_text = extract_text_from_pdf(uploaded_file)
    elif file_type == "docx":
        resume_text = extract_text_from_docx(uploaded_file)
    else:
        st.error("Unsupported file format. Please upload a PDF or DOCX file.")

    st.subheader("Extracted Resume Text: ")
    st.write(resume_text[:1000])  # Show only first 1000 characters

st.subheader("📌 Job Description")
job_description = st.text_area("Paste the Job Description Here")

# Process resume text with NLP
def extract_keywords(text):
    """Extracts important keywords from text using NLP"""
    doc = nlp(text)
    keywords = [token.text.lower() for token in doc if token.pos_ in ["NOUN", "PROPN"]]
    return set(keywords)

match_score = None  # Initialize match_score before using it

if job_description and resume_text:
    resume_keywords = extract_keywords(resume_text)
    job_keywords = extract_keywords(job_description)

    st.subheader("🔍 Resume vs Job Description Keywords")
    if resume_keywords:
        st.write("📄 Resume Keywords:", ", ".join(resume_keywords))
    else:
        st.write("📄 No keywords found in the resume.")

    if job_keywords:
        st.write("💼 Job Description Keywords:", ", ".join(job_keywords))
    else:
        st.write("💼 No keywords found in the job description.")

    # Calculate match score 
    if job_keywords:  # Avoid division by zero
        match_score = len(resume_keywords & job_keywords) / len(job_keywords) * 100
        match_score = round(match_score, 2)

        st.subheader("🎯 Job Match Score")
        st.metric(label="Match Percentage", value=f"{match_score}%")

# Ensure match_score exists before plotting
if match_score is not None:
    fig, ax = plt.subplots()
    ax.bar(["Resume Match"], [match_score], color="green" if match_score > 50 else "red")
    ax.set_ylim([0, 100])
    ax.set_ylabel("Match Percentage")
    st.pyplot(fig)

import streamlit as st
import google.generativeai as genai
import os
import docx2txt
import PyPDF2 as pdf
from dotenv import load_dotenv
import spacy
import json

# Load environment variables
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Load NLP model
nlp = spacy.load("en_core_web_sm")

# Streamlit Page Config
st.set_page_config(page_title="ATS Resume Tracker", page_icon="📄", layout="centered")

# Custom Styling
st.markdown(
    """
    <style>
    body { background-color: #f8f9fa; }
    .main { background: white; border-radius: 10px; padding: 20px; }
    h1 { color: #ff6600; text-align: center; }
    .stButton>button { background-color: #ff6600; color: white; }
    .section-header { font-size: 20px; font-weight: bold; color: #ff6600; margin-top: 20px; }
    .highlight { font-size: 18px; font-weight: bold; color: #007bff; }
    </style>
    """,
    unsafe_allow_html=True,
)

# App Header
st.title("📄 ATS Resume Tracker")
st.write("Enhance your resume for better ATS compatibility.")

# Job Description Input
job_description = st.text_area("📌 Paste the Job Description", height=200)

# Resume Upload
uploaded_file = st.file_uploader("📂 Upload Your Resume (PDF/DOCX)", type=["pdf", "docx"])

def extract_text(uploaded_file):
    if uploaded_file.type == "application/pdf":
        reader = pdf.PdfReader(uploaded_file)
        return "\n".join([page.extract_text() for page in reader.pages if page.extract_text()])
    elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        return docx2txt.process(uploaded_file)

def analyze_resume(resume_text, job_description):
    prompt = f"""
    Analyze the resume against the job description.
    Resume: {resume_text}
    Job Description: {job_description}
    Output JSON: {{"Match":"%","Suitability":"","Summary":"","Experience":"","Experience Details":"","Projects":"","Project Details":"","Certifications":"","Certification Details":"","Achievements":"","Achievement Details":"","Skills":"","Missing Keywords":""}}
    """
    model = genai.GenerativeModel("gemini-pro")
    response = model.generate_content(prompt)
    return json.loads(response.text)

# Submit Button
if st.button("🔍 Evaluate Resume"):
    if uploaded_file and job_description:
        resume_text = extract_text(uploaded_file)
        if resume_text:
            response = analyze_resume(resume_text, job_description)
            
            st.subheader("✅ ATS Evaluation Result:")
            st.write(f"**Job Match:** {response['Match']}")
            st.write(f"**Suitability:** {response['Suitability']}")
            
            st.markdown("<div class='section-header'>📌 Summary</div>", unsafe_allow_html=True)
            st.write(response['Summary'])
            
            st.markdown("<div class='section-header'>📌 Experience</div>", unsafe_allow_html=True)
            st.write(response['Experience'])
            st.write(response['Experience Details'])
            
            st.markdown("<div class='section-header'>📌 Projects</div>", unsafe_allow_html=True)
            st.write(response['Projects'])
            st.write(response['Project Details'])
            
            st.markdown("<div class='section-header'>📌 Certifications</div>", unsafe_allow_html=True)
            st.write(response['Certifications'])
            st.write(response['Certification Details'])
            
            st.markdown("<div class='section-header'>📌 Achievements</div>", unsafe_allow_html=True)
            st.write(response['Achievements'])
            st.write(response['Achievement Details'])
            
            st.markdown("<div class='section-header'>📌 Skills</div>", unsafe_allow_html=True)
            st.write(response['Skills'])
            
            st.markdown("<div class='section-header'>📌 Missing Keywords</div>", unsafe_allow_html=True)
            st.write(response['Missing Keywords'])
        else:
            st.error("Could not extract text from the uploaded file. Try another format.")
    else:
        st.warning("Please upload a resume and provide a job description.")

# Footer
st.markdown(
    """
    <hr>
    <p style='text-align: right; color: grey;'>
        Made by <b>Teja Katkam</b> | Email: <a href='mailto:227r1a6627@cmrtc.ac.in'>227r1a6627@cmrtc.ac.in</a>
    </p>
    """,
    unsafe_allow_html=True,
)

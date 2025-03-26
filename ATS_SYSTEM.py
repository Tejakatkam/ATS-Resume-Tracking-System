import streamlit as st
import google.generativeai as genai
import os
import docx2txt
import PyPDF2 as pdf
from dotenv import load_dotenv
import spacy

# Load environment variables from a .env file
load_dotenv()

# Configure the generative AI model with the Google API key
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Set up the model configuration for text generation
generation_config = {
    "temperature": 0.4,
    "top_p": 1,
    "top_k": 32,
    "max_output_tokens": 4096,
}

# Define safety settings for content generation
safety_settings = [
    {"category": f"HARM_CATEGORY_{category}", "threshold": "BLOCK_MEDIUM_AND_ABOVE"}
    for category in ["HARASSMENT", "HATE_SPEECH", "SEXUALLY_EXPLICIT", "DANGEROUS_CONTENT"]
]

# Load NLP model
nlp = spacy.load("en_core_web_sm")

def list_available_models():
    try:
        models = genai.list_models()
        return [model.name for model in models if "generateContent" in model.supported_generation_methods]
    except Exception as e:
        return f"Error fetching models: {str(e)}"

def generate_response_from_gemini(input_text):
    llm = genai.GenerativeModel(
        model_name="gemini-1.5-pro",  # Verify this with list_available_models()
        generation_config=generation_config,
        safety_settings=safety_settings,
    )
    try:
        output = llm.generate_content(input_text)
        return output.text
    except Exception as e:
        available_models = list_available_models()
        return f"Error generating response: {str(e)}. Available models: {available_models}"

def extract_text_from_pdf_file(uploaded_file):
    pdf_reader = pdf.PdfReader(uploaded_file)
    text_content = ""
    for page in pdf_reader.pages:
        text_content += str(page.extract_text())
    return text_content

def extract_text_from_docx_file(uploaded_file):
    return docx2txt.process(uploaded_file)

def extract_skills_and_experience(text):
    doc = nlp(text)
    skills = []
    experiences = []

    for ent in doc.ents:
        if ent.label_ in ["SKILL", "EXPERIENCE"]:
            if ent.label_ == "SKILL":
                skills.append(ent.text)
            elif ent.label_ == "EXPERIENCE":
                experiences.append(ent.text)

    return skills, experiences

# Prompt Template
input_prompt_template = """
As an experienced Applicant Tracking System (ATS) analyst,
with profound knowledge in technology, software engineering, data science, 
and big data engineering, your role involves evaluating resumes against job descriptions.
Recognizing the competitive job market, provide top-notch assistance for resume improvement.
Your goal is to analyze the resume against the given job description, 
assign a percentage match based on key criteria, and pinpoint missing keywords accurately.
resume:{text}
description:{job_description}
I want the response in one single string having the structure
{{"Job Description Match":"%","Missing Keywords":"","Candidate Summary":"","Experience":""}}
"""

# Function to format the response as a styled paragraph
def format_response_as_paragraph(response_text):
    try:
        # Extract values from the response string
        match = response_text.split('"Job Description Match":"')[1].split('"')[0]
        missing_keywords = response_text.split('"Missing Keywords":"')[1].split('"')[0]
        summary = response_text.split('"Candidate Summary":"')[1].split('"')[0]
        experience = response_text.split('"Experience":"')[1].split('"')[0]
        
        # Format into a paragraph with HTML/CSS styling
        paragraph = (
            f'<p style="font-size: 25px; font-weight: bold; color: #2c3e50;">The resume matches the job description by {match}.</p>'
            f'<p style="font-size: 18px; font-weight: bold; color: #34495e;">Keywords missing from the resume include:</p>'
            f'<p style="font-size: 14px; color: #7f8c8d;">{missing_keywords}.</p>'
            f'<p style="font-size: 18px; font-weight: bold; color: #34495e;">Here’s a summary of the candidate:</p>'
            f'<p style="font-size: 14px; color: #7f8c8d;">{summary}.</p>'
            f'<p style="font-size: 18px; font-weight: bold; color: #34495e;">The candidate’s relevant experience is:</p>'
            f'<p style="font-size: 14px; color: #7f8c8d;">{experience}.</p>'
        )
        return paragraph
    except (IndexError, ValueError):
        return '<p style="color: red;">Unable to format response. Please check the model output.</p>'

# Inject modern CSS styling with teal background
st.markdown(
    """
    <style>
    #MainMenu {visibility: hidden;}
        # footer {visibility: hidden;}
        header {visibility: hidden;}

    .stApp {
        background: linear-gradient(135deg, #34495e 0%, #2c3e50 100%);
        color: #2c3e50;
        font-family: 'Poppins', sans-serif;
    }
    /* Global styles */
    body {
        background: linear-gradient(135deg, #26a69a 0%, #4db6ac 100%); /* Teal gradient */
        color: #2c3e50;
        font-family: 'Poppins', sans-serif;
    }

    /* Title styling */
    h1 {
        color: #e67e22 !important;
        text-align: center;
        font-size: 36px !important;
        font-weight: 700 !important;
        margin-bottom: 20px;
        text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.1);
    }

    label {
        color: white !important;  /* Change text color to white */
    }

    /* Subheader styling */
    h2 {
        color: #34495e;
        font-size: 24px;
        font-weight: 600;
        margin-top: 30px;
        margin-bottom: 20px;
        border-bottom: 2px solid #e67e22;
        padding-bottom: 5px;
        display: inline-block;
    }
    /* Text area styling */
    textarea {
    color: #ffffff !important;  /* White text color */
    background-color: #333333 !important; /* Dark background for contrast */
    border-radius: 10px !important;
    border: 1px solid #dcdcdc !important;
    box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1) !important;
    padding: 10px !important;
    font-size: 16px !important;
    transition: all 0.3s ease !important;
}

textarea:focus {
    border-color: #ffffff !important;
    box-shadow: 0 0 8px rgba(230, 126, 34, 0.3) !important;
}


    /* File uploader styling */
    .stFileUploader {
        border: 2px dashed #dcdcdc;
        border-radius: 10px;
        padding: 20px;
        background-color: #ffffff;
        box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
        transition: all 0.3s ease;
    }
    .stFileUploader:hover {
        border-color: #e67e22;
        box-shadow: 0 0 10px rgba(230, 126, 34, 0.2);
    }

    /* Button styling */
    .stButton>button {
        background-color: #e67e22;
        color: white;
        border: none;
        border-radius: 25px;
        padding: 10px 20px;
        font-size: 16px;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 2px 5px rgba(0, 0, 0, 0.2);
    }
    
    .stButton>button:hover {
        background-color: #d35400;
        transform: translateY(-2px);
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.3);
    }

    /* ATS Evaluation Result card */
    .result-card {
        background-color: #ffffff;
        border-radius: 15px;
        padding: 20px;
        margin-top: 20px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
        transition: all 0.3s ease;
    }
    .result-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.15);
    }

    /* Footer styling */
    .footer {
        position: fixed;
        bottom: 0;
        right: 0;
        background: linear-gradient(135deg, #34495e 0%, #2c3e50 100%);
        text-align: left;
        padding: 15px 20px;
        font-size: 14px;
        color: #ecf0f1;
    }
    .footer a {
        color: #e67e22;
        text-decoration: none;
        transition: color 0.3s ease;
    }
    .footer a:hover {
        color: #f39c12;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Streamlit app
st.title("Intelligent ATS - Enhance Your Resume ATS")
job_description = st.text_area("Paste the Job Description", height=300)
uploaded_file = st.file_uploader("Upload Your Resume", type=["pdf", "docx"], help="Please upload a PDF or DOCX file")

submit_button = st.button("Submit")

if submit_button:
    if uploaded_file is not None:
        if uploaded_file.type == "application/pdf":
            resume_text = extract_text_from_pdf_file(uploaded_file)
        elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            resume_text = extract_text_from_docx_file(uploaded_file)

        # Extract skills and experience
        skills, experiences = extract_skills_and_experience(resume_text)
        experiences_str = ", ".join(experiences) if experiences else "No specific experiences identified."

        # Generate response from the Gemini model
        response_text = generate_response_from_gemini(input_prompt_template.format(text=resume_text, job_description=job_description))

        # Format the response as a styled paragraph
        formatted_response = format_response_as_paragraph(response_text)

        # Extract Job Description Match percentage for conditional logic
        try:
            match_percentage_str = response_text.split('"Job Description Match":"')[1].split('"')[0]
            match_percentage = float(match_percentage_str.rstrip('%'))
        except (IndexError, ValueError):
            st.error("Error parsing the response. Please check the model output.")
            match_percentage = 0

        st.markdown('<h2 style="color: white;">ATS Evaluation Result:</h2>', unsafe_allow_html=True)
        # Wrap the result in a card-like container
        st.markdown(
            f'<div class="result-card">{formatted_response}</div>',
            unsafe_allow_html=True
        )

        # Display message based on Job Description Match percentage
        if match_percentage >= 60:
            st.markdown(
                '<p style="font-size: 25px; font-weight: bold; color: green;">Candidate is a good match for the position.</p>',
                unsafe_allow_html=True
            )
            if experiences:
                st.markdown(
                    f'<p style="font-size: 14px; color: #7f8c8d;">Highlighted Experience: {experiences_str}</p>',
                    unsafe_allow_html=True
                )
        else:
            st.markdown(
                '<p style="font-size: 25px; font-weight: bold; color: red;">Candidate is not a match.</p>',
                unsafe_allow_html=True
            )

# Footer with your name and email
footer = """
    <div class="footer">
        <p>Made by - <b style="font-size:20px;">ATS</b>
        <br>Email: <a href="mailto:227r1a6640@cmrtc.ac.in">Abhiram-227r1a6640@cmrtc.ac.in</a>
        <br>Email: <a href="mailto:227r1a6627@cmrtc.ac.in">Teja-227r1a6627@cmrtc.ac.in</a>
        <br>Email: <a href="mailto:227r1a6655@cmrtc.ac.in">Shria-227r1a6655@cmrtc.ac.in</a></p>
    </div>
"""

st.markdown(footer, unsafe_allow_html=True)
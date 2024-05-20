import streamlit as st
from openai import OpenAI,OpenAIError
import fitz  # PyMuPDF
import os
from dotenv import load_dotenv
from pathlib import Path


# Load environment variables
load_dotenv()

# Set your OpenAI API key
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Directory to save uploaded PDFs
UPLOAD_DIR = Path("./uploaded-docs")
UPLOAD_DIR.mkdir(exist_ok=True)


# Function to save uploaded file
def save_uploaded_file(uploaded_file):
    save_path = UPLOAD_DIR / uploaded_file.name
    with open(save_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return save_path

# Function to extract text from PDF
def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text()
    return text


# Function to query OpenAI GPT-4
def query_openai(prompt):
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content.strip()
    except OpenAIError as e:
        if "rate limit" in str(e).lower():
            st.error("You have exceeded the rate limit for GPT-3.5 turbo. Please try again later.")
        else:
            st.error(f"An error occurred with OpenAI: {e}")
        return None

def run_docquery_app():
  try:
    # Upload Document
    # Streamlit App
    st.title("Document Query and Public Dataset Search")
    uploaded_file = st.file_uploader("Upload a PDF document", type=["pdf"])

    if uploaded_file is not None:
        pdf_path = save_uploaded_file(uploaded_file)
        document_text = extract_text_from_pdf(pdf_path)
        st.write("Extracted Text from Document:")
        st.write(document_text)

        question = st.text_input("Ask a question about the document:")

        if st.button("Get Answer"):
            if question:
                # Crafting a clear and precise prompt
                prompt = f"""
                Document Text: {document_text}

                Question: {question}

                If the answer is found in the document, respond with: "Answer is from the document: [Your Answer]"
                If the answer is not found in the document, respond with: "Answer is not from the document."
                Answer:
                """
                answer = query_openai(prompt)

                if "Answer is from the document:" in answer:
                    st.write("Answer from Document:")
                    st.write(answer.replace("Answer is from the document:", "").strip())
                elif "Answer is not from the document." in answer:
                    st.write("Answer not found in the document. Searching in public datasets...")
                    public_answer = query_openai(question)
                    st.write("Answer from Public Datasets:")
                    st.write(public_answer)
                else:
                    st.write("Answer:")
                    st.write(answer)
            else:
                st.write("Please ask a question.")
  except Exception as e:
    st.error(f"An error occurred: {e}")
run_docquery_app()

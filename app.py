import streamlit as st
import os
import fitz  # PyMuPDF
import tempfile
import requests
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS

# --- Page config ---
st.set_page_config(page_title="HR Copilot", layout="wide")
st.title(" HR Recruitment Copilot")

# --- Secrets ---
HF_API_KEY = st.secrets.get("HUGGINGFACE_API_KEY", "")
HF_MODEL = "mistralai/Mixtral-8x7B-Instruct-v0.1"
HEADERS = {
    "Authorization": f"Bearer {HF_API_KEY}",
    "Content-Type": "application/json"
}

# --- Functions ---
def extract_text_from_pdf(pdf_file):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(pdf_file.read())
        tmp_path = tmp.name

    text = ""
    with fitz.open(tmp_path) as doc:
        for page in doc:
            text += page.get_text()
    os.remove(tmp_path)
    return text

def get_matching_keywords(jd_text, resume_text):
    jd_tokens = set(jd_text.lower().split()) - ENGLISH_STOP_WORDS
    resume_tokens = set(resume_text.lower().split()) - ENGLISH_STOP_WORDS
    return jd_tokens.intersection(resume_tokens), jd_tokens

def score_resume(jd_tokens, matched_keywords):
    if not jd_tokens:
        return 0
    return round((len(matched_keywords) / len(jd_tokens)) * 100, 2)

def summarize_match(jd, resume):
    prompt = f"""
You are an HR assistant. Given the job description and a candidate's resume, explain how well the resume matches the JD in 2-3 lines.

Job Description:
{jd}

Resume:
{resume}

Summary:"""

    response = requests.post(
        f"https://api-inference.huggingface.co/models/{HF_MODEL}",
        headers=HEADERS,
        json={"inputs": prompt}
    )

    if response.status_code == 200:
        result = response.json()
        if isinstance(result, list) and len(result) > 0:
            return result[0]["generated_text"].split("Summary:")[-1].strip()
        return "No summary available."
    else:
        return f" Error: {response.json().get('error', 'Unknown')}"

# --- UI ---
jd_text = st.text_area("  Paste the Job Description (JD):", height=200)
uploaded_files = st.file_uploader(" Upload Resumes (PDFs):", type="pdf", accept_multiple_files=True)
score_threshold = st.slider(" Score Threshold for Shortlisting", min_value=0, max_value=100, value=70)

# --- Analysis Button ---
if st.button(" Run Analysis"):
    if not HF_API_KEY:
        st.error("Please set your Hugging Face API Key in `.streamlit/secrets.toml`")
    elif not jd_text.strip():
        st.warning("Please enter a job description.")
    elif not uploaded_files:
        st.warning("Please upload at least one resume.")
    else:
        st.success(" Analysis started...")
        results = []

        for file in uploaded_files:
            resume_text = extract_text_from_pdf(file)
            matched_keywords, jd_tokens = get_matching_keywords(jd_text, resume_text)
            score = score_resume(jd_tokens, matched_keywords)
            summary = summarize_match(jd_text, resume_text)

            results.append({
                "name": file.name,
                "score": score,
                "summary": summary,
                "keywords": sorted(matched_keywords)
            })

        # Sort by score descending
        results.sort(key=lambda x: x["score"], reverse=True)

        # --- Shortlisted ---
        st.subheader(" Shortlisted Candidates")
        shortlisted = []
        for res in results:
            if res["score"] >= score_threshold:
                shortlisted.append(res)
                st.markdown(f"###  {res['name']}")
                st.markdown(f"**Score:** {res['score']}/100")
                st.markdown("**Matching Keywords:**")
                st.write(", ".join(res['keywords']) if res['keywords'] else "None")
                st.markdown("**AI Summary:**")
                st.info(res['summary'])

        # --- CSV Export ---
        if shortlisted:
            df_shortlisted = pd.DataFrame([
                {
                    "File Name": res["name"],
                    "Score": res["score"],
                    "Matching Keywords": ", ".join(res["keywords"]),
                    "AI Summary": res["summary"]
                } for res in shortlisted
            ])
            st.download_button(
                label="📥 Download Shortlisted as CSV",
                data=df_shortlisted.to_csv(index=False).encode('utf-8'),
                file_name='shortlisted_candidates.csv',
                mime='text/csv'
            )

        # --- Eliminated ---
        st.divider()
        st.subheader("❌ Eliminated Candidates")
        for res in results:
            if res["score"] < score_threshold:
                st.markdown(f"### ❌ {res['name']}")
                st.markdown(f"**Score:** {res['score']}/100")
                st.markdown("**Matching Keywords:**")
                st.write(", ".join(res['keywords']) if res['keywords'] else "None")
                st.markdown("**AI Summary:**")
                st.error(res['summary'])

        # --- Chart ---
        st.divider()
        st.subheader(" Score Distribution")
        candidate_names = [res["name"] for res in results]
        candidate_scores = [res["score"] for res in results]

        fig, ax = plt.subplots(figsize=(10, 4))
        colors = ['green' if s >= score_threshold else 'red' for s in candidate_scores]
        ax.barh(candidate_names, candidate_scores, color=colors)
        ax.set_xlabel("Score")
        ax.set_title("Candidate Score Overview")
        st.pyplot(fig)

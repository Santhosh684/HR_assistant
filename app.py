import streamlit as st
import os
import fitz  # PyMuPDF
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.feature_extraction.text import TfidfVectorizer
import re

# --------------------------------------
# Utility Functions
# --------------------------------------

def clean_text(text):
    return re.sub(r'[^a-zA-Z\s]', '', text.lower())

def extract_text_from_pdf(file):
    doc = fitz.open(stream=file.read(), filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text()
    return clean_text(text)

def extract_top_keywords(jd_text, top_n=20):
    jd_clean = clean_text(jd_text)
    vectorizer = TfidfVectorizer(stop_words='english', max_features=top_n)
    X = vectorizer.fit_transform([jd_clean])
    return vectorizer.get_feature_names_out()

def score_resume_from_keywords(jd_text, resume_text, top_n=20):
    jd_keywords = extract_top_keywords(jd_text, top_n)
    matches = [kw for kw in jd_keywords if kw in resume_text]
    score = int((len(matches) / top_n) * 100)
    summary = f"Matched {len(matches)}/{top_n} keywords"
    return score, summary, matches

# --------------------------------------
# Streamlit UI
# --------------------------------------

st.set_page_config(page_title="HR Recruitment Copilot", layout="wide")
st.title(" HR Recruitment Copilot")
st.markdown("Upload resumes, provide a Job Description, and let AI rank candidates.")

jd_input = st.text_area(" Paste the Job Description here")

uploaded_files = st.file_uploader("📎 Upload Candidate Resumes (PDF only)", type=["pdf"], accept_multiple_files=True)

score_threshold = st.slider("Minimum Score Threshold for Shortlisting", 0, 100, 60)

if st.button("Run Analysis") and jd_input and uploaded_files:
    results = []

    with st.spinner("Analyzing resumes..."):
        for file in uploaded_files:
            resume_text = extract_text_from_pdf(file)
            score, summary, keywords = score_resume_from_keywords(jd_input, resume_text)
            results.append({
                "Name": file.name,
                "Score": score,
                "Summary": summary,
                "Matched Keywords": ", ".join(keywords)
            })

    df = pd.DataFrame(results)
    df_sorted = df.sort_values(by="Score", ascending=False)

    st.subheader(" Candidate Ranking")
    st.dataframe(df_sorted.reset_index(drop=True))

    # Bar Chart
    plt.figure(figsize=(5, 3))
    
    # st.subheader(" Score Visualization")
    # fig, ax = plt.subplots(figsize=(3, 4))  # 3:4 ratio (width:height)
    # ax.barh(df_sorted["Name"], df_sorted["Score"], color='green')
    # ax.invert_yaxis()
    # st.pyplot(fig)

    # Shortlist based on threshold
    shortlisted = df_sorted[df_sorted["Score"] >= score_threshold]
    eliminated = df_sorted[df_sorted["Score"] < score_threshold]

    st.success(f"{len(shortlisted)} candidates shortlisted")
    st.error(f"{len(eliminated)} candidates eliminated")

    with st.expander("View Shortlisted Candidates"):
        st.dataframe(shortlisted.reset_index(drop=True))

    with st.expander("View Eliminated Candidates"):
        st.dataframe(eliminated.reset_index(drop=True))

    # Export to CSV
    csv = shortlisted.to_csv(index=False).encode("utf-8")
    st.download_button(
        label=" Download Shortlisted CSV",
        data=csv,
        file_name="shortlisted_candidates.csv",
        mime="text/csv"
    )

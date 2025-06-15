HR Recruitment Copilot

An AI-powered tool that assists HR teams in shortlisting candidates based on how well their resumes match a given Job Description (JD).

Built using Python, Streamlit, and free open-source LLMs (via Hugging Face), this copilot extracts text from resumes, compares it against a JD, scores applicants, and shortlists or eliminates them based on a score threshold.

---

## Features

*  Upload multiple resumes (PDF format)
*  AI-powered skill & experience matching with Job Description
*  Resume scoring out of 100
*  Justification summary per applicant
*  Rank applicants by score (descending)
*  Eliminate low-scoring resumes based on threshold
*  View shortlisted vs eliminated candidates side-by-side

---

## Tech Stack

* Python 3.8+
* Streamlit (for frontend)
* PyMuPDF  for PDF text extraction
* Hugging Face Inference API** (e.g. `Mixtral`, `mistral-7b`, etc.)

---

## Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/hr-recruitment-copilot.git
cd hr-recruitment-copilot
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Set Your Hugging Face API Key

In `app.py`, replace:

```python
HEADERS = {"Authorization": "Bearer YOUR_HUGGINGFACE_API_KEY"}
```

with your actual key from [https://huggingface.co/settings/tokens](https://huggingface.co/settings/tokens).

Alternatively, use environment variables or `st.secrets` for secure deployments.

### 4. Run the App

```bash
streamlit run app.py
```

---

##  Folder Structure

```
hr-recruitment-copilot/
├── app.py                 # Main Streamlit app
├── resume_parser.py       # (Optional) Resume parsing utils
├── scoring_engine.py      # (Optional) JD comparison logic
├── requirements.txt       # Required Python packages
├── resumes/               # Folder to store uploaded PDFs
├── shortlisted/           # Folder for shortlisted resumes or output CSVs
```

---

##  Example Use Case

1. Paste a job description (JD)
2. Upload multiple candidate resumes (PDF)
3. Set a minimum score threshold (e.g., 70)
4. Click "Run Analysis"
5. View shortlisted vs eliminated candidates with AI-generated insights

---

##  Deployment (Optional)

* Easily deploy to [Streamlit Cloud](https://streamlit.io/cloud)
* Use GitHub repo and set secrets like:

  ```
  HUGGINGFACE_API_KEY = your_key_here
  ```

---

## Future Enhancements

* Export shortlisted candidates to CSV
* Candidate metadata extraction (email, LinkedIn, etc.)
* Visual insights (charts, graphs)
* Interactive Q\&A Copilot chatbot

---

##  Credits

* LLM: [Mistral](https://huggingface.co/mistralai/Mixtral-8x7B-Instruct-v0.1)
* Built with ❤️ using Python + Streamlit

---

## 📄 License

This project is licensed under the MIT License.

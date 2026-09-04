# 📄 CV ↔ Job Description Matcher

An AI-powered web app that compares a CV against a job description and returns:

- A **match score** (0–100%)
- **Matched skills** — requirements from the job description already present in the CV
- **Missing skills** — requirements the CV doesn't cover
- **Actionable suggestions** to tailor the CV for that specific role

Built as a portfolio project to demonstrate practical use of LLMs for a real-world problem: helping job seekers tailor their applications faster.

## Demo

*(Add a screenshot or GIF of the app here once you've run it — recruiters skim, so this matters!)*

## Tech Stack

- **Python**
- **Streamlit** — web UI
- **Anthropic Claude API** — CV/JD comparison and analysis
- **pypdf** — PDF text extraction

## How It Works

1. User uploads their CV (PDF) or pastes CV text, and pastes a job description.
2. The app extracts text from the PDF if needed.
3. A structured prompt sends both texts to Claude, asking for a JSON response with a match score, matched/missing skills, and improvement suggestions.
4. The app parses the JSON and renders it as a clean, readable report.

## Running Locally

### 1. Clone the repo
```bash
git clone <your-repo-url>
cd cv-matcher
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Get an Anthropic API key
Sign up at [console.anthropic.com](https://console.anthropic.com) and create an API key.

### 4. Run the app
```bash
streamlit run app.py
```

Paste your API key into the sidebar when the app opens in your browser, then upload a CV and job description to try it out.

## Notes

- No data is stored — the CV and API key only exist for the current browser session.
- The API key can also be set as an environment variable `ANTHROPIC_API_KEY` instead of typing it into the sidebar each time.

## Possible Future Improvements

- Support DOCX CV uploads
- Save/download the analysis report as a PDF
- Batch-compare one CV against multiple job descriptions

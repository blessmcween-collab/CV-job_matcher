"""
CV vs Job Description Matcher
------------------------------
A Streamlit app that compares a CV against a job description using the
Anthropic Claude API, and returns a match score, matched skills, missing
skills, and concrete suggestions to improve the CV.

Run with:  streamlit run app.py
"""

import json
import os

import anthropic
import streamlit as st
from pypdf import PdfReader

# ---------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------
st.set_page_config(
    page_title="CV Matcher",
    page_icon="📄",
    layout="wide",
)

# ---------------------------------------------------------------------
# Simple warm-toned styling
# ---------------------------------------------------------------------
st.markdown(
    """
    <style>
    .stApp {
        background-color: #FFF8F0;
    }
    h1, h2, h3 {
        color: #B5451B;
    }
    .stButton>button {
        background-color: #E8734A;
        color: white;
        border-radius: 8px;
        padding: 0.5em 1.5em;
        border: none;
        font-weight: 600;
    }
    .stButton>button:hover {
        background-color: #C85A32;
        color: white;
    }
    .score-box {
        background-color: #FFEEDF;
        border-radius: 12px;
        padding: 1.5em;
        text-align: center;
        border: 2px solid #E8734A;
    }
    .score-number {
        font-size: 3em;
        font-weight: 800;
        color: #B5451B;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------
def extract_text_from_pdf(uploaded_file) -> str:
    """Extract raw text from an uploaded PDF file."""
    reader = PdfReader(uploaded_file)
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    return text.strip()


def get_client() -> anthropic.Anthropic:
    """Create an Anthropic client using the API key from env var or sidebar input."""
    api_key = st.session_state.get("api_key") or os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        st.error("Please add your Anthropic API key in the sidebar to continue.")
        st.stop()
    return anthropic.Anthropic(api_key=api_key)


MATCH_PROMPT = """You are an expert technical recruiter and career coach.
Compare the CV below against the job description below.

Respond ONLY with valid JSON (no markdown fences, no preamble) in exactly
this shape:

{{
  "match_score": <integer 0-100>,
  "matched_skills": ["skill or requirement from the JD that IS present in the CV", ...],
  "missing_skills": ["skill or requirement from the JD that is MISSING from the CV", ...],
  "suggestions": ["concrete, specific suggestion to improve the CV for this job", ...]
}}

Rules:
- match_score reflects overall fit for this specific role, not general CV quality.
- List 3-8 items each for matched_skills and missing_skills, most important first.
- Give exactly 2-3 suggestions, each concrete and actionable (not generic advice).

CV:
\"\"\"
{cv_text}
\"\"\"

JOB DESCRIPTION:
\"\"\"
{jd_text}
\"\"\"
"""


def analyze(cv_text: str, jd_text: str) -> dict:
    client = get_client()
    message = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=1500,
        messages=[
            {
                "role": "user",
                "content": MATCH_PROMPT.format(cv_text=cv_text, jd_text=jd_text),
            }
        ],
    )
    raw = message.content[0].text.strip()
    # Defensive cleanup in case the model wraps the JSON in fences anyway
    if raw.startswith("```"):
        raw = raw.strip("`")
        raw = raw.replace("json\n", "", 1)
    return json.loads(raw)


# ---------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------
with st.sidebar:
    st.header("⚙️ Settings")
    key_input = st.text_input(
        "Anthropic API key",
        type="password",
        help="Get a key at console.anthropic.com. It is only kept for this session.",
    )
    if key_input:
        st.session_state["api_key"] = key_input
    st.markdown("---")
    st.markdown(
        "Built with **Streamlit** + **Claude API**.\n\n"
        "Your CV and API key are never stored — everything runs "
        "only for the current session."
    )

# ---------------------------------------------------------------------
# Main layout
# ---------------------------------------------------------------------
st.title("📄 CV ↔ Job Description Matcher")
st.write(
    "Upload your CV and paste a job description to see how well they match, "
    "what's missing, and how to improve your CV for this specific role."
)

col1, col2 = st.columns(2)

with col1:
    st.subheader("Your CV")
    cv_file = st.file_uploader("Upload CV (PDF)", type=["pdf"])
    cv_text_manual = st.text_area(
        "...or paste your CV text instead", height=200, placeholder="Paste CV text here"
    )

with col2:
    st.subheader("Job Description")
    jd_text = st.text_area(
        "Paste the job description", height=280, placeholder="Paste job description here"
    )

analyze_clicked = st.button("🔍 Analyze Match", use_container_width=True)

if analyze_clicked:
    # Resolve CV text from either upload or pasted text
    cv_text = ""
    if cv_file is not None:
        with st.spinner("Reading PDF..."):
            cv_text = extract_text_from_pdf(cv_file)
    elif cv_text_manual.strip():
        cv_text = cv_text_manual.strip()

    if not cv_text:
        st.warning("Please upload a CV PDF or paste your CV text.")
    elif not jd_text.strip():
        st.warning("Please paste a job description.")
    else:
        with st.spinner("Analyzing match with Claude..."):
            try:
                result = analyze(cv_text, jd_text)
            except json.JSONDecodeError:
                st.error("Couldn't parse the model's response. Please try again.")
                st.stop()
            except anthropic.APIError as e:
                st.error(f"API error: {e}")
                st.stop()

        st.markdown("---")

        # Score
        score = result.get("match_score", 0)
        st.markdown(
            f"""
            <div class="score-box">
                <div class="score-number">{score}%</div>
                <div>Match Score</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("")

        res_col1, res_col2 = st.columns(2)

        with res_col1:
            st.subheader("✅ Matched Skills")
            for skill in result.get("matched_skills", []):
                st.markdown(f"- {skill}")

        with res_col2:
            st.subheader("❌ Missing Skills")
            for skill in result.get("missing_skills", []):
                st.markdown(f"- {skill}")

        st.subheader("💡 Suggestions to Improve Your CV")
        for i, suggestion in enumerate(result.get("suggestions", []), start=1):
            st.markdown(f"**{i}.** {suggestion}")

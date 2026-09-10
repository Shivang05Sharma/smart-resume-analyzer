import streamlit as st
import pdfplumber

from docx import Document

from analyzer import (
    extract_skills,
    calculate_ats_score,
    calculate_job_match,
    find_missing_skills,
)


# -----------------------------
# PAGE CONFIGURATION
# -----------------------------

st.set_page_config(
    page_title="Smart Resume Analyzer",
    page_icon="📄",
    layout="wide"
)


# -----------------------------
# FUNCTIONS
# -----------------------------

def extract_pdf_text(file):
    """Extract text from PDF."""

    text = ""

    with pdfplumber.open(file) as pdf:

        for page in pdf.pages:

            page_text = page.extract_text()

            if page_text:
                text += page_text + "\n"

    return text


def extract_docx_text(file):
    """Extract text from DOCX."""

    document = Document(file)

    text = ""

    for paragraph in document.paragraphs:
        text += paragraph.text + "\n"

    return text


def extract_resume_text(file):

    file_name = file.name.lower()

    if file_name.endswith(".pdf"):
        return extract_pdf_text(file)

    elif file_name.endswith(".docx"):
        return extract_docx_text(file)

    else:
        return ""


# -----------------------------
# HEADER
# -----------------------------

st.title("📄 Smart Resume Analyzer")

st.write(
    "Analyze your resume, identify skills, calculate an ATS-style "
    "score and compare your resume with a job description."
)

st.divider()


# -----------------------------
# SIDEBAR
# -----------------------------

with st.sidebar:

    st.header("⚙️ Settings")

    st.write("Upload your resume and optionally provide a job description.")

    st.info(
        "Supported formats:\n\n"
        "• PDF\n"
        "• DOCX"
    )


# -----------------------------
# RESUME UPLOAD
# -----------------------------

uploaded_file = st.file_uploader(
    "Upload your Resume",
    type=["pdf", "docx"]
)


# -----------------------------
# JOB DESCRIPTION
# -----------------------------

job_description = st.text_area(
    "Paste Job Description (Optional)",
    height=200,
    placeholder="Paste the job description here..."
)


# -----------------------------
# ANALYZE BUTTON
# -----------------------------

if uploaded_file:

    if st.button(
        "🚀 Analyze Resume",
        use_container_width=True
    ):

        with st.spinner("Analyzing your resume..."):

            resume_text = extract_resume_text(
                uploaded_file
            )

        if not resume_text.strip():

            st.error(
                "Could not extract text from this file."
            )

        else:

            # -----------------------------
            # ANALYSIS
            # -----------------------------

            ats_score, feedback = calculate_ats_score(
                resume_text
            )

            skills = extract_skills(
                resume_text
            )

            # -----------------------------
            # TOP METRICS
            # -----------------------------

            st.subheader("📊 Resume Analysis")

            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric(
                    "ATS Score",
                    f"{ats_score}/100"
                )

            with col2:
                st.metric(
                    "Skills Detected",
                    len(skills)
                )

            with col3:

                word_count = len(
                    resume_text.split()
                )

                st.metric(
                    "Word Count",
                    word_count
                )

            st.divider()

            # -----------------------------
            # SCORE PROGRESS
            # -----------------------------

            st.subheader("ATS Score")

            st.progress(
                ats_score / 100
            )

            if ats_score >= 80:

                st.success(
                    "Excellent resume structure!"
                )

            elif ats_score >= 60:

                st.warning(
                    "Good start, but there is room for improvement."
                )

            else:

                st.error(
                    "Your resume needs significant improvement."
                )

            # -----------------------------
            # SKILLS
            # -----------------------------

            st.subheader("🧠 Detected Skills")

            if skills:

                skill_text = " • ".join(
                    skill.title()
                    for skill in skills
                )

                st.write(skill_text)

            else:

                st.warning(
                    "No recognized technical skills detected."
                )

            # -----------------------------
            # JOB MATCH
            # -----------------------------

            if job_description.strip():

                st.divider()

                st.subheader(
                    "🎯 Job Description Match"
                )

                match_score = calculate_job_match(
                    resume_text,
                    job_description
                )

                st.metric(
                    "Job Match",
                    f"{match_score}%"
                )

                st.progress(
                    match_score / 100
                )

                # Missing skills

                missing_skills = find_missing_skills(
                    resume_text,
                    job_description
                )

                st.subheader(
                    "❌ Missing Skills"
                )

                if missing_skills:

                    for skill in missing_skills:

                        st.write(
                            f"• {skill.title()}"
                        )

                else:

                    st.success(
                        "No major missing skills detected!"
                    )

            # -----------------------------
            # FEEDBACK
            # -----------------------------

            st.divider()

            st.subheader(
                "💡 Improvement Suggestions"
            )

            if feedback:

                for item in feedback:

                    st.write(
                        f"🔹 {item}"
                    )

            else:

                st.success(
                    "No major issues detected."
                )

            # -----------------------------
            # RESUME TEXT
            # -----------------------------

            with st.expander(
                "📃 View Extracted Resume Text"
            ):

                st.text(
                    resume_text
                )

else:

    st.info(
        "👆 Upload a PDF or DOCX resume to begin."
    )
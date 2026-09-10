import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


# Skills that the analyzer can detect
SKILLS = [
    "python",
    "java",
    "c++",
    "c",
    "javascript",
    "typescript",
    "html",
    "css",
    "react",
    "angular",
    "node.js",
    "flask",
    "django",
    "streamlit",
    "sql",
    "mysql",
    "mongodb",
    "postgresql",
    "git",
    "github",
    "docker",
    "aws",
    "azure",
    "machine learning",
    "deep learning",
    "artificial intelligence",
    "data science",
    "data analysis",
    "nlp",
    "tensorflow",
    "pytorch",
    "pandas",
    "numpy",
    "scikit-learn",
    "excel",
    "power bi",
    "tableau",
    "rest api",
    "api",
    "linux",
    "cybersecurity",
    "ethical hacking",
    "cloud computing",
]


def clean_text(text):
    """Clean resume text."""

    text = text.lower()

    # Remove unnecessary characters
    text = re.sub(r"[^a-zA-Z0-9+#.\-/ ]", " ", text)

    # Remove multiple spaces
    text = re.sub(r"\s+", " ", text)

    return text.strip()


def extract_skills(text):
    """Find known skills inside the resume."""

    text = clean_text(text)

    found_skills = []

    for skill in SKILLS:

        # Escape special characters in skill names
        pattern = r"(?<!\w)" + re.escape(skill.lower()) + r"(?!\w)"

        if re.search(pattern, text):
            found_skills.append(skill)

    return sorted(set(found_skills))


def calculate_ats_score(text):
    """
    Calculate a simple ATS-style score.

    This is not an official ATS score.
    """

    text_lower = clean_text(text)

    score = 0
    feedback = []

    # 1. Length
    word_count = len(text_lower.split())

    if word_count >= 400:
        score += 20
    elif word_count >= 250:
        score += 15
    elif word_count >= 150:
        score += 10
    else:
        score += 5
        feedback.append("Resume appears too short.")

    # 2. Skills
    skills = extract_skills(text)

    if len(skills) >= 10:
        score += 20
    elif len(skills) >= 6:
        score += 15
    elif len(skills) >= 3:
        score += 10
    else:
        score += 5
        feedback.append("Add more relevant technical skills.")

    # 3. Important sections
    sections = {
        "education": ["education", "academic"],
        "experience": ["experience", "employment", "work history"],
        "projects": ["projects", "project"],
        "skills": ["skills", "technical skills"],
        "certifications": ["certification", "certifications"],
    }

    section_score = 0

    for section, keywords in sections.items():

        if any(keyword in text_lower for keyword in keywords):
            section_score += 5
        else:
            feedback.append(f"Consider adding a {section} section.")

    score += section_score

    # Maximum section points = 25
    # Remaining 35 points for quality indicators

    # 4. Contact information
    email_exists = re.search(
        r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}",
        text
    )

    phone_exists = re.search(
        r"\b\d{10}\b",
        text
    )

    if email_exists:
        score += 5
    else:
        feedback.append("Email address not detected.")

    if phone_exists:
        score += 5
    else:
        feedback.append("Phone number not detected.")

    # 5. Action words
    action_words = [
        "developed",
        "created",
        "implemented",
        "designed",
        "built",
        "managed",
        "analyzed",
        "optimized",
        "led",
        "automated",
        "improved",
    ]

    action_count = sum(
        1 for word in action_words if word in text_lower
    )

    if action_count >= 5:
        score += 10
    elif action_count >= 2:
        score += 5
    else:
        feedback.append(
            "Use stronger action verbs such as Developed, Built, Implemented, or Optimized."
        )

    # 6. Numbers / measurable achievements
    numbers = re.findall(r"\b\d+%|\b\d+\+|\b\d+\b", text_lower)

    if len(numbers) >= 5:
        score += 10
    elif len(numbers) >= 2:
        score += 5
    else:
        feedback.append(
            "Add measurable results to projects or achievements."
        )

    # Ensure score doesn't exceed 100
    score = min(score, 100)

    return score, feedback


def calculate_job_match(resume_text, job_description):
    """Compare resume with job description using TF-IDF."""

    resume = clean_text(resume_text)
    job = clean_text(job_description)

    if not resume or not job:
        return 0

    vectorizer = TfidfVectorizer(
        stop_words="english"
    )

    try:
        vectors = vectorizer.fit_transform(
            [resume, job]
        )

        similarity = cosine_similarity(
            vectors[0:1],
            vectors[1:2]
        )[0][0]

        return round(similarity * 100, 2)

    except ValueError:
        return 0


def find_missing_skills(resume_text, job_description):
    """Find skills mentioned in job description but absent from resume."""

    resume_skills = set(extract_skills(resume_text))
    job_skills = set(extract_skills(job_description))

    missing = job_skills - resume_skills

    return sorted(missing)
"""
analyzer.py
Pure Python rule-based resume analyser.
No AI / LLM / external API required.
"""

import re
import string
from collections import Counter


# ─────────────────────────────────────────────
# STOPWORDS  (basic English stopwords)
# ─────────────────────────────────────────────
STOPWORDS = {
    "a", "an", "the", "and", "or", "but", "in", "on", "at", "to", "for",
    "of", "with", "by", "from", "is", "are", "was", "were", "be", "been",
    "being", "have", "has", "had", "do", "does", "did", "will", "would",
    "could", "should", "may", "might", "shall", "can", "need", "dare",
    "ought", "used", "that", "this", "these", "those", "i", "you", "he",
    "she", "it", "we", "they", "me", "him", "her", "us", "them", "my",
    "your", "his", "its", "our", "their", "who", "which", "what", "how",
    "when", "where", "why", "all", "each", "every", "both", "few", "more",
    "most", "other", "into", "through", "during", "before", "after",
    "above", "below", "between", "out", "off", "over", "under", "again",
    "then", "once", "here", "there", "any", "also", "as", "if", "so",
    "than", "about", "up", "no", "not", "only", "same", "such", "own",
    "just", "because", "while", "although", "however", "therefore",
}

# ─────────────────────────────────────────────
# PREDEFINED SKILLS DATABASE
# ─────────────────────────────────────────────
TECH_SKILLS = {
    # Programming Languages
    "python", "java", "javascript", "typescript", "c", "c++", "c#", "ruby",
    "php", "swift", "kotlin", "go", "rust", "scala", "r", "matlab", "perl",
    "bash", "shell", "powershell", "dart", "lua",
    # Web
    "html", "css", "react", "angular", "vue", "node", "nodejs", "express",
    "django", "flask", "fastapi", "spring", "asp.net", "jquery", "bootstrap",
    "tailwind", "graphql", "rest", "restful", "api", "oauth", "jwt",
    # Databases
    "sql", "mysql", "postgresql", "mongodb", "redis", "sqlite", "oracle",
    "cassandra", "firebase", "dynamodb", "elasticsearch", "nosql",
    # Cloud & DevOps
    "aws", "azure", "gcp", "docker", "kubernetes", "terraform", "ansible",
    "jenkins", "github", "gitlab", "bitbucket", "ci/cd", "linux", "unix",
    "nginx", "apache", "heroku", "vercel", "netlify",
    # Data & ML
    "machine learning", "deep learning", "nlp", "data science", "pandas",
    "numpy", "scikit-learn", "tensorflow", "pytorch", "keras", "opencv",
    "tableau", "power bi", "excel", "spark", "hadoop", "kafka",
    # Soft Skills
    "communication", "teamwork", "leadership", "problem solving",
    "critical thinking", "time management", "collaboration", "agile",
    "scrum", "kanban", "jira", "confluence",
    # Other
    "git", "linux", "testing", "unit testing", "debugging", "oop",
    "data structures", "algorithms", "microservices", "blockchain",
    "cybersecurity", "networking", "mobile development", "android", "ios",
}

# ─────────────────────────────────────────────
# RESUME SECTION KEYWORDS
# ─────────────────────────────────────────────
SECTION_PATTERNS = {
    "Education":    ["education", "academic", "degree", "university", "college",
                     "bachelor", "master", "phd", "b.tech", "m.tech", "b.sc", "m.sc"],
    "Experience":   ["experience", "work experience", "employment", "internship",
                     "intern", "worked at", "job", "position", "role", "company"],
    "Skills":       ["skills", "technical skills", "core competencies",
                     "technologies", "tools", "stack", "proficient"],
    "Projects":     ["projects", "personal projects", "academic projects",
                     "portfolio", "built", "developed", "created"],
    "Achievements": ["achievements", "awards", "honors", "certifications",
                     "certificate", "accomplishments", "recognition"],
    "Summary":      ["summary", "objective", "profile", "about me",
                     "career objective", "professional summary"],
}


# ─────────────────────────────────────────────
# TEXT UTILITIES
# ─────────────────────────────────────────────

def clean_text(text: str) -> str:
    """Lowercase and remove punctuation from text."""
    text = text.lower()
    text = text.translate(str.maketrans("", "", string.punctuation.replace("/", "")))
    return text


def tokenize(text: str) -> list[str]:
    """Split cleaned text into meaningful tokens, removing stopwords."""
    words = re.findall(r'\b[a-z][a-z0-9+#./]*\b', clean_text(text))
    return [w for w in words if w not in STOPWORDS and len(w) > 1]


def extract_keywords(text: str, top_n: int = 30) -> list[str]:
    """Return the most frequent meaningful keywords from text."""
    tokens = tokenize(text)
    freq = Counter(tokens)
    return [word for word, _ in freq.most_common(top_n)]


def extract_skills(text: str) -> set[str]:
    """Extract skills from text by matching against the predefined skills database."""
    text_lower = clean_text(text)
    found = set()
    for skill in TECH_SKILLS:
        # Use word-boundary matching for single-word skills
        if " " in skill:
            if skill in text_lower:
                found.add(skill)
        else:
            if re.search(rf'\b{re.escape(skill)}\b', text_lower):
                found.add(skill)
    return found


# ─────────────────────────────────────────────
# SECTION DETECTION
# ─────────────────────────────────────────────

def detect_sections(resume_text: str) -> dict[str, bool]:
    """Check which standard resume sections are present."""
    text_lower = resume_text.lower()
    found = {}
    for section, keywords in SECTION_PATTERNS.items():
        found[section] = any(kw in text_lower for kw in keywords)
    return found


# ─────────────────────────────────────────────
# SCORING FUNCTIONS
# ─────────────────────────────────────────────

def score_skills_match(resume_skills: set, jd_skills: set) -> int:
    """Score how many JD skills appear in the resume."""
    if not jd_skills:
        return 50
    matched = resume_skills & jd_skills
    return min(100, int((len(matched) / len(jd_skills)) * 100))


def score_keyword_match(resume_text: str, jd_text: str) -> int:
    """Score keyword overlap between resume and JD."""
    jd_keywords = set(extract_keywords(jd_text, top_n=40))
    resume_keywords = set(tokenize(resume_text))
    if not jd_keywords:
        return 50
    matched = jd_keywords & resume_keywords
    return min(100, int((len(matched) / len(jd_keywords)) * 100))


def score_sections(sections_found: dict) -> int:
    """Score based on how many standard sections are present."""
    total = len(sections_found)
    present = sum(1 for v in sections_found.values() if v)
    return int((present / total) * 100)


def score_content_quality(resume_text: str) -> int:
    """Score based on resume length, bullet points, and word variety."""
    words = resume_text.split()
    word_count = len(words)
    bullet_count = resume_text.count("•") + resume_text.count("-") + resume_text.count("*")
    unique_ratio = len(set(w.lower() for w in words)) / max(word_count, 1)

    # Word count score (ideal: 300-700 words)
    if word_count < 100:
        length_score = 20
    elif word_count < 200:
        length_score = 50
    elif word_count <= 700:
        length_score = 100
    elif word_count <= 900:
        length_score = 80
    else:
        length_score = 60

    bullet_score = min(100, bullet_count * 10)     # up to 10 bullets = 100
    variety_score = min(100, int(unique_ratio * 150))

    return int((length_score * 0.4) + (bullet_score * 0.3) + (variety_score * 0.3))


def score_ats(resume_text: str) -> int:
    """
    ATS compatibility: checks for plain formatting, no tables (hard to detect
    from plain text), keyword density, and proper section headers.
    """
    score = 60  # base
    text_lower = resume_text.lower()

    # Has contact info indicators
    if re.search(r'[\w.+-]+@[\w-]+\.[a-z]+', resume_text):
        score += 10  # email found
    if re.search(r'\+?\d[\d\s\-().]{7,}\d', resume_text):
        score += 5   # phone found

    # Has clear section headers
    header_hits = sum(
        1 for kws in SECTION_PATTERNS.values()
        if any(kw in text_lower for kw in kws)
    )
    score += min(15, header_hits * 3)

    # Penalise very short resumes
    if len(resume_text.split()) < 150:
        score -= 20

    return max(0, min(100, score))


# ─────────────────────────────────────────────
# SUGGESTION ENGINE
# ─────────────────────────────────────────────

def generate_suggestions(
    sections: dict,
    resume_skills: set,
    jd_skills: set,
    resume_text: str,
    missing_keywords: list,
) -> list[str]:
    """Generate actionable, rule-based improvement suggestions."""
    tips = []
    word_count = len(resume_text.split())

    # Section-based tips
    if not sections.get("Summary"):
        tips.append("Add a 2-3 sentence professional summary at the top of your resume.")
    if not sections.get("Projects"):
        tips.append("Add a Projects section to showcase hands-on work or academic projects.")
    if not sections.get("Achievements"):
        tips.append("Include an Achievements or Certifications section to stand out.")
    if not sections.get("Skills"):
        tips.append("Add a dedicated Skills section listing your technical and soft skills.")
    if not sections.get("Experience"):
        tips.append("Add work experience or internship details (even part-time counts).")

    # Keyword tips
    if missing_keywords:
        top_missing = ", ".join(missing_keywords[:5])
        tips.append(f"Add these missing keywords from the JD to boost ATS score: {top_missing}.")

    # Content tips
    if word_count < 250:
        tips.append("Your resume is too short. Aim for 300–600 words with detailed descriptions.")
    elif word_count > 900:
        tips.append("Your resume is too long. Try to keep it under 1 page (300–600 words).")

    bullet_count = resume_text.count("•") + resume_text.count("-") + resume_text.count("*")
    if bullet_count < 5:
        tips.append("Use bullet points to describe your experience — easier for recruiters to scan.")

    if not re.search(r'[\w.+-]+@[\w-]+\.[a-z]+', resume_text):
        tips.append("Make sure your email address is included in the resume.")

    if not re.search(r'\+?\d[\d\s\-().]{7,}\d', resume_text):
        tips.append("Add your phone number so recruiters can contact you easily.")

    # Quantification tip
    if not re.search(r'\d+%|\d+ years?|\d+\+', resume_text):
        tips.append("Quantify your achievements (e.g., 'Improved performance by 30%', '2+ years of experience').")

    return tips[:7]   # return top 7 tips


# ─────────────────────────────────────────────
# STRENGTHS & WEAKNESSES
# ─────────────────────────────────────────────

def find_strengths(sections: dict, resume_skills: set, jd_skills: set, resume_text: str) -> list[str]:
    strengths = []
    word_count = len(resume_text.split())

    if len(resume_skills & jd_skills) >= 5:
        strengths.append(f"Strong skill alignment — {len(resume_skills & jd_skills)} matching skills found.")
    if sections.get("Experience"):
        strengths.append("Work/internship experience section is present.")
    if sections.get("Projects"):
        strengths.append("Projects section adds practical credibility.")
    if sections.get("Education"):
        strengths.append("Education qualifications are clearly mentioned.")
    if 250 <= word_count <= 800:
        strengths.append("Resume length is within the ideal range.")
    if re.search(r'[\w.+-]+@[\w-]+\.[a-z]+', resume_text):
        strengths.append("Contact email is present for easy recruiter reach-out.")
    if re.search(r'\d+%|\d+ years?|\d+\+', resume_text):
        strengths.append("Quantified achievements found — great for impact!")
    if sections.get("Achievements"):
        strengths.append("Certifications/achievements section is present.")

    return strengths[:5] if strengths else ["Resume has basic structure in place."]


def find_weaknesses(sections: dict, resume_skills: set, jd_skills: set, resume_text: str) -> list[str]:
    weaknesses = []
    word_count = len(resume_text.split())

    if not sections.get("Summary"):
        weaknesses.append("Missing professional summary/objective section.")
    if not sections.get("Projects"):
        weaknesses.append("No Projects section — missed opportunity to show hands-on skills.")
    if not sections.get("Achievements"):
        weaknesses.append("No Achievements/Certifications section found.")
    if word_count < 200:
        weaknesses.append("Resume content is too thin — add more detail to each section.")
    if word_count > 900:
        weaknesses.append("Resume is too long — condense to 1 page for better readability.")
    if len(resume_skills & jd_skills) < 3:
        weaknesses.append("Very few skills match the job description — tailor your skills section.")
    if not re.search(r'\d+%|\d+ years?|\d+\+', resume_text):
        weaknesses.append("No quantified achievements — add numbers to make impact clear.")

    return weaknesses[:5] if weaknesses else ["No major weaknesses detected — great job!"]


# ─────────────────────────────────────────────
# MAIN ANALYSE FUNCTION
# ─────────────────────────────────────────────

def analyse_resume(resume_text: str, job_description: str) -> dict:
    """
    Perform full rule-based resume analysis.
    Returns a dict with scores, keywords, strengths, weaknesses, and suggestions.
    """
    # Extract skills
    resume_skills = extract_skills(resume_text)
    jd_skills = extract_skills(job_description)

    # Extract keywords
    jd_keywords = set(extract_keywords(job_description, top_n=40))
    resume_tokens = set(tokenize(resume_text))
    matched_kw = sorted(jd_keywords & resume_tokens)
    missing_kw = sorted(jd_keywords - resume_tokens)

    # Detect sections
    sections = detect_sections(resume_text)

    # Section scores
    skills_score      = score_skills_match(resume_skills, jd_skills)
    keyword_score     = score_keyword_match(resume_text, job_description)
    section_score     = score_sections(sections)
    content_score     = score_content_quality(resume_text)
    ats_score         = score_ats(resume_text)

    # Overall weighted score
    overall = int(
        skills_score  * 0.30 +
        keyword_score * 0.25 +
        section_score * 0.20 +
        content_score * 0.15 +
        ats_score     * 0.10
    )

    # Strengths, weaknesses, suggestions
    strengths   = find_strengths(sections, resume_skills, jd_skills, resume_text)
    weaknesses  = find_weaknesses(sections, resume_skills, jd_skills, resume_text)
    suggestions = generate_suggestions(sections, resume_skills, jd_skills, resume_text, missing_kw)

    # Summary line
    matched_count = len(resume_skills & jd_skills)
    total_jd      = len(jd_skills) or 1
    summary = (
        f"Your resume matches {matched_count} out of {total_jd} required skills from the job description. "
        f"It has {sum(sections.values())} of {len(sections)} standard sections detected. "
        f"Overall keyword overlap is {keyword_score}% — review the missing keywords to improve ATS ranking."
    )

    return {
        "overall_score": overall,
        "sections": {
            "Skills Match":          skills_score,
            "Keyword Overlap":       keyword_score,
            "Section Coverage":      section_score,
            "Content Quality":       content_score,
            "ATS Compatibility":     ats_score,
        },
        "strengths":         strengths,
        "weaknesses":        weaknesses,
        "suggestions":       suggestions,
        "matched_keywords":  matched_kw[:20],
        "missing_keywords":  missing_kw[:20],
        "matched_skills":    sorted(resume_skills & jd_skills),
        "missing_skills":    sorted(jd_skills - resume_skills),
        "sections_found":    sections,
        "summary":           summary,
        "word_count":        len(resume_text.split()),
    }


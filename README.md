# AI Resume Analyser

> **Developer:** Harshil Mangal  
> **GitHub:** [@b241155-cloud](https://github.com/b241155-cloud)

A resume analysis tool built with **Streamlit** + pure **Python** backend.  
**No API key, no AI model, no internet required** — works fully offline.

---

## Features

- Upload resume in **PDF or DOCX** format
- Paste any **Job Description** to match against
- **Keyword matching** — finds matched & missing keywords
- **Skills detection** — from a built-in database of 80+ tech/soft skills
- **Section coverage** — checks for Education, Experience, Projects, etc.
- **ATS compatibility score** — contact info, headers, formatting
- **Content quality score** — word count, bullet points, word variety
- **Radar chart + Bar chart** — visual score breakdown
- **Actionable suggestions** — rule-based tips to improve the resume

---

## Project Structure

```
ai-resume-analyser/
├── app.py              # Streamlit frontend
├── resume_parser.py    # PDF & DOCX text extraction
├── analyzer.py         # Pure Python rule-based analysis engine
├── utils.py            # Score helpers & chart utilities
├── requirements.txt    # Dependencies (no LLM libraries)
└── README.md
```

---

## Setup & Run

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the app
```bash
streamlit run app.py
```

Opens at **http://localhost:8501**

---

## How the Scoring Works

| Section Score      | What it checks                                        | Weight |
|--------------------|-------------------------------------------------------|--------|
| Skills Match       | Resume skills vs JD skills from built-in database     | 30%    |
| Keyword Overlap    | Top JD keywords found in resume text                  | 25%    |
| Section Coverage   | Education, Experience, Projects, Skills, etc.         | 20%    |
| Content Quality    | Word count, bullet points, vocabulary variety         | 15%    |
| ATS Compatibility  | Email, phone, section headers present                 | 10%    |

---

## Tech Stack

| Layer      | Technology      |
|------------|-----------------|
| Frontend   | Streamlit       |
| Backend    | Pure Python     |
| PDF Parse  | PyPDF2          |
| DOCX Parse | python-docx     |
| Charts     | Plotly          |
| NLP        | re, collections |

---

## Notes

- Resume must be a **text-based PDF** (not a scanned image)
- Analysis runs instantly — no API calls, no waiting
- The skills database covers 80+ programming languages, frameworks, tools & soft skills

"""
app.py
Main Streamlit application for AI Resume Analyser.
Backend: Pure Python (no LLM / no API key required)
Run with: streamlit run app.py
"""

import streamlit as st
import plotly.graph_objects as go

from resume_parser import extract_resume_text
from analyzer import analyse_resume
from utils import score_color, score_label, build_radar_data

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="AI Resume Analyser",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# CUSTOM CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
    .main-title {
        font-size: 2.4rem;
        font-weight: 700;
        color: #1a1a2e;
        text-align: center;
        margin-bottom: 0.2rem;
    }
    .sub-title {
        font-size: 1rem;
        color: #555;
        text-align: center;
        margin-bottom: 2rem;
    }
    .score-card {
        background: #f8f9fa;
        border-radius: 12px;
        padding: 1.4rem;
        text-align: center;
        border: 2px solid #e9ecef;
    }
    .score-number {
        font-size: 3.2rem;
        font-weight: 800;
        line-height: 1;
    }
    .score-label {
        font-size: 1rem;
        color: #555;
        margin-top: 0.3rem;
    }
    .tag {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.82rem;
        margin: 3px 2px;
    }
    .tag-green { background:#d4edda; color:#155724; }
    .tag-red   { background:#f8d7da; color:#721c24; }
    .tag-blue  { background:#d1ecf1; color:#0c5460; }
    .section-tick { font-size: 1rem; margin: 2px 0; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/resume.png", width=70)
    st.title("Resume Analyser")
    st.markdown("**No API key needed!**")
    st.markdown("Pure Python analysis engine.")
    st.divider()
    st.markdown("### How to use")
    st.markdown("""
1. Upload your **Resume** (PDF or DOCX)
2. Paste the **Job Description**
3. Click **Analyse Resume**
4. Review your score and suggestions
    """)
    st.divider()
    st.markdown("#### What gets checked")
    st.markdown("""
- Skills & keyword match  
- Section coverage  
- Content quality  
- ATS compatibility  
- Missing keywords  
    """)
    st.caption("Built with Python + Streamlit")

# ─────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────
st.markdown('<div class="main-title">Resume Analyser</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="sub-title">Get instant feedback on your resume — no AI key required</div>',
    unsafe_allow_html=True,
)

# ─────────────────────────────────────────────
# INPUT
# ─────────────────────────────────────────────
col_left, col_right = st.columns([1, 1], gap="large")

with col_left:
    st.subheader("Upload Your Resume")
    uploaded_file = st.file_uploader(
        "Choose a PDF or DOCX file",
        type=["pdf", "docx"],
        help="Text-based PDFs work best. Scanned/image PDFs may not parse well.",
    )
    if uploaded_file:
        st.success(f"Uploaded: **{uploaded_file.name}**")

with col_right:
    st.subheader("Job Description")
    job_description = st.text_area(
        "Paste the job description here",
        height=210,
        placeholder=(
            "e.g. We are looking for a Python Developer with experience "
            "in Django, REST APIs, PostgreSQL and Docker..."
        ),
    )

st.divider()

analyse_btn = st.button("Analyse Resume", use_container_width=True, type="primary")

# ─────────────────────────────────────────────
# ANALYSIS
# ─────────────────────────────────────────────
if analyse_btn:
    if not uploaded_file:
        st.error("Please upload your resume (PDF or DOCX).")
        st.stop()
    if not job_description.strip():
        st.error("Please paste the job description.")
        st.stop()

    with st.spinner("Reading your resume..."):
        try:
            resume_text = extract_resume_text(uploaded_file)
        except ValueError as e:
            st.error(str(e))
            st.stop()

    if len(resume_text.split()) < 30:
        st.warning(
            "Resume text is very short. "
            "Make sure the PDF is not a scanned image — use a text-based PDF."
        )
        st.stop()

    with st.spinner("Analysing..."):
        result = analyse_resume(resume_text, job_description)

    st.success("Analysis complete!")
    st.markdown("---")

    # ══════════════════════════════════════════
    # OVERALL SCORE + SUMMARY
    # ══════════════════════════════════════════
    st.markdown("## Overall Resume Score")
    overall = result["overall_score"]
    color   = score_color(overall)
    label   = score_label(overall)

    c1, c2, c3 = st.columns([1, 1.6, 1.4])

    with c1:
        st.markdown(
            f"""<div class="score-card">
                <div class="score-number" style="color:{color}">{overall}<span style="font-size:1.4rem">/100</span></div>
                <div class="score-label">{label}</div>
                <div style="font-size:0.82rem;margin-top:0.5rem;color:#888">
                    Word count: {result['word_count']}
                </div>
            </div>""",
            unsafe_allow_html=True,
        )

    with c2:
        st.info(f"**Summary**\n\n{result['summary']}")

    with c3:
        # Section presence checklist
        st.markdown("**Sections Detected**")
        for section, found in result["sections_found"].items():
            icon = "✅" if found else "❌"
            st.markdown(f"{icon} {section}", unsafe_allow_html=False)

    st.markdown("---")

    # ══════════════════════════════════════════
    # SECTION SCORES — Bar Chart
    # ══════════════════════════════════════════
    st.markdown("## Section-wise Scores")
    sections_data = result["sections"]
    labels, values = build_radar_data(sections_data)
    colors = [score_color(v) for v in values]

    fig_bar = go.Figure(go.Bar(
        x=values,
        y=labels,
        orientation="h",
        marker_color=colors,
        text=[f"{v}/100" for v in values],
        textposition="outside",
    ))
    fig_bar.update_layout(
        xaxis=dict(range=[0, 115], showgrid=False, zeroline=False),
        yaxis=dict(autorange="reversed"),
        height=280,
        margin=dict(l=10, r=50, t=20, b=10),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
    )
    st.plotly_chart(fig_bar, use_container_width=True)

    st.markdown("---")

    # ══════════════════════════════════════════
    # STRENGTHS & WEAKNESSES
    # ══════════════════════════════════════════
    col_s, col_w = st.columns(2, gap="large")

    with col_s:
        st.markdown("### Strengths")
        for s in result["strengths"]:
            st.markdown(f"- {s}")

    with col_w:
        st.markdown("### Areas to Improve")
        for w in result["weaknesses"]:
            st.markdown(f"- {w}")

    st.markdown("---")

    # ══════════════════════════════════════════
    # KEYWORD ANALYSIS
    # ══════════════════════════════════════════
    st.markdown("## Keyword Analysis")
    kw1, kw2 = st.columns(2)

    with kw1:
        st.markdown("**Matched Keywords** *(found in your resume)*")
        matched = result["matched_keywords"]
        if matched:
            html = " ".join(f'<span class="tag tag-green">{k}</span>' for k in matched)
            st.markdown(html, unsafe_allow_html=True)
        else:
            st.caption("None matched.")

    with kw2:
        st.markdown("**Missing Keywords** *(add these to your resume)*")
        missing = result["missing_keywords"]
        if missing:
            html = " ".join(f'<span class="tag tag-red">{k}</span>' for k in missing)
            st.markdown(html, unsafe_allow_html=True)
        else:
            st.caption("Great — all key terms are covered!")

    st.markdown("---")

    # ══════════════════════════════════════════
    # SKILLS ANALYSIS
    # ══════════════════════════════════════════
    st.markdown("## Skills Match")
    sk1, sk2 = st.columns(2)

    with sk1:
        st.markdown("**Matched Skills**")
        matched_skills = result["matched_skills"]
        if matched_skills:
            html = " ".join(f'<span class="tag tag-blue">{s}</span>' for s in matched_skills)
            st.markdown(html, unsafe_allow_html=True)
        else:
            st.caption("No skill overlap detected.")

    with sk2:
        st.markdown("**Skills to Add** *(from JD)*")
        missing_skills = result["missing_skills"]
        if missing_skills:
            html = " ".join(f'<span class="tag tag-red">{s}</span>' for s in missing_skills)
            st.markdown(html, unsafe_allow_html=True)
        else:
            st.caption("All required skills are present!")

    st.markdown("---")

    # ══════════════════════════════════════════
    # SUGGESTIONS
    # ══════════════════════════════════════════
    st.markdown("## Suggestions to Improve Your Resume")
    for i, tip in enumerate(result["suggestions"], 1):
        st.markdown(f"**{i}.** {tip}")

    st.markdown("---")

    # ══════════════════════════════════════════
    # RADAR CHART
    # ══════════════════════════════════════════
    st.markdown("## Skill Radar Chart")
    labels_r, values_r = build_radar_data(sections_data)
    labels_r_closed  = labels_r + [labels_r[0]]
    values_r_closed  = values_r + [values_r[0]]

    fig_radar = go.Figure(go.Scatterpolar(
        r=values_r_closed,
        theta=labels_r_closed,
        fill="toself",
        fillcolor="rgba(52,152,219,0.2)",
        line=dict(color="rgba(52,152,219,0.9)", width=2),
        marker=dict(size=6),
    ))
    fig_radar.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
        height=380,
        margin=dict(l=40, r=40, t=20, b=20),
        paper_bgcolor="rgba(0,0,0,0)",
    )
    r1, r2, r3 = st.columns([1, 2, 1])
    with r2:
        st.plotly_chart(fig_radar, use_container_width=True)

    st.balloons()

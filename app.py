import plotly.graph_objects as go
import plotly.express as px

import re
import io
import fitz
import pandas as pd
import streamlit as st
from docx import Document

st.set_page_config(
    page_title="Resume Analyzer AI",
    page_icon="🚀",
    layout="wide"
)


# CAREERPILOT_PRO_THEME
st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #0b1020 0%, #111827 55%, #17152d 100%);
    color: #e5e7eb;
}
[data-testid="stHeader"] {
    background: rgba(11, 16, 32, 0.85);
}
.block-container {
    max-width: 1200px;
    padding-top: 2rem;
    padding-bottom: 3rem;
}
[data-testid="stSidebar"] {
    background: #10172a;
    border-right: 1px solid #29334d;
}
[data-testid="stMetric"] {
    background: linear-gradient(145deg, #18233b, #202044);
    border: 1px solid #34415f;
    padding: 18px;
    border-radius: 16px;
}
[data-testid="stMetricLabel"] {
    color: #aab7d0;
}
[data-testid="stMetricValue"] {
    color: #ffffff;
}
.stButton > button, .stDownloadButton > button {
    background: linear-gradient(90deg, #6757e8, #3978e8);
    color: white;
    border: 0;
    border-radius: 10px;
    padding: 0.6rem 1.2rem;
    font-weight: 600;
}
.stButton > button:hover, .stDownloadButton > button:hover {
    border: 1px solid #a5b4fc;
    color: white;
}
.stTextArea textarea, .stTextInput input {
    background: #151e32;
    color: #f3f4f6;
    border: 1px solid #3b4968;
    border-radius: 10px;
}
[data-testid="stFileUploader"] {
    background: #151e32;
    border: 1px dashed #6475b8;
    border-radius: 14px;
    padding: 12px;
}
h1, h2, h3 {
    color: #f8fafc;
}
hr {
    border-color: #34415f;
}
</style>
""", unsafe_allow_html=True)

st.sidebar.markdown("""
<div style="padding:18px 8px; margin-bottom:18px;">
    <div style="font-size:25px;font-weight:800;color:#a99bff;">
        🚀 Resume Analyzer AI
    </div>
    <div style="font-size:12px;color:#aab7d0;">
        INTELLIGENT RESUME ANALYZER
    </div>
</div>
""", unsafe_allow_html=True)


KEYWORD_BANK = {
    "Technical Skills": [
        "Python", "Java", "SQL", "Machine Learning",
        "Deep Learning", "NLP", "TensorFlow",
        "PyTorch", "Pandas", "NumPy", "Scikit-learn"
    ],
    "Soft Skills": [
        "Communication", "Teamwork", "Problem Solving",
        "Critical Thinking", "Collaboration"
    ],
    "Tools and Technologies": [
        "Git", "GitHub", "Streamlit", "Flask",
        "AWS", "Azure", "MySQL"
    ],
    "Job Responsibilities": [
        "Data Analysis", "Model Development",
        "Data Preprocessing", "Model Evaluation",
        "API Integration", "Documentation"
    ],
    "Qualifications": [
        "B.Tech", "Artificial Intelligence",
        "Computer Science", "Academic Projects"
    ]
}

WEIGHTS = {
    "Technical Skills": 0.40,
    "Tools and Technologies": 0.20,
    "Job Responsibilities": 0.30,
    "Soft Skills": 0.10
}


def extract_text(uploaded_file):
    data = uploaded_file.getvalue()

    if uploaded_file.name.lower().endswith(".pdf"):
        pdf = fitz.open(stream=data, filetype="pdf")
        return "\n".join(page.get_text() for page in pdf)

    if uploaded_file.name.lower().endswith(".docx"):
        doc = Document(io.BytesIO(data))
        return "\n".join(p.text for p in doc.paragraphs)

    raise ValueError("Upload a PDF or DOCX file.")



KEYWORD_ALIASES = {
    "NLP": ["Natural Language Processing"],
    "Machine Learning": ["ML"],
    "Deep Learning": ["DL"],
    "Scikit-learn": ["sklearn", "scikit learn"],
    "Communication": ["Verbal Communication", "Written Communication"],
    "Teamwork": ["Team Collaboration", "Working in a Team"],
    "Collaboration": ["Collaborative Work"],
    "Problem Solving": ["Problem-solving"],
    "AWS": ["Amazon Web Services"],
    "Azure": ["Microsoft Azure"],
    "GitHub": ["Git Hub"],
    "MySQL": ["My SQL"],
    "Data Analysis": ["Data Analytics"],
    "Model Development": ["ML Model Development"],
    "Data Preprocessing": ["Data Cleaning", "Data Preparation"],
    "Model Evaluation": ["Model Performance Evaluation"],
    "API Integration": ["API Development", "Integrating APIs"],
    "Documentation": ["Technical Documentation"],
    "Academic Projects": ["Academic Project", "College Projects"],
    "Artificial Intelligence": ["AI"],
    "Computer Science": ["Computer Science Engineering", "CSE"]
}

def find_keywords(text, keywords):
    found = []

    for keyword in keywords:
        variations = [keyword] + KEYWORD_ALIASES.get(keyword, [])

        for term in variations:
            pattern = r"(?<!\w)" + re.escape(term) + r"(?!\w)"

            if re.search(pattern, text, re.I):
                found.append(keyword)
                break

    return found



def analyze_job(resume, jd):
    results = {}

    for category, keywords in KEYWORD_BANK.items():
        required = find_keywords(jd, keywords)
        matched = find_keywords(resume, required)
        missing = [k for k in required if k not in matched]

        score = len(matched) / len(required) * 100 if required else 0

        results[category] = {
            "score": round(score, 2),
            "matched": matched,
            "missing": missing
        }

    total = 0
    used_weight = 0

    for category, weight in WEIGHTS.items():
        data = results[category]

        if data["matched"] or data["missing"]:
            total += data["score"] * weight
            used_weight += weight

    job_score = total / used_weight if used_weight else 0

    return round(job_score, 2), results




def validate_resume(text):
    text_lower = text.lower()

    patterns = {
        "education": r"education|academic qualifications|qualification",
        "skills": r"technical skills|key skills|skills|core competencies",
        "experience": r"work experience|professional experience|employment history",
        "projects": r"academic projects|personal projects|projects",
        "internship": r"internships|internship experience",
        "certifications": r"certifications|certificates",
        "summary": r"professional summary|profile summary|career objective|objective"
    }

    found = [
        name for name, pattern in patterns.items()
        if re.search(pattern, text_lower)
    ]

    has_email = bool(re.search(r"[\w.+-]+@[\w.-]+\.\w+", text))
    has_phone = bool(re.search(r"\b\d{10}\b", text))
    has_contact = has_email or has_phone

    has_core_section = any(
        section in found
        for section in ["skills", "experience", "projects", "internship"]
    )

    return (
        (has_contact and len(found) >= 2)
        or (len(found) >= 3 and has_core_section)
    )


def resume_quality(text):

    words = re.findall(r"\b[\w+#.-]+\b", text)
    word_count = len(words)

    checks = {}

    # 1. Contact information
    checks["Contact information"] = bool(
        re.search(r"[\w.+-]+@[\w.-]+\.\w+", text)
    )

    # 2. Education
    checks["Education section"] = bool(
        re.search(r"\beducation\b", text, re.I)
    )

    # 3. Skills
    checks["Skills section"] = bool(
        re.search(r"\bskills\b", text, re.I)
    )

    # 4. Projects or experience
    checks["Projects or experience"] = bool(
        re.search(r"\b(projects|experience|internship)\b", text, re.I)
    )

    # 5. Action verbs
    action_verbs = [
        "developed", "created", "designed", "built",
        "implemented", "trained", "analyzed",
        "managed", "evaluated", "automated",
        "prepared", "improved", "deployed"
    ]

    action_count = sum(
        len(re.findall(r"\b" + verb + r"\b", text, re.I))
        for verb in action_verbs
    )

    checks["Strong action verbs"] = action_count >= 3

    # 6. Quantified achievements
    metric_pattern = (
        r"\b\d+(?:\.\d+)?\s*(?:%|percent|"
        r"years?|months?|days?|users?|records?|"
        r"datasets?|models?|projects?)\b"
    )

    metric_count = len(re.findall(metric_pattern, text, re.I))
    checks["Quantified achievements"] = metric_count >= 2

    # 7. Bullet-point structure
    bullet_count = len(re.findall(r"(?m)^\s*[•●▪\-]", text))
    checks["Bullet-point structure"] = bullet_count >= 3

    # 8. Readability
    sentences = [
        s.strip() for s in re.split(r"[.!?]+", text)
        if len(s.split()) >= 4
    ]

    average_sentence_length = (
        sum(len(s.split()) for s in sentences) / len(sentences)
        if sentences else 0
    )

    checks["Readable sentence length"] = (
        5 <= average_sentence_length <= 30
    )

    # 9. Resume length
    checks["Suitable resume length"] = 150 <= word_count <= 800

    # Weighted scoring
    weights = {
        "Contact information": 10,
        "Education section": 10,
        "Skills section": 10,
        "Projects or experience": 10,
        "Strong action verbs": 15,
        "Quantified achievements": 15,
        "Bullet-point structure": 10,
        "Readable sentence length": 10,
        "Suitable resume length": 10
    }

    score = sum(
        weights[item] * int(checks[item])
        for item in weights
    )

    return round(score, 2), checks, word_count
def generate_suggestions(resume, results):
    suggestions = []

    weak_phrases = {
        "worked on": "Describe your specific contribution.",
        "responsible for": "Explain the task you handled.",
        "helped with": "Mention your actual contribution.",
        "good knowledge of": "Show where you applied this knowledge."
    }

    for phrase, advice in weak_phrases.items():
        if re.search(r"\b" + re.escape(phrase) + r"\b", resume, re.I):
            suggestions.append({
                "Priority": "Medium",
                "Issue": "Weak phrase: " + phrase,
                "Suggestion": advice
            })

    for category, data in results.items():
        if category == "Qualifications":
            continue

        for keyword in data["missing"]:
            suggestions.append({
                "Priority": (
                    "High" if category == "Technical Skills"
                    else "Medium"
                ),
                "Issue": "Missing keyword: " + keyword,
                "Suggestion": (
                    "If you genuinely have this experience, "
                    "add evidence from a project or internship. "
                    "Otherwise, do not add it."
                )
            })

    return suggestions



def generate_rewrites(resume):
    replacements = {
        "worked on": ("Contributed to", "Explain your specific contribution."),
        "responsible for": ("Handled", "Describe the tasks you performed."),
        "helped with": ("Contributed to", "Mention your individual contribution."),
        "good knowledge of": ("Familiar with", "Support this with practical examples."),
        "involved in": ("Contributed to", "Explain your role in the activity.")
    }

    sentences = re.split(r"(?<=[.!?])\s+|\n+", resume)
    rewrites = []

    for sentence in sentences:
        original = sentence.strip()

        for phrase, details in replacements.items():
            replacement, tip = details
            pattern = r"\b" + re.escape(phrase) + r"\b"

            if re.search(pattern, original, re.I):
                improved = re.sub(
                    pattern,
                    replacement,
                    original,
                    count=1,
                    flags=re.I
                )

                rewrites.append({
                    "Original": original,
                    "Suggested Rewrite": improved,
                    "Improvement Tip": (
                        tip + " Add relevant tools, your action "
                        "and genuine results where applicable."
                    )
                })
                break

    return rewrites



def generate_detailed_feedback(resume, missing, checks):
    feedback = []

    # Job requirement gaps
    if missing:
        feedback.append({
            "Area": "Job Requirements",
            "Observation": "Some required skills were not detected.",
            "Recommendation": (
                "Review these skills: " + ", ".join(missing) +
                ". Add them only if you genuinely have the experience."
            )
        })

    # Project descriptions
    if re.search(r"\b(projects?)\b", resume, re.I):
        if not re.search(
            r"\b(developed|implemented|designed|built|created)\b",
            resume, re.I
        ):
            feedback.append({
                "Area": "Project Descriptions",
                "Observation": "Clear project action statements were not detected.",
                "Recommendation": (
                    "Describe what you built, the technologies used, "
                    "your contribution and the outcome."
                )
            })

    # Measurable achievements
    if not checks.get("Quantified achievements", False):
        feedback.append({
            "Area": "Measurable Achievements",
            "Observation": "Few measurable results were detected.",
            "Recommendation": (
                "Where accurate, include genuine figures such as dataset "
                "size, model performance, project duration or users."
            )
        })

    # Resume sections
    for check, passed in checks.items():
        if not passed and check in [
            "Education section",
            "Skills section",
            "Projects or experience"
        ]:
            feedback.append({
                "Area": check,
                "Observation": "This section may need attention.",
                "Recommendation": (
                    "Add or clearly label this section if it is relevant "
                    "to your background."
                )
            })

    return feedback




def build_pdf_report(data, detailed_feedback):
    from io import BytesIO
    from xml.sax.saxutils import escape
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib.units import mm
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    )

    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        rightMargin=18*mm, leftMargin=18*mm,
        topMargin=18*mm, bottomMargin=18*mm
    )

    styles = getSampleStyleSheet()
    story = []

    def para(value, style="BodyText"):
        value = escape(str(value)).replace("\n", "<br/>")
        return Paragraph(value, styles[style])

    def add_table(rows, widths=None):
        wrapped = [
            [para(cell) for cell in row]
            for row in rows
        ]
        table = Table(wrapped, colWidths=widths, repeatRows=1)
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#263746")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("PADDING", (0, 0), (-1, -1), 7),
        ]))
        story.append(table)
        story.append(Spacer(1, 12))

    story.append(para("Resume Analyzer AI", "Title"))
    story.append(para("Resume Analysis Report", "Heading1"))
    story.append(para(
        "Prototype heuristic estimates, not official ATS scores."
    ))
    story.append(Spacer(1, 12))

    story.append(para("1. Overall Results", "Heading2"))
    add_table([
        ["Metric", "Result"],
        ["Resume Quality", f'{data["quality"]}%'],
        ["Job Match", f'{data["job_score"]}%'],
        ["Resume Word Count", data["word_count"]]
    ])

    story.append(para("2. Keyword Analysis", "Heading2"))
    rows = [["Category", "Match (%)", "Matched Keywords", "Missing Keywords"]]

    for category, result in data["results"].items():
        rows.append([
            category,
            result["score"],
            ", ".join(result["matched"]) or "None",
            ", ".join(result["missing"]) or "None"
        ])

    add_table(rows, [32*mm, 20*mm, 55*mm, 55*mm])

    story.append(para("3. Improvement Suggestions", "Heading2"))
    suggestions = data.get("suggestions", [])

    if suggestions:
        rows = [["Priority", "Issue", "Recommendation"]]
        for item in suggestions:
            rows.append([
                item.get("Priority", ""),
                item.get("Issue", ""),
                item.get("Suggestion", "")
            ])
        add_table(rows, [25*mm, 48*mm, 89*mm])
    else:
        story.append(para("No suggestions available."))

    story.append(para("4. Detailed Resume Feedback", "Heading2"))

    if detailed_feedback:
        rows = [["Area", "Observation", "Recommendation"]]
        for item in detailed_feedback:
            rows.append([
                item.get("Area", ""),
                item.get("Observation", ""),
                item.get("Recommendation", "")
            ])
        add_table(rows, [32*mm, 48*mm, 82*mm])
    else:
        story.append(para("No additional feedback detected."))

    story.append(para("5. Before and After Suggestions", "Heading2"))
    rewrites = data.get("rewrites", [])

    if rewrites:
        keys = list(rewrites[0].keys())
        rows = [[key for key in keys]]
        for item in rewrites:
            rows.append([item.get(key, "") for key in keys])
        add_table(rows)
    else:
        story.append(para("No rewrite suggestions available."))

    story.append(para("6. Resume Readiness Checklist", "Heading2"))
    rows = [["Check", "Status"]]

    for item, passed in data["checks"].items():
        rows.append([item, "Passed" if passed else "Needs attention"])

    add_table(rows)

    story.append(Spacer(1, 12))
    story.append(para(
        "Review all recommendations carefully. Only include skills, "
        "experience and achievements that accurately reflect your background."
    ))

    doc.build(story)
    return buffer.getvalue()


# ---------------- DASHBOARD ----------------

st.title("🚀 Resume Analyzer AI")
st.subheader("Intelligent Resume Screening & Job Matching System")

st.write(
    "Analyze your resume, compare it with a job description, "
    "and discover practical improvement opportunities."
)

st.divider()

resume_file = st.file_uploader(
    "Upload your Resume",
    type=["pdf", "docx"]
)

jd = st.text_area(
    "Paste Job Description",
    height=200,
    placeholder="Paste the complete job description here..."
)

if st.button("Analyze My Resume", type="primary"):

    if not resume_file or not jd.strip():
        st.warning("Please upload a resume and enter a job description.")

    else:
        try:
            resume = extract_text(resume_file)

            if not resume.strip():
                st.error("No readable text found in the resume.")
                st.stop()

            if not validate_resume(resume):
                st.error(
                    "This document does not appear to be a resume. "
                    "Please upload a valid resume PDF or DOCX."
                )
                st.stop()

            quality, checks, word_count = resume_quality(resume)
            job_score, results = analyze_job(resume, jd)
            suggestions = generate_suggestions(resume, results)
            rewrites = generate_rewrites(resume)

            st.session_state["analysis"] = {
                "quality": quality,
                "job_score": job_score,
                "checks": checks,
                "results": results,
                "suggestions": suggestions,
                "rewrites": rewrites,
                "resume": resume,
                "word_count": word_count
            }

        except Exception as error:
            st.error(f"Analysis failed: {error}")


if "analysis" in st.session_state:

    data = st.session_state["analysis"]

    st.divider()
    st.header("📊 Resume Analysis Dashboard")

    c1, c2, c3 = st.columns(3)

    c1.metric("Resume Quality", f"{data['quality']}%")
    c2.metric("Job Match", f"{data['job_score']}%")
    c3.metric("Resume Words", data["word_count"])

    st.caption(
        "Scores are prototype heuristic estimates, not official ATS scores."
    )

    st.divider()

    # Stage 1
    st.header("1. Identify Keywords")

    category_rows = []

    for category, result in data["results"].items():
        category_rows.append({
            "Category": category,
            "Match (%)": result["score"],
            "Matched": ", ".join(result["matched"]) or "None",
            "Missing": ", ".join(result["missing"]) or "None"
        })

    st.dataframe(
        pd.DataFrame(category_rows),
        use_container_width=True,
        hide_index=True
    )


    # Visual Analytics
    st.divider()
    st.header("📈 Visual Analytics")

    # 1. Resume Quality Gauge
    gauge = go.Figure(go.Indicator(
        mode="gauge+number",
        value=data["quality"],
        title={"text": "Resume Quality"},
        number={"suffix": "%"},
        gauge={
            "axis": {"range": [0, 100]},
            "bar": {"color": "#16A085"},
            "steps": [
                {"range": [0, 50], "color": "#FDEDEC"},
                {"range": [50, 75], "color": "#FCF3CF"},
                {"range": [75, 100], "color": "#D5F5E3"}
            ]
        }
    ))

    gauge.update_layout(height=280)
    st.plotly_chart(gauge, use_container_width=True)

    # 2. Category Match Chart
    chart_data = pd.DataFrame([
        {"Category": category, "Match": result["score"]}
        for category, result in data["results"].items()
    ])

    category_chart = px.bar(
        chart_data,
        x="Category",
        y="Match",
        title="Job Match by Category",
        range_y=[0, 100],
        text_auto=".1f"
    )

    st.plotly_chart(category_chart, use_container_width=True)

    # 3. Matched vs Missing Keywords
    keyword_data = []

    for category, result in data["results"].items():
        keyword_data.append({
            "Category": category,
            "Status": "Matched",
            "Count": len(result["matched"])
        })
        keyword_data.append({
            "Category": category,
            "Status": "Missing",
            "Count": len(result["missing"])
        })

    keyword_df = pd.DataFrame(keyword_data)

    keyword_chart = px.bar(
        keyword_df,
        x="Category",
        y="Count",
        color="Status",
        barmode="group",
        title="Matched vs Missing Keywords",
        text_auto=True
    )

    st.plotly_chart(keyword_chart, use_container_width=True)

    # Stage 2
    st.header("2. Optimize Resume")

    st.subheader("Improvement Suggestions")

    if data["suggestions"]:
        st.dataframe(
            pd.DataFrame(data["suggestions"]),
            use_container_width=True,
            hide_index=True
        )
    else:
        st.success("No basic wording or keyword gaps detected.")

    st.subheader("Detailed Resume Feedback")

    detailed_feedback = generate_detailed_feedback(
        data["resume"],
        [
            skill
            for result in data["results"].values()
            for skill in result["missing"]
        ],
        data["checks"]
    )

    if detailed_feedback:
        st.dataframe(
            pd.DataFrame(detailed_feedback),
            use_container_width=True,
            hide_index=True
        )
    else:
        st.success("No additional improvement areas detected.")

    st.subheader("Before and After Suggestions")

    if data["rewrites"]:
        st.dataframe(
            pd.DataFrame(data["rewrites"]),
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("No weak phrases detected.")

    st.caption(
        "Review every rewrite and verify that it accurately describes "
        "your actual contribution."
    )

    # Stage 3
    st.header("3. Apply with Confidence")

    st.subheader("Resume Readiness Checklist")

    for item, passed in data["checks"].items():
        if passed:
            st.success("✓ " + item)
        else:
            st.warning("Needs attention: " + item)

    st.info(
        "Review the missing requirements and checklist before applying. "
        "Never add skills or experience you do not have."
    )


    # PDF Analysis Report
    pdf_bytes = build_pdf_report(data, detailed_feedback)

    st.download_button(
        label="📄 Download PDF Analysis Report",
        data=pdf_bytes,
        file_name="CareerPilot_AI_Analysis_Report.pdf",
        mime="application/pdf"
    )

    report = {
        "Resume Quality": data["quality"],
        "Job Match": data["job_score"],
        "Resume Words": data["word_count"],
        "Category Results": data["results"],
        "Suggestions": data["suggestions"],
        "Formatting Checklist": data["checks"]
    }

    report_text = pd.Series(report).to_json(
        indent=4, force_ascii=False
    )

    st.download_button(
        "⬇️ Download Analysis Report",
        data=report_text,
        file_name="CareerPilot_Analysis_Report.json",
        mime="application/json"
    )

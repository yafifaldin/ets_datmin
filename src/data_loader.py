"""
Data Loader Module
==================
Loading data dan precomputed artifacts dengan Streamlit caching.
Mendukung mode demo (synthetic data) ketika dataset asli belum tersedia.
"""

import pandas as pd
import numpy as np
import streamlit as st
import pickle
import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
ASSETS_DIR = PROJECT_ROOT / "assets"


@st.cache_data(show_spinner=False)
def load_skill_taxonomy():
    """Load skill taxonomy untuk form pilihan."""
    with open(ASSETS_DIR / "skill_taxonomy.json", "r", encoding="utf-8") as f:
        return json.load(f)


@st.cache_data(show_spinner=False)
def load_jobs_data():
    """
    Load processed jobs data. Kalau belum ada, generate synthetic demo data.
    """
    jobs_path = PROCESSED_DIR / "jobs_clean.csv"
    if jobs_path.exists():
        df = pd.read_csv(jobs_path)
        # Parse skills_list kalau tersimpan sebagai string
        from .feature_engineering import parse_skills_list
        df["skills_list"] = df["skills_list"].apply(parse_skills_list)
        return df, False  # False = real data
    else:
        # Generate synthetic demo data
        df = _generate_synthetic_jobs()
        return df, True  # True = demo mode


def _generate_synthetic_jobs(n=2000, seed=42):
    """
    Generate synthetic IT job dataset untuk demo mode.
    Strukturnya mengikuti dataset LinkedIn arshkon.
    """
    np.random.seed(seed)

    job_templates = {
        "Data Scientist": {
            "skills": ["Python", "Machine Learning", "Statistics", "SQL", "TensorFlow",
                       "Deep Learning", "Pandas", "Scikit-learn", "PyTorch"],
            "salary_range": (95000, 160000),
            "weight": 12,
        },
        "Data Analyst": {
            "skills": ["SQL", "Python", "Excel", "Tableau", "Power BI", "Statistics",
                       "Data Visualization", "Data Analysis"],
            "salary_range": (60000, 95000),
            "weight": 15,
        },
        "Machine Learning Engineer": {
            "skills": ["Python", "TensorFlow", "PyTorch", "Machine Learning", "MLOps",
                       "Docker", "AWS", "Kubernetes", "Deep Learning"],
            "salary_range": (120000, 180000),
            "weight": 10,
        },
        "Software Engineer": {
            "skills": ["Java", "Python", "JavaScript", "Git", "REST API", "SQL",
                       "Docker", "Linux"],
            "salary_range": (85000, 145000),
            "weight": 18,
        },
        "Backend Developer": {
            "skills": ["Node.js", "Python", "Java", "PostgreSQL", "MongoDB", "REST API",
                       "Docker", "Redis", "Microservices"],
            "salary_range": (80000, 140000),
            "weight": 12,
        },
        "Frontend Developer": {
            "skills": ["JavaScript", "React", "HTML/CSS", "TypeScript", "Vue.js",
                       "Git", "REST API"],
            "salary_range": (70000, 130000),
            "weight": 10,
        },
        "DevOps Engineer": {
            "skills": ["AWS", "Docker", "Kubernetes", "Terraform", "CI/CD", "Jenkins",
                       "Linux", "Python", "Git"],
            "salary_range": (95000, 155000),
            "weight": 8,
        },
        "Cloud Engineer": {
            "skills": ["AWS", "Google Cloud Platform", "Microsoft Azure", "Docker",
                       "Kubernetes", "Terraform", "Linux", "Python"],
            "salary_range": (100000, 160000),
            "weight": 7,
        },
        "Data Engineer": {
            "skills": ["Python", "SQL", "Apache Spark", "ETL", "BigQuery",
                       "AWS", "Docker", "Airflow", "Snowflake"],
            "salary_range": (95000, 155000),
            "weight": 8,
        },
        "Cybersecurity Engineer": {
            "skills": ["Cybersecurity", "Linux", "Python", "Network Engineering",
                       "Security", "Cloud", "Penetration Testing"],
            "salary_range": (90000, 145000),
            "weight": 6,
        },
        "Full Stack Developer": {
            "skills": ["JavaScript", "Node.js", "React", "Python", "SQL", "MongoDB",
                       "REST API", "Git", "HTML/CSS"],
            "salary_range": (80000, 140000),
            "weight": 10,
        },
        "AI Engineer": {
            "skills": ["Python", "Deep Learning", "TensorFlow", "PyTorch", "NLP",
                       "Computer Vision", "LLM", "Machine Learning"],
            "salary_range": (110000, 175000),
            "weight": 7,
        },
        "Mobile Developer": {
            "skills": ["iOS Development", "Android Development", "Swift", "Kotlin",
                       "React Native", "Flutter", "Git"],
            "salary_range": (85000, 140000),
            "weight": 5,
        },
        "QA Engineer": {
            "skills": ["Testing/QA", "Selenium", "Python", "Java", "Git",
                       "CI/CD", "REST API"],
            "salary_range": (65000, 110000),
            "weight": 6,
        },
        "Product Manager": {
            "skills": ["Product Management", "Agile", "Scrum", "Data Analysis",
                       "SQL", "Jira"],
            "salary_range": (95000, 160000),
            "weight": 6,
        },
    }

    companies = [
        "TechCorp Inc.", "DataFlow Solutions", "CloudNine Systems", "ByteForge Labs",
        "Nexus Analytics", "Pinnacle Software", "Quantum Dynamics", "Apex Digital",
        "Vertex AI", "Crystal Software", "Synapse Tech", "Helix Data Systems",
        "Beacon Cloud", "Stratum Engineering", "Catalyst Labs", "Meridian AI",
        "Vanguard Software", "Polaris Data", "Atlas DevOps", "Zenith Analytics",
        "Lumen Systems", "Orbit Tech", "Cipher Security", "Forge AI Studio",
        "Datawave Inc.", "Sigma Engineering", "Mosaic AI", "Element Cloud",
    ]

    industries = ["Technology", "Financial Services / Fintech", "Healthcare / Healthtech",
                  "E-commerce / Retail", "Consulting", "Telecommunications",
                  "Manufacturing", "Education"]

    locations = ["San Francisco, CA", "New York, NY", "Seattle, WA", "Austin, TX",
                 "Boston, MA", "Chicago, IL", "Los Angeles, CA", "Denver, CO",
                 "Remote", "Atlanta, GA", "Portland, OR", "Washington, DC"]

    exp_levels = ["Entry", "Mid", "Senior", "Executive"]
    exp_weights = [0.20, 0.40, 0.30, 0.10]

    company_sizes = ["1-10", "11-50", "51-200", "201-500", "501-1000",
                     "1001-5000", "5001-10000", "10000+"]
    company_size_weights = [0.05, 0.10, 0.20, 0.20, 0.15, 0.15, 0.10, 0.05]

    titles = list(job_templates.keys())
    weights = [job_templates[t]["weight"] for t in titles]
    weights = np.array(weights) / sum(weights)

    rows = []
    for i in range(n):
        title = np.random.choice(titles, p=weights)
        template = job_templates[title]

        # Pilih 5-9 skill dari template
        n_skills = np.random.randint(5, min(10, len(template["skills"])+1))
        # Add slight variation - sometimes drop or add random skill
        base_skills = list(np.random.choice(template["skills"], n_skills, replace=False))

        # Salary based on template + experience modifier
        exp = np.random.choice(exp_levels, p=exp_weights)
        exp_mult = {"Entry": 0.7, "Mid": 1.0, "Senior": 1.3, "Executive": 1.6}[exp]
        sal_min, sal_max = template["salary_range"]
        med_salary = np.random.uniform(sal_min, sal_max) * exp_mult

        # Add seniority suffix
        if exp == "Senior" and not title.startswith("Senior"):
            title_full = f"Senior {title}"
        elif exp == "Entry":
            title_full = f"Junior {title}" if not title.startswith("Junior") else title
        else:
            title_full = title

        remote_allowed = int(np.random.random() < 0.45)

        rows.append({
            "job_id": f"job_{i:05d}",
            "title": title_full,
            "company_name": np.random.choice(companies),
            "location": np.random.choice(locations),
            "description": f"We're hiring a {title_full}. Required skills: {', '.join(base_skills)}. Join our team in a {exp.lower()} role.",
            "skills_list": base_skills,
            "industries": np.random.choice(industries),
            "experience_level": exp,
            "work_type": "Full-time",
            "med_salary": round(med_salary, 0),
            "min_salary": round(med_salary * 0.85, 0),
            "max_salary": round(med_salary * 1.15, 0),
            "remote_allowed": remote_allowed,
            "applies": int(np.random.exponential(50)),
            "views": int(np.random.exponential(200)),
            "company_size": np.random.choice(company_sizes, p=company_size_weights),
        })

    return pd.DataFrame(rows)


@st.cache_data(show_spinner=False)
def get_vocabulary_and_matrix(_df):
    """Build vocabulary dan skill matrix (cached)."""
    from .feature_engineering import build_skill_vocabulary, build_job_skill_matrix
    vocab = build_skill_vocabulary(_df, skill_col="skills_list", min_freq=5)
    matrix = build_job_skill_matrix(_df, vocab, skill_col="skills_list")
    return vocab, matrix


@st.cache_data(show_spinner=False)
def get_target_job_titles(_df, top_n=30):
    """Daftar target job titles untuk dropdown user."""
    # Group similar titles (drop "Junior", "Senior" prefix)
    titles = _df["title"].dropna().tolist()
    cleaned = []
    for t in titles:
        # Strip seniority prefix
        for prefix in ["Junior ", "Senior ", "Lead ", "Principal ", "Staff "]:
            if t.startswith(prefix):
                t = t[len(prefix):]
                break
        cleaned.append(t)

    from collections import Counter
    top = [t for t, _ in Counter(cleaned).most_common(top_n)]
    return sorted(set(top))

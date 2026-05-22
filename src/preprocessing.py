"""
Preprocessing Module — LinkedIn Job Postings (arshkon dataset)
"""

import pandas as pd
import numpy as np
import re
from pathlib import Path

PROJECT_ROOT  = Path(__file__).parent.parent
RAW_DIR       = PROJECT_ROOT / "data" / "raw"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"

# Strict IT keywords — avoid civil/mechanical/structural engineers
IT_TITLE_INCLUDE = [
    "software", "data ", "machine learning", "artificial intelligence",
    "cloud", "devops", "devsecops", "site reliability", "sre",
    "backend", "back end", "back-end", "frontend", "front end", "front-end",
    "full stack", "fullstack", "full-stack",
    "cybersecurity", "security engineer", "infosec",
    "database administrator", "dba",
    "network engineer", "systems engineer", "system engineer",
    "qa engineer", "quality assurance", "automation engineer",
    "mobile developer", "ios developer", "android developer",
    "computer scientist", "it manager", "it director",
    "product manager", "technical program", "engineering manager",
    "python", "java developer", "javascript developer",
    "react developer", "node developer", "angular developer",
    "salesforce developer", "salesforce engineer",
    "platform engineer", "infrastructure engineer",
    "data scientist", "data analyst", "data engineer", "analytics engineer",
    "ml engineer", "ai engineer", "nlp engineer",
    "business intelligence", "bi developer",
    "wordpress", "php developer", "ruby developer",
]

IT_TITLE_EXCLUDE = [
    "civil engineer", "structural engineer", "mechanical engineer",
    "electrical engineer", "chemical engineer", "aerospace engineer",
    "environmental engineer", "geotechnical", "hvac", "plumbing",
    "building engineer", "facilities engineer", "manufacturing engineer",
    "process engineer", "plant engineer", "field engineer",
    "sales engineer", "solutions engineer", "presales",
    "project architect", "licensed architect", "architectural",
    "social security", "behavior analyst", "financial analyst",
    "fp&a", "credit analyst", "risk analyst", "compliance analyst",
]

EXPERIENCE_LEVEL_MAP = {
    "Internship": "Internship", "Entry level": "Entry",
    "Associate": "Entry", "Mid-Senior level": "Mid",
    "Director": "Senior", "Executive": "Executive",
    "EN": "Entry", "MI": "Mid", "SE": "Senior", "EX": "Executive",
}

SKILL_CANONICAL = {
    "python": "Python", "sql": "SQL", "java": "Java",
    "javascript": "JavaScript", "typescript": "TypeScript",
    "c++": "C++", "c#": "C#", "golang": "Go", "php": "PHP",
    "ruby": "Ruby", "scala": "Scala", "kotlin": "Kotlin",
    "swift": "Swift", "rust": "Rust", "bash": "Bash",
    "r programming": "R",
    "r language": "R",
    "proficiency in r": "R",
    "rstudio": "R",
    "tidyverse": "R",
    "ggplot": "R",
    "dplyr": "R",
    "machine learning": "Machine Learning",
    "deep learning": "Deep Learning",
    "natural language processing": "NLP",
    "computer vision": "Computer Vision",
    "tensorflow": "TensorFlow", "pytorch": "PyTorch",
    "keras": "Keras", "scikit-learn": "Scikit-learn",
    "nlp": "NLP", "llm": "LLM", "mlops": "MLOps",
    "xgboost": "XGBoost", "a/b testing": "A/B Testing",
    "data analysis": "Data Analysis", "data science": "Data Science",
    "data engineering": "Data Engineering",
    "statistics": "Statistics", "pandas": "Pandas", "numpy": "NumPy",
    "apache spark": "Apache Spark", "hadoop": "Hadoop",
    "etl": "ETL", "data warehouse": "Data Warehouse",
    "bigquery": "BigQuery", "snowflake": "Snowflake",
    "dbt": "dbt", "airflow": "Airflow", "kafka": "Kafka",
    "tableau": "Tableau", "power bi": "Power BI",
    "looker": "Looker", "excel": "Excel",
    "aws": "AWS", "google cloud platform": "Google Cloud Platform",
    "microsoft azure": "Microsoft Azure",
    "docker": "Docker", "kubernetes": "Kubernetes",
    "terraform": "Terraform", "ansible": "Ansible",
    "jenkins": "Jenkins", "ci/cd": "CI/CD", "linux": "Linux",
    "git": "Git", "github actions": "GitHub Actions",
    "react": "React", "vue.js": "Vue.js", "angular": "Angular",
    "node.js": "Node.js", "django": "Django", "flask": "Flask",
    "fastapi": "FastAPI", "spring boot": "Spring Boot",
    "rest api": "REST API", "graphql": "GraphQL",
    "react native": "React Native", "flutter": "Flutter",
    "ios": "iOS Development", "android": "Android Development",
    "mysql": "MySQL", "postgresql": "PostgreSQL",
    "mongodb": "MongoDB", "redis": "Redis",
    "elasticsearch": "Elasticsearch", "cassandra": "Cassandra",
    "oracle": "Oracle", "dynamodb": "DynamoDB",
    "cybersecurity": "Cybersecurity",
    "penetration testing": "Penetration Testing",
    "agile": "Agile", "scrum": "Scrum", "jira": "Jira",
    "product management": "Product Management",
    "figma": "Figma", "system design": "System Design",
    "microservices": "Microservices", "salesforce": "Salesforce",
}

TECH_SKILLS = list(SKILL_CANONICAL.keys())


def is_it_job(title: str) -> bool:
    if not isinstance(title, str):
        return False
    t = title.lower()
    # Exclude first — strict exclusions
    if any(ex in t for ex in IT_TITLE_EXCLUDE):
        return False
    # Then include
    return any(kw in t for kw in IT_TITLE_INCLUDE)


def extract_skills_from_description(description: str) -> list:
    if not isinstance(description, str) or len(description) < 30:
        return []
    text = description.lower()
    # Normalize variants
    text = re.sub(r'\bnode\.?js\b', 'node.js', text)
    text = re.sub(r'\bpostgres(ql)?\b', 'postgresql', text)
    text = re.sub(r'\bscikit[\s\-]learn\b', 'scikit-learn', text)
    text = re.sub(r'\bgcp\b', 'google cloud platform', text)
    text = re.sub(r'\bazure\b', 'microsoft azure', text)
    text = re.sub(r'\bamz|amazon web services\b', 'aws', text)
    text = re.sub(r'\bvue\.?js\b', 'vue.js', text)
    text = re.sub(r'\bspring[\s\-]boot\b', 'spring boot', text)

    found = []
    for skill in TECH_SKILLS:
        if re.search(r'\b' + re.escape(skill) + r'\b', text):
            canonical = SKILL_CANONICAL.get(skill, skill.title())
            if canonical not in found:
                found.append(canonical)
    return found


def normalize_salary_to_yearly(df):
    if "pay_period" not in df.columns:
        return df
    mult = {"HOURLY": 2080, "MONTHLY": 12, "YEARLY": 1, "WEEKLY": 52}
    for col in ["max_salary", "min_salary", "med_salary"]:
        if col not in df.columns:
            continue
        df[col] = pd.to_numeric(df[col], errors="coerce")
        for period, m in mult.items():
            mask = (df["pay_period"] == period) & df[col].notna()
            df.loc[mask, col] = df.loc[mask, col] * m
        df.loc[df[col] < 10000,   col] = np.nan
        df.loc[df[col] > 1000000, col] = np.nan
    if "min_salary" in df.columns and "max_salary" in df.columns:
        df["med_salary"] = df[["min_salary", "max_salary"]].mean(axis=1)
    return df


def handle_missing_salary(df):
    """
    Normalize salary values only — do NOT fill missing with median.
    95% of LinkedIn jobs have no salary data; filling would fabricate data.
    Charts will show only jobs that actually have salary info.
    """
    if "med_salary" not in df.columns:
        return df
    df["med_salary"] = pd.to_numeric(df["med_salary"], errors="coerce")
    # Only keep reasonable yearly salaries (already normalized by normalize_salary_to_yearly)
    # Values outside $15k-$800k are likely errors
    df.loc[df["med_salary"] < 15000, "med_salary"] = np.nan
    df.loc[df["med_salary"] > 800000, "med_salary"] = np.nan
    return df


def normalize_experience_level(df, col="formatted_experience_level"):
    if col not in df.columns:
        return df
    df["experience_level"] = df[col].map(EXPERIENCE_LEVEL_MAP).fillna("Mid")
    return df


def normalize_work_type(df, col="formatted_work_type"):
    if col in df.columns:
        df["work_type"] = df[col].fillna("Full-time")
    return df


def load_arshkon_dataset():
    postings_path = RAW_DIR / "postings.csv"
    if not postings_path.exists():
        raise FileNotFoundError(f"postings.csv not found in {RAW_DIR}")
    df = pd.read_csv(postings_path, low_memory=False)
    print(f"  Loaded {len(df):,} raw postings")

    # company_name is already in postings.csv — just ensure it's there
    # Supplement company_size from companies.csv if available
    companies_path = RAW_DIR / "companies.csv"
    if companies_path.exists() and "company_size" not in df.columns:
        companies = pd.read_csv(companies_path, low_memory=False,
                                usecols=["company_id", "company_size"])
        df = df.merge(companies, on="company_id", how="left")

    return df


def preprocess_full_pipeline():
    print("Loading dataset...")
    df = load_arshkon_dataset()

    print("Normalizing experience level...")
    df = normalize_experience_level(df)

    print("Filtering IT jobs (strict)...")
    df = df[df["title"].apply(is_it_job)].reset_index(drop=True)
    print(f"  After filter: {len(df):,} jobs")

    print("Extracting technical skills from descriptions...")
    df["skills_list"] = df["description"].apply(extract_skills_from_description)
    n = (df["skills_list"].apply(len) > 0).sum()
    print(f"  Jobs with ≥1 skill: {n:,} ({n/len(df)*100:.0f}%)")

    print("Normalizing salary to yearly USD...")
    df = normalize_salary_to_yearly(df)

    print("Filling missing salary...")
    df = handle_missing_salary(df)

    df = normalize_work_type(df)

    keep_cols = [
        "job_id", "title", "company_name", "description", "location",
        "skills_list", "experience_level", "work_type",
        "med_salary", "min_salary", "max_salary",
        "remote_allowed", "applies", "views", "company_size",
    ]
    df = df[[c for c in keep_cols if c in df.columns]]

    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    out = PROCESSED_DIR / "jobs_clean.csv"
    df.to_csv(out, index=False)
    print(f"Saved {len(df):,} rows → {out}")
    return df


if __name__ == "__main__":
    preprocess_full_pipeline()
"""
Preprocessing Module
====================
Bertanggung jawab untuk:
- Loading raw data dari folder data/raw/
- Merging multiple LinkedIn dataset files
- Cleaning, filtering IT domain, handling missing values
- Output: data/processed/jobs_clean.csv

Dataset yang digunakan:
1. arshkon/linkedin-job-postings: postings.csv, job_skills.csv,
   job_industries.csv, companies.csv
2. asaniczka/data-science-job-postings-and-skills: job_postings.csv
"""

import pandas as pd
import numpy as np
import os
from pathlib import Path

# ===== Path Configuration =====
PROJECT_ROOT = Path(__file__).parent.parent
RAW_DIR = PROJECT_ROOT / "data" / "raw"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"

# ===== IT Domain Keywords =====
IT_KEYWORDS = [
    "data", "engineer", "developer", "software", "programmer",
    "machine learning", "ml ", "artificial intelligence", "ai ",
    "cloud", "devops", "analyst", "scientist", "architect",
    "backend", "frontend", "full stack", "fullstack", "full-stack",
    "qa", "tester", "security", "cyber", "network",
    "database", "dba", "system admin", "sysadmin", "site reliability",
    "ui/ux", "product manager", "technical", "it ", "information technology"
]

EXPERIENCE_LEVEL_MAP = {
    "Internship": "Internship",
    "Entry level": "Entry",
    "Associate": "Entry",
    "Mid-Senior level": "Mid",
    "Director": "Senior",
    "Executive": "Executive",
    "EN": "Entry",
    "MI": "Mid",
    "SE": "Senior",
    "EX": "Executive",
}


def is_it_job(title):
    """Cek apakah job title termasuk domain IT."""
    if not isinstance(title, str):
        return False
    title_lower = title.lower()
    return any(keyword in title_lower for keyword in IT_KEYWORDS)


def load_arshkon_dataset():
    """Load dan merge file-file dataset arshkon."""
    postings_path = RAW_DIR / "postings.csv"
    job_skills_path = RAW_DIR / "job_skills.csv"
    job_industries_path = RAW_DIR / "job_industries.csv"
    companies_path = RAW_DIR / "companies.csv"

    postings = pd.read_csv(postings_path, low_memory=False)

    # Merge job skills (one job can have multiple skills)
    if job_skills_path.exists():
        skills = pd.read_csv(job_skills_path)
        # Aggregate skills per job_id into list
        skills_grouped = skills.groupby("job_id")["skill_abr"].apply(
            lambda x: ",".join(x.dropna().astype(str))
        ).reset_index()
        skills_grouped.columns = ["job_id", "skills_abr"]
        postings = postings.merge(skills_grouped, on="job_id", how="left")

    # Merge industries
    if job_industries_path.exists():
        industries = pd.read_csv(job_industries_path)
        ind_grouped = industries.groupby("job_id")["industry_id"].apply(
            lambda x: ",".join(x.dropna().astype(str))
        ).reset_index()
        ind_grouped.columns = ["job_id", "industries"]
        postings = postings.merge(ind_grouped, on="job_id", how="left")

    # Merge company info
    if companies_path.exists():
        companies = pd.read_csv(companies_path)
        keep_cols = ["company_id", "name", "company_size"]
        keep_cols = [c for c in keep_cols if c in companies.columns]
        companies = companies[keep_cols].rename(columns={
            "name": "company_name",
        })
        postings = postings.merge(companies, on="company_id", how="left")

    return postings


def load_asaniczka_dataset():
    """Load dataset asaniczka sebagai supplementary."""
    path = RAW_DIR / "data_science_jobs.csv"
    if not path.exists():
        # Try alternative filenames
        alternatives = ["job_postings.csv", "ds_jobs.csv"]
        for alt in alternatives:
            if (RAW_DIR / alt).exists():
                path = RAW_DIR / alt
                break
        else:
            return None
    return pd.read_csv(path, low_memory=False)


def clean_skills_column(df, skills_col="skills"):
    """Bersihkan dan standardisasi kolom skills."""
    def parse_skills(x):
        if pd.isna(x):
            return []
        if isinstance(x, list):
            return [s.strip() for s in x if s]
        # Try parse as comma-separated string
        return [s.strip() for s in str(x).split(",") if s.strip()]

    df["skills_list"] = df[skills_col].apply(parse_skills)
    return df


def filter_it_jobs(df, title_col="title"):
    """Filter hanya job IT berdasarkan title."""
    if title_col not in df.columns:
        return df
    mask = df[title_col].apply(is_it_job)
    return df[mask].reset_index(drop=True)


def handle_missing_salary(df):
    """Isi missing salary dengan median per title + experience."""
    salary_cols = ["max_salary", "min_salary", "med_salary"]
    salary_cols = [c for c in salary_cols if c in df.columns]

    if not salary_cols:
        return df

    # Use median salary if not present
    if "med_salary" not in df.columns and "min_salary" in df.columns and "max_salary" in df.columns:
        df["med_salary"] = (df["min_salary"] + df["max_salary"]) / 2

    if "med_salary" in df.columns:
        df["med_salary"] = df.groupby(["title"])["med_salary"].transform(
            lambda x: x.fillna(x.median())
        )
        df["med_salary"] = df["med_salary"].fillna(df["med_salary"].median())

    return df


def normalize_experience_level(df, col="formatted_experience_level"):
    """Normalisasi experience level ke kategori standar."""
    if col not in df.columns:
        return df
    df["experience_level"] = df[col].map(EXPERIENCE_LEVEL_MAP).fillna("Mid")
    return df


def normalize_work_type(df, col="formatted_work_type"):
    """Normalisasi work type."""
    if col in df.columns:
        df["work_type"] = df[col].fillna("Full-time")
    return df


def preprocess_full_pipeline():
    """
    Pipeline lengkap preprocessing:
    Load → Merge → Filter IT → Clean → Save
    """
    # Step 1: Load arshkon
    print("Loading arshkon dataset...")
    df = load_arshkon_dataset()
    print(f"  Loaded {len(df)} job postings")

    # Step 2: Filter IT jobs
    print("Filtering IT domain...")
    df = filter_it_jobs(df, title_col="title")
    print(f"  After IT filter: {len(df)} jobs")

    # Step 3: Clean skills
    if "skills_abr" in df.columns:
        df = clean_skills_column(df, skills_col="skills_abr")

    # Step 4: Handle missing salary
    print("Handling missing salary...")
    df = handle_missing_salary(df)

    # Step 5: Normalize categorical fields
    df = normalize_experience_level(df)
    df = normalize_work_type(df)

    # Step 6: Drop irrelevant columns to reduce size
    keep_cols = [
        "job_id", "title", "company_name", "description", "location",
        "skills_list", "industries", "experience_level", "work_type",
        "med_salary", "min_salary", "max_salary",
        "remote_allowed", "applies", "views", "company_size"
    ]
    keep_cols = [c for c in keep_cols if c in df.columns]
    df = df[keep_cols]

    # Step 7: Save processed
    output_path = PROCESSED_DIR / "jobs_clean.csv"
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)
    print(f"Saved cleaned data to {output_path}")
    return df


if __name__ == "__main__":
    preprocess_full_pipeline()

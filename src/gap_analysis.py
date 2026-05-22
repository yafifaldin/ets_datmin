"""
Gap Analysis Module
===================
Bertanggung jawab untuk:
- Membandingkan skill user dengan skill requirement target job
- Menghitung match score dan list skill yang kurang
- Memprioritaskan gap berdasarkan frekuensi skill di dataset
"""

import pandas as pd
import numpy as np
from collections import Counter
from .feature_engineering import parse_skills_list, normalize_skill_name


def skill_overlap(user_skills, job_skills):
    """
    Hitung overlap antara skill user dan skill job.

    Returns:
        dict berisi: matched, missing, match_percentage
    """
    user_set = set(normalize_skill_name(s) for s in user_skills if s)
    job_set = set(normalize_skill_name(s) for s in job_skills if s)

    matched = sorted(user_set & job_set)
    missing = sorted(job_set - user_set)
    extra = sorted(user_set - job_set)

    if len(job_set) == 0:
        match_pct = 0.0
    else:
        match_pct = len(matched) / len(job_set) * 100

    return {
        "matched": matched,
        "missing": missing,
        "extra": extra,
        "match_percentage": round(match_pct, 1),
        "n_required": len(job_set),
        "n_have": len(matched),
    }


def gap_to_target_job(user_skills, target_title, df, skill_col="skills_list"):
    """
    Gap analysis terhadap target job tertentu.
    Aggregate skill requirements dari semua job dengan title serupa.

    Returns:
        dict dengan info gap dan skill yang prioritas untuk dipelajari
    """
    # Filter job dengan title yang mengandung target_title
    target_lower = target_title.lower()
    mask = df["title"].fillna("").str.lower().str.contains(target_lower, na=False)
    target_jobs = df[mask]

    if len(target_jobs) == 0:
        return {
            "found": False,
            "n_jobs_found": 0,
            "matched": [],
            "missing": [],
            "match_percentage": 0,
            "skill_priority": [],
        }

    # Aggregate skill frequency from target jobs
    skill_counter = Counter()
    n_jobs = len(target_jobs)

    for skills in target_jobs[skill_col]:
        parsed = parse_skills_list(skills)
        normalized = [normalize_skill_name(s) for s in parsed if s]
        skill_counter.update(set(normalized))  # set untuk hitung di berapa banyak job

    # Skill requirement = skill yang muncul di > 30% job target
    threshold = max(1, int(n_jobs * 0.2))
    required_skills = {s for s, freq in skill_counter.items() if freq >= threshold}

    overlap = skill_overlap(user_skills, list(required_skills))

    # Priority skill: skill yang kurang, diurutkan dari yang paling sering muncul
    priority = []
    for skill in overlap["missing"]:
        freq = skill_counter.get(skill, 0)
        pct = round(freq / n_jobs * 100, 1)
        priority.append({
            "skill": skill,
            "demand_pct": pct,
            "demand_count": freq,
        })
    priority.sort(key=lambda x: x["demand_pct"], reverse=True)

    return {
        "found": True,
        "n_jobs_found": n_jobs,
        "target_title": target_title,
        "matched": overlap["matched"],
        "missing": overlap["missing"],
        "match_percentage": overlap["match_percentage"],
        "skill_priority": priority,
    }


def compute_market_skill_frequency(df, skill_col="skills_list", top_n=20):
    """
    Hitung skill paling sering muncul di seluruh dataset.

    Returns:
        DataFrame dengan kolom 'skill' dan 'frequency_pct'
    """
    skill_counter = Counter()
    n_jobs = len(df)

    for skills in df[skill_col]:
        parsed = parse_skills_list(skills)
        normalized = set(normalize_skill_name(s) for s in parsed if s)
        skill_counter.update(normalized)

    data = [
        {"skill": s, "count": c, "frequency_pct": round(c / n_jobs * 100, 1)}
        for s, c in skill_counter.most_common(top_n)
    ]
    return pd.DataFrame(data)
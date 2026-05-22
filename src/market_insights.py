"""
Market Insights Module
======================
Bertanggung jawab untuk analisis deskriptif dari dataset:
- Skill paling sering dicari pasar
- Distribusi salary per job title
- Tren remote vs on-site
- Top hiring companies
- Distribusi experience level
"""

import pandas as pd
import numpy as np
from .feature_engineering import parse_skills_list, normalize_skill_name


def salary_distribution(df, salary_col="med_salary"):
    """
    Statistik distribusi salary.

    Returns:
        dict dengan median, mean, q1, q3, min, max
    """
    # Try med_salary first, fallback to max_salary
    if salary_col not in df.columns or df[salary_col].dropna().eq(0).all():
        for alt in ["max_salary", "min_salary"]:
            if alt in df.columns and df[alt].dropna().gt(0).any():
                salary_col = alt
                break
    if salary_col not in df.columns:
        return None
    salary = df[salary_col].dropna()
    salary = salary[salary > 0]  # exclude zeros
    if len(salary) == 0:
        return None
    return {
        "median": float(salary.median()),
        "mean": float(salary.mean()),
        "q1": float(salary.quantile(0.25)),
        "q3": float(salary.quantile(0.75)),
        "min": float(salary.min()),
        "max": float(salary.max()),
        "count": int(len(salary)),
    }


def salary_by_title(df, salary_col="med_salary", title_col="title", top_n=15):
    """
    Salary median per job title yang paling banyak posting.

    Returns:
        DataFrame [title, median_salary, count]
    """
    if salary_col not in df.columns or title_col not in df.columns:
        return pd.DataFrame()

    # Get top N most common titles first
    top_titles = df[title_col].value_counts().head(top_n).index
    subset = df[df[title_col].isin(top_titles)]

    agg = subset.groupby(title_col).agg(
        median_salary=(salary_col, "median"),
        count=(salary_col, "size"),
    ).reset_index()
    agg = agg.dropna(subset=["median_salary"]).sort_values("median_salary", ascending=False)
    return agg


def salary_by_experience(df, salary_col="med_salary", exp_col="experience_level"):
    """Salary median per experience level."""
    if salary_col not in df.columns or exp_col not in df.columns:
        return pd.DataFrame()
    agg = df.groupby(exp_col).agg(
        median_salary=(salary_col, "median"),
        count=(salary_col, "size"),
    ).reset_index()
    agg = agg.dropna(subset=["median_salary"])

    # Order experience levels logically
    order = ["Internship", "Entry", "Mid", "Senior", "Executive"]
    agg["_order"] = agg[exp_col].apply(lambda x: order.index(x) if x in order else 99)
    agg = agg.sort_values("_order").drop(columns=["_order"]).reset_index(drop=True)
    return agg


def remote_distribution(df, remote_col="remote_allowed", work_type_col="work_type"):
    """Distribusi remote vs on-site."""
    result = {}
    if remote_col in df.columns:
        total = len(df)
        remote_count = (df[remote_col].fillna(0).astype(float) == 1).sum()
        result["remote_pct"] = round(remote_count / total * 100, 1) if total else 0
        result["onsite_pct"] = round((total - remote_count) / total * 100, 1) if total else 0
        result["remote_count"] = int(remote_count)
        result["onsite_count"] = int(total - remote_count)

    if work_type_col in df.columns:
        wt_dist = df[work_type_col].value_counts(normalize=True) * 100
        result["work_type_dist"] = wt_dist.round(1).to_dict()

    return result


def experience_level_distribution(df, exp_col="experience_level"):
    """Distribusi experience level."""
    if exp_col not in df.columns:
        return pd.DataFrame()

    dist = df[exp_col].value_counts(normalize=True) * 100
    dist = dist.round(1).reset_index()
    dist.columns = ["experience_level", "percentage"]

    order = ["Internship", "Entry", "Mid", "Senior", "Executive"]
    dist["_order"] = dist["experience_level"].apply(
        lambda x: order.index(x) if x in order else 99
    )
    dist = dist.sort_values("_order").drop(columns=["_order"]).reset_index(drop=True)
    return dist


def top_companies(df, company_col="company_name", top_n=10):
    """Top hiring companies berdasarkan jumlah posting."""
    if company_col not in df.columns:
        return pd.DataFrame()
    top = df[company_col].value_counts().head(top_n).reset_index()
    top.columns = ["company", "n_postings"]
    return top


def top_skills_for_title(df, target_title, skill_col="skills_list",
                         title_col="title", top_n=15):
    """
    Skill paling dicari untuk target job title tertentu.
    """
    from collections import Counter

    target_lower = target_title.lower()
    mask = df[title_col].fillna("").str.lower().str.contains(target_lower, na=False)
    subset = df[mask]
    n_jobs = len(subset)
    if n_jobs == 0:
        return pd.DataFrame(), 0

    counter = Counter()
    for skills in subset[skill_col]:
        parsed = parse_skills_list(skills)
        normalized = set(normalize_skill_name(s) for s in parsed if s)
        counter.update(normalized)

    data = [
        {"skill": s, "count": c, "frequency_pct": round(c / n_jobs * 100, 1)}
        for s, c in counter.most_common(top_n)
    ]
    return pd.DataFrame(data), n_jobs


def applies_views_summary(df):
    """Summary applies dan views per job."""
    result = {}
    for col in ["applies", "views"]:
        if col in df.columns:
            data = df[col].dropna()
            if len(data) > 0:
                result[f"avg_{col}"] = float(data.mean())
                result[f"median_{col}"] = float(data.median())
                result[f"total_{col}"] = int(data.sum())
    return result

# Re-export for convenience
from .gap_analysis import compute_market_skill_frequency
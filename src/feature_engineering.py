"""
Feature Engineering Module
==========================
Bertanggung jawab untuk:
- Membangun skill vocabulary dari seluruh dataset
- Mengkonversi job dataset menjadi binary skill matrix
- Mengkonversi user input menjadi user profile vector
- TF-IDF representation dari job description
"""

import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from scipy.sparse import csr_matrix, hstack
import ast


def parse_skills_list(x):
    """Parse skills_list column yang mungkin tersimpan sebagai string."""
    if isinstance(x, list):
        return x
    if pd.isna(x):
        return []
    if isinstance(x, str):
        try:
            parsed = ast.literal_eval(x)
            if isinstance(parsed, list):
                return parsed
        except (ValueError, SyntaxError):
            pass
        return [s.strip() for s in x.split(",") if s.strip()]
    return []


def normalize_skill_name(skill):
    """Standardisasi nama skill (lowercase, trim, alias mapping)."""
    if not isinstance(skill, str):
        return ""
    skill = skill.strip().lower()

    # Alias mapping untuk variasi nama yang sama
    aliases = {
        "ml": "machine learning",
        "ai": "artificial intelligence",
        "js": "javascript",
        "ts": "typescript",
        "nlp": "natural language processing",
        "cv": "computer vision",
        "k8s": "kubernetes",
        "gcp": "google cloud platform",
        "aws cloud": "aws",
        "sql server": "microsoft sql server",
        "postgres": "postgresql",
        "mongo": "mongodb",
    }
    return aliases.get(skill, skill)


def build_skill_vocabulary(df, skill_col="skills_list", min_freq=10):
    """
    Bangun vocabulary skill dari seluruh dataset.

    Args:
        df: DataFrame berisi kolom skills_list
        skill_col: nama kolom yang berisi list skill
        min_freq: minimum frekuensi skill untuk dimasukkan vocabulary

    Returns:
        list of unique skills (sorted alphabetically)
    """
    from collections import Counter

    all_skills = []
    for skills in df[skill_col]:
        parsed = parse_skills_list(skills)
        normalized = [normalize_skill_name(s) for s in parsed]
        all_skills.extend([s for s in normalized if s])

    counter = Counter(all_skills)
    vocab = sorted([skill for skill, freq in counter.items() if freq >= min_freq])
    return vocab


def build_job_skill_matrix(df, vocabulary, skill_col="skills_list"):
    """
    Konversi setiap job menjadi binary vector berdasarkan vocabulary.

    Returns:
        numpy array shape (n_jobs, n_skills)
    """
    n_jobs = len(df)
    n_skills = len(vocabulary)
    skill_to_idx = {s: i for i, s in enumerate(vocabulary)}

    matrix = np.zeros((n_jobs, n_skills), dtype=np.int8)

    for i, skills in enumerate(df[skill_col]):
        parsed = parse_skills_list(skills)
        for s in parsed:
            normalized = normalize_skill_name(s)
            if normalized in skill_to_idx:
                matrix[i, skill_to_idx[normalized]] = 1

    return matrix


def build_user_vector(user_skills, vocabulary):
    """
    Konversi pilihan skill user menjadi binary vector.

    Args:
        user_skills: list of skill strings yang dipilih user
        vocabulary: skill vocabulary global

    Returns:
        numpy array shape (1, n_skills)
    """
    skill_to_idx = {s: i for i, s in enumerate(vocabulary)}
    vec = np.zeros((1, len(vocabulary)), dtype=np.int8)

    for s in user_skills:
        normalized = normalize_skill_name(s)
        if normalized in skill_to_idx:
            vec[0, skill_to_idx[normalized]] = 1

    return vec


def build_tfidf_matrix(df, text_col="description", max_features=300):
    """
    Bangun TF-IDF matrix dari kolom deskripsi job.

    Returns:
        sparse matrix, vectorizer object
    """
    texts = df[text_col].fillna("").astype(str)
    vectorizer = TfidfVectorizer(
        max_features=max_features,
        stop_words="english",
        ngram_range=(1, 2),
        min_df=5,
        max_df=0.85
    )
    matrix = vectorizer.fit_transform(texts)
    return matrix, vectorizer


def transform_user_query_tfidf(user_skills, user_keywords, vectorizer):
    """
    Konversi user skills dan keywords ke TF-IDF vector menggunakan
    vectorizer yang sudah di-fit dari dataset.
    """
    query_text = " ".join(user_skills + (user_keywords or []))
    return vectorizer.transform([query_text])


def combine_features(skill_matrix, tfidf_matrix, alpha=0.7):
    """
    Gabungkan binary skill matrix dengan TF-IDF matrix.

    alpha: bobot untuk skill matrix (1-alpha untuk TF-IDF)
    """
    skill_sparse = csr_matrix(skill_matrix.astype(float) * alpha)
    tfidf_weighted = tfidf_matrix * (1 - alpha)
    combined = hstack([skill_sparse, tfidf_weighted])
    return combined

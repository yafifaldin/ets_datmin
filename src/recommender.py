"""
Recommender Module (Content-Based Filtering)
============================================
Bertanggung jawab untuk:
- Menghitung cosine similarity antara user profile vector dan job-skill matrix
- Menerapkan filter preferensi user (work_type, experience, salary)
- Mengembalikan top-N rekomendasi job dengan match score
"""

import numpy as np
import pandas as pd


def compute_similarity(user_vector, job_matrix):
    """
    Hitung skill match score antara user profile dan setiap job.

    Menggunakan ASYMMETRIC COVERAGE score yang lebih intuitif daripada
    cosine similarity murni:

        score = 0.7 * coverage + 0.3 * cosine

    - coverage = matched_skills / job_skills_required
      (seberapa banyak kebutuhan job yang user cover)
    - cosine   = cosine similarity standar
      (untuk tetap menangkap partial overlap dan dipakai sebagai tie-breaker)

    Kenapa tidak cosine murni?
    Cosine similarity pada binary vector menormalisasi panjang kedua vector,
    sehingga user dengan 2/5 skill match job menghasilkan 63.2%, yang terasa
    misleading karena sebenarnya hanya cover 40% kebutuhan job.
    Asymmetric coverage lebih mencerminkan "seberapa siap kamu untuk job ini".

    Args:
        user_vector: numpy array shape (1, n_skills)
        job_matrix : numpy array shape (n_jobs, n_skills)

    Returns:
        numpy array shape (n_jobs,) berisi score 0.0–1.0
    """
    import numpy as np
    from sklearn.metrics.pairwise import cosine_similarity as _cosine

    u = np.asarray(user_vector, dtype=float)
    J = np.asarray(job_matrix, dtype=float)

    # Cosine similarity (shape: n_jobs,)
    cosine = _cosine(u, J).flatten()

    # Coverage = dot(u, j) / sum(j)  →  matched / required
    dot = J @ u.flatten()                  # (n_jobs,)
    job_norms = J.sum(axis=1)              # total skills required per job
    with np.errstate(divide="ignore", invalid="ignore"):
        coverage = np.where(job_norms > 0, dot / job_norms, 0.0)

    return 0.7 * coverage + 0.3 * cosine


def apply_preference_filter(df, scores, preferences):
    """
    Terapkan filter preferensi user pada similarity scores.
    Job yang tidak match preference dapat penalty (bukan dihapus,
    supaya tetap muncul tapi ranking lebih rendah).

    preferences dict berisi:
        - experience_level: str ('Entry', 'Mid', 'Senior', 'Executive', 'Any')
        - work_type: str ('Remote', 'On-site', 'Hybrid', 'Any')
        - industry: str (matches df["industries"] value, or 'Any')
        - company_size: str (matches df["company_size"] bucket, or 'Any')
        - min_salary: float (USD)
        - max_salary: float (USD)
    """
    scores = scores.copy()

    # --- Experience level (soft penalty) ---
    exp = preferences.get("experience_level")
    if exp and exp != "Any" and "experience_level" in df.columns:
        mask = df["experience_level"] != exp
        scores[mask.values] *= 0.7  # 30% penalty kalau tidak match

    # --- Work type (Remote / On-site / Hybrid) ---
    wt = preferences.get("work_type")
    if wt and wt != "Any" and "remote_allowed" in df.columns:
        remote_flag = df["remote_allowed"].fillna(0).astype(float) == 1
        if wt == "Remote":
            scores[(~remote_flag).values] *= 0.7
        elif wt == "On-site":
            scores[remote_flag.values] *= 0.7
        elif wt == "Hybrid":
            # Hybrid: kita anggap remote_allowed=1 sebagai possible hybrid,
            # tapi tidak ada penalty kuat karena banyak listing tidak eksplisit
            pass

    # --- Industry (soft penalty if mismatch) ---
    ind = preferences.get("industry")
    if ind and ind != "Any" and "industries" in df.columns:
        ind_str = df["industries"].fillna("").astype(str)
        mask = ~ind_str.str.contains(ind, case=False, na=False, regex=False)
        scores[mask.values] *= 0.8

    # --- Company size (soft penalty if mismatch) ---
    size_pref = preferences.get("company_size")
    if size_pref and size_pref != "Any" and "company_size" in df.columns:
        # Map form options to size bucket ranges
        size_bucket_map = {
            "Startup (1-50)": ["1-10", "11-50"],
            "Mid-size (51-500)": ["51-200", "201-500"],
            "Large (501-5000)": ["501-1000", "1001-5000"],
            "Enterprise (5000+)": ["5001-10000", "10000+"],
        }
        allowed = size_bucket_map.get(size_pref, [])
        if allowed:
            cs = df["company_size"].fillna("").astype(str)
            mask = ~cs.isin(allowed)
            scores[mask.values] *= 0.85

    # --- Salary range (soft penalty if outside) ---
    target_min = preferences.get("min_salary")
    target_max = preferences.get("max_salary")
    if target_min is not None and "med_salary" in df.columns:
        salary = df["med_salary"].fillna(0).astype(float)
        below_mask = (salary < target_min * 0.8)
        scores[below_mask.values] *= 0.6
    if target_max is not None and "med_salary" in df.columns:
        salary = df["med_salary"].fillna(0).astype(float)
        above_mask = (salary > target_max * 1.3)
        scores[above_mask.values] *= 0.85

    return scores


def get_top_recommendations(df, scores, top_n=10):
    """
    Ambil top-N job berdasarkan similarity scores.

    Returns:
        DataFrame top-N job dengan kolom tambahan 'match_score' (0-100)
    """
    df = df.copy()
    df["match_score"] = (scores * 100).round(1)
    df_sorted = df.sort_values("match_score", ascending=False).head(top_n)
    return df_sorted.reset_index(drop=True)


def recommend_for_user(user_skills, df, vocabulary, job_matrix,
                       preferences=None, top_n=10,
                       user_vector_builder=None):
    """
    Pipeline lengkap rekomendasi.

    Args:
        user_skills: list of skill strings
        df: job DataFrame
        vocabulary: skill vocabulary
        job_matrix: precomputed binary skill matrix
        preferences: dict preferensi user (optional)
        top_n: jumlah rekomendasi
        user_vector_builder: fungsi untuk build user vector
            (di-pass untuk hindari circular import)

    Returns:
        top-N DataFrame
    """
    if user_vector_builder is None:
        from .feature_engineering import build_user_vector
        user_vector_builder = build_user_vector

    user_vec = user_vector_builder(user_skills, vocabulary)
    scores = compute_similarity(user_vec, job_matrix)

    if preferences:
        scores = apply_preference_filter(df, scores, preferences)

    return get_top_recommendations(df, scores, top_n=top_n)

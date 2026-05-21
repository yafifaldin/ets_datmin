"""
Evaluation Module
=================
Bertanggung jawab untuk:
- Mengukur kualitas rekomendasi dengan Precision@K, Recall@K, NDCG
- Validasi dengan leave-one-out sampling
"""

import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from .feature_engineering import parse_skills_list, normalize_skill_name


def precision_at_k(recommended, relevant, k=10):
    """
    Precision@K = (jumlah item relevant di top-K rekomendasi) / K
    """
    rec_k = recommended[:k]
    hits = len(set(rec_k) & set(relevant))
    return hits / k


def recall_at_k(recommended, relevant, k=10):
    """
    Recall@K = (jumlah item relevant di top-K rekomendasi) / total relevant
    """
    if len(relevant) == 0:
        return 0.0
    rec_k = recommended[:k]
    hits = len(set(rec_k) & set(relevant))
    return hits / len(relevant)


def ndcg_at_k(recommended, relevant, k=10):
    """
    NDCG@K = DCG@K / IDCG@K
    Mengukur kualitas urutan rekomendasi.
    """
    rec_k = recommended[:k]
    relevant_set = set(relevant)

    # DCG: sum of (relevance / log2(rank+1))
    dcg = 0.0
    for i, item in enumerate(rec_k):
        if item in relevant_set:
            dcg += 1.0 / np.log2(i + 2)  # i+2 karena rank dimulai dari 1, log2(1)=0

    # IDCG: ideal DCG kalau semua relevant ada di posisi atas
    ideal_hits = min(len(relevant), k)
    idcg = sum(1.0 / np.log2(i + 2) for i in range(ideal_hits))

    if idcg == 0:
        return 0.0
    return dcg / idcg


def evaluate_recommender(df, job_matrix, vocabulary, n_samples=200,
                          k_values=(5, 10, 20), random_state=42):
    """
    Evaluasi recommender dengan leave-one-skill-out methodology.

    Methodology:
    1. Sample N job dari dataset
    2. Untuk tiap sample, hilangkan 1 skill dari skill list-nya
    3. Gunakan sisa skill sebagai "user profile"
    4. Lihat apakah job-job dengan skill yang dihilangkan tadi
       muncul di top-K rekomendasi

    Returns:
        dict berisi avg precision, recall, ndcg per K
    """
    np.random.seed(random_state)
    n = min(n_samples, len(df))
    sample_idx = np.random.choice(len(df), n, replace=False)

    results = {f"precision@{k}": [] for k in k_values}
    results.update({f"recall@{k}": [] for k in k_values})
    results.update({f"ndcg@{k}": [] for k in k_values})

    for idx in sample_idx:
        skills = parse_skills_list(df.iloc[idx]["skills_list"])
        skills = [normalize_skill_name(s) for s in skills if s]
        if len(skills) < 2:
            continue

        # Hide one skill
        hidden_skill = np.random.choice(skills)
        remaining = [s for s in skills if s != hidden_skill]

        # Build query vector from remaining skills
        skill_to_idx = {s: i for i, s in enumerate(vocabulary)}
        query_vec = np.zeros((1, len(vocabulary)))
        for s in remaining:
            if s in skill_to_idx:
                query_vec[0, skill_to_idx[s]] = 1

        # Find similar jobs
        scores = cosine_similarity(query_vec, job_matrix).flatten()
        # idx bisa lebih besar dari job_matrix kalau matrix di-subsample
        if idx < len(scores):
            scores[idx] = -1  # exclude itself
        ranked = np.argsort(scores)[::-1]

        # Relevant: job lain yang punya hidden_skill
        if hidden_skill in skill_to_idx:
            skill_col_idx = skill_to_idx[hidden_skill]
            relevant_mask = job_matrix[:, skill_col_idx] == 1
            relevant_mask[idx] = False
            relevant = set(np.where(relevant_mask)[0].tolist())
        else:
            relevant = set()

        if len(relevant) == 0:
            continue

        recommended = ranked.tolist()
        for k in k_values:
            results[f"precision@{k}"].append(precision_at_k(recommended, relevant, k))
            results[f"recall@{k}"].append(recall_at_k(recommended, relevant, k))
            results[f"ndcg@{k}"].append(ndcg_at_k(recommended, relevant, k))

    # Average
    summary = {}
    for key, values in results.items():
        if values:
            summary[key] = round(float(np.mean(values)), 4)
        else:
            summary[key] = 0.0

    return summary

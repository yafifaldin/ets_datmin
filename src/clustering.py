"""
Clustering Module (K-Means)
===========================
Bertanggung jawab untuk:
- Segmentasi job ke dalam cluster berdasarkan skill profile
- Menentukan jumlah cluster optimal via Elbow Method
- Label otomatis tiap cluster berdasarkan skill dominan
"""

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score


def find_optimal_k(matrix, k_range=range(2, 11), random_state=42):
    """
    Cari jumlah cluster optimal menggunakan Elbow Method dan Silhouette Score.

    Returns:
        dict berisi optimal_k, inertias, silhouette_scores
    """
    inertias = []
    silhouettes = []

    for k in k_range:
        km = KMeans(n_clusters=k, random_state=random_state, n_init=10)
        labels = km.fit_predict(matrix)
        inertias.append(km.inertia_)

        # Silhouette score (skip if k=1)
        if k >= 2 and len(matrix) > k:
            sil = silhouette_score(matrix, labels, sample_size=min(5000, len(matrix)))
            silhouettes.append(sil)
        else:
            silhouettes.append(0)

    # Optimal k: kombinasi elbow (penurunan inertia) dan silhouette tertinggi
    best_sil_idx = int(np.argmax(silhouettes))
    optimal_k = list(k_range)[best_sil_idx]

    return {
        "optimal_k": optimal_k,
        "k_values": list(k_range),
        "inertias": inertias,
        "silhouette_scores": silhouettes,
    }


def fit_kmeans(matrix, n_clusters=5, random_state=42, scale=True):
    """
    Fit K-Means pada job-skill matrix.

    Returns:
        kmeans model, cluster labels, scaler (optional)
    """
    if scale:
        scaler = StandardScaler()
        X = scaler.fit_transform(matrix)
    else:
        scaler = None
        X = matrix

    kmeans = KMeans(n_clusters=n_clusters, random_state=random_state, n_init=10)
    labels = kmeans.fit_predict(X)
    return kmeans, labels, scaler


def label_clusters(kmeans, vocabulary, top_skills_per_cluster=5):
    """
    Label otomatis tiap cluster berdasarkan skill dominan di centroid.

    Returns:
        dict {cluster_id: {"top_skills": [...], "label": "..."}}
    """
    labels_map = {}
    n_clusters = kmeans.n_clusters

    for cluster_id in range(n_clusters):
        centroid = kmeans.cluster_centers_[cluster_id]
        # Get top skill indices by centroid weight
        top_idx = np.argsort(centroid)[::-1][:top_skills_per_cluster]
        top_skills = [vocabulary[i] for i in top_idx if i < len(vocabulary)]

        # Auto-generate label berdasarkan skill dominan
        label = _generate_cluster_label(top_skills)
        labels_map[cluster_id] = {
            "top_skills": top_skills,
            "label": label,
        }

    return labels_map


def _generate_cluster_label(top_skills):
    """Generate label cluster berdasarkan skill dominan."""
    skills_set = set(s.lower() for s in top_skills)

    # Domain-specific cluster naming
    if {"python", "machine learning", "statistics"} & skills_set or "data scientist" in str(skills_set):
        if "tensorflow" in skills_set or "pytorch" in skills_set or "deep learning" in skills_set:
            return "ML & AI Engineering"
        return "Data Science & Analytics"
    if {"aws", "kubernetes", "docker", "terraform"} & skills_set:
        return "Cloud & DevOps"
    if {"react", "javascript", "typescript", "vue.js", "angular"} & skills_set:
        return "Frontend Development"
    if {"node.js", "java", "spring", "django", "flask"} & skills_set:
        return "Backend Development"
    if {"sql", "data analysis", "tableau", "power bi"} & skills_set:
        return "Data Analytics & BI"
    if {"cybersecurity", "security"} & skills_set:
        return "Cybersecurity"
    if {"product management", "agile", "scrum"} & skills_set:
        return "Product & Project Management"

    # Fallback
    return f"Cluster: {', '.join(top_skills[:2]).title()}"

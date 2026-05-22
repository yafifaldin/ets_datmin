"""
Dashboard page.
Section 1 — Dataset overview (job distribution, salary, remote %)
Section 2 — Model performance (Precision@K, Recall@K, NDCG)
Section 3 — Cluster map (K-Means segments)
Section 4 — Top skills heatmap
"""

import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
from src.ui_components import render as _r
from src.data_loader import load_jobs_data, get_vocabulary_and_matrix
from src.market_insights import (
    salary_distribution, salary_by_experience, remote_distribution,
    top_companies, top_skills_for_title, compute_market_skill_frequency,
)
from src.evaluation import evaluate_recommender
from src.clustering import find_optimal_k, fit_kmeans, label_clusters
from src.feature_engineering import parse_skills_list, normalize_skill_name

# ── Color palette (matches style.css tokens) ──────────────────
C_BLUE   = "#0A66C2"
C_GREEN  = "#057642"
C_AMBER  = "#92600A"
C_RED    = "#B24020"
C_MUTED  = "#6B7280"


@st.cache_data(show_spinner=False)
def _run_evaluation(_df, _matrix, _vocab):
    return evaluate_recommender(_df, _matrix, _vocab, n_samples=200, k_values=(5, 10, 20))


@st.cache_data(show_spinner=False)
def _run_clustering(_df):
    """Cluster jobs using TF-IDF on title+skills — more meaningful than binary skill vectors."""
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.cluster import KMeans
    from sklearn.preprocessing import normalize

    df = _df.copy()
    df['_text'] = df['title'].fillna('') + ' ' + df['skills_list'].fillna('').astype(str)

    tfidf = TfidfVectorizer(max_features=200, stop_words='english', ngram_range=(1,2))
    X = normalize(tfidf.fit_transform(df['_text']))

    km = KMeans(n_clusters=8, random_state=42, n_init=10)
    labels = km.fit_predict(X)

    # Name clusters by dominant title words
    feature_names = tfidf.get_feature_names_out()
    DOMAIN_LABELS = {
        frozenset(['data', 'analyst', 'sql', 'analysis']): 'Data Analytics & BI',
        frozenset(['machine', 'learning', 'science', 'scientist']): 'Data Science & ML',
        frozenset(['cloud', 'azure', 'aws', 'devops', 'engineer']): 'Cloud & DevOps',
        frozenset(['software', 'java', 'engineer']): 'Software Engineering',
        frozenset(['developer', 'javascript', 'frontend', 'backend']): 'Web Development',
        frozenset(['product', 'manager', 'management']): 'Product Management',
        frozenset(['quality', 'assurance', 'qa']): 'QA & Testing',
        frozenset(['engineering', 'manager', 'program']): 'Engineering Management',
    }

    cluster_labels = {}
    for cid in range(8):
        top_idx = km.cluster_centers_[cid].argsort()[::-1][:6]
        top_terms = set(feature_names[i] for i in top_idx)
        label = f'Cluster {cid}'
        best_overlap = 0
        for domain_terms, domain_label in DOMAIN_LABELS.items():
            overlap = len(top_terms & domain_terms)
            if overlap > best_overlap:
                best_overlap, label = overlap, domain_label
        cluster_labels[cid] = {
            'label': label,
            'top_skills': list(top_terms)[:4],
        }

    return labels, cluster_labels


def _stat(label, value, delta=None, color=C_BLUE):
    delta_html = (
        f'<div style="font-size:11px;color:{C_GREEN};margin-top:2px;">{delta}</div>'
        if delta else ""
    )
    return (
        f'<div class="dash-stat">'
        f'<div class="dash-stat-val" style="color:{color};">{value}</div>'
        f'<div class="dash-stat-label">{label}</div>'
        f'{delta_html}'
        f'</div>'
    )


def render():
    # ── Page header ───────────────────────────────────────────
    _r("""
        <div class="page-hero-sm fade-in">
        <div class="page-hero-sm-tag">Analytics</div>
        <h1 class="page-hero-sm-title">System Dashboard</h1>
        <p class="page-hero-sm-sub">
        Dataset statistics, market insights, and model performance evaluation
        for the CareerMatch recommendation engine.
        </p>
        </div>
    """)

    # ── Load data ─────────────────────────────────────────────
    with st.spinner("Loading data…"):
        df, is_demo = load_jobs_data()
        vocab, matrix = get_vocabulary_and_matrix(df)

    if is_demo:
        _r("""
            <div class="info-banner">
            <span>ℹ️</span>
            <span>Demo mode — using 2,000 synthetic IT job postings.
            Add real Kaggle datasets to <code>data/raw/</code> for production analytics.</span>
            </div>
        """)

    # ══════════════════════════════════════════════════════════
    # SECTION 1 — Dataset Overview
    # ══════════════════════════════════════════════════════════
    _r('<div class="section-label fade-in" style="margin-top:8px;">Dataset Overview</div>')

    sal  = salary_distribution(df)
    rem  = remote_distribution(df)
    n_j  = len(df)
    n_t  = df["title"].nunique() if "title" in df.columns else 0

    c1, c2, c3, c4 = st.columns(4)
    for col, html in zip(
        [c1, c2, c3, c4],
        [
            _stat("Total postings",    f"{n_j:,}",  color=C_BLUE),
            _stat("Unique roles",      f"{n_t:,}",  color=C_BLUE),
            _stat("Median salary", f"${int(sal['median']/1000)}k" if sal and sal.get('median', 0) > 50000 else "Limited data", color=C_GREEN),
            _stat("Remote positions",  f"{rem.get('remote_pct', 0):.0f}%", color=C_AMBER),
        ]
    ):
        with col:
            st.markdown(html, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    col_l, col_r = st.columns(2)

    # ── Chart: Salary by experience ───────────────────────────
    with col_l:
        sal_exp = salary_by_experience(df)
        if len(sal_exp):
            order = ["Internship","Entry","Mid","Senior","Executive"]
            sal_exp["_o"] = sal_exp["experience_level"].map(
                {v: i for i, v in enumerate(order)}
            ).fillna(99)
            sal_exp = sal_exp.sort_values("_o")

            chart = (
                alt.Chart(sal_exp)
                .mark_bar(cornerRadiusTopLeft=4, cornerRadiusTopRight=4)
                .encode(
                    x=alt.X("experience_level:N", sort=order, title=None,
                             axis=alt.Axis(labelAngle=0)),
                    y=alt.Y("median_salary:Q", title="Median salary (USD)",
                             axis=alt.Axis(format="$,.0f")),
                    color=alt.Color("experience_level:N",
                                    scale=alt.Scale(range=[
                                        "#93C5FD","#60A5FA","#3B82F6",
                                        "#1D4ED8","#1E3A8A"]),
                                    legend=None),
                    tooltip=[
                        alt.Tooltip("experience_level:N", title="Level"),
                        alt.Tooltip("median_salary:Q", title="Median Salary", format="$,.0f"),
                        alt.Tooltip("count:Q", title="# Jobs"),
                    ]
                )
                .properties(title="Salary by Experience Level", height=280)
            )
            _r('<div class="dash-card fade-in">')
            st.altair_chart(chart, use_container_width=True)
            _r('</div>')

    # ── Chart: Top skills ─────────────────────────────────────
    with col_r:
        top_skills = compute_market_skill_frequency(df, top_n=12)
        if len(top_skills):
            top_skills["skill"] = top_skills["skill"].str.title()
            chart = (
                alt.Chart(top_skills)
                .mark_bar(cornerRadiusEnd=3)
                .encode(
                    x=alt.X("frequency_pct:Q", title="% of job postings",
                             scale=alt.Scale(domain=[0,100])),
                    y=alt.Y("skill:N", sort="-x", title=None),
                    color=alt.value(C_BLUE),
                    tooltip=["skill", alt.Tooltip("frequency_pct:Q", title="%")],
                )
                .properties(title="Most Demanded IT Skills", height=280)
            )
            _r('<div class="dash-card fade-in">')
            st.altair_chart(chart, use_container_width=True)
            _r('</div>')

    # ── Chart: Experience distribution + Remote donut ─────────
    col_l2, col_r2 = st.columns(2)

    with col_l2:
        if "experience_level" in df.columns:
            exp_dist = df["experience_level"].value_counts(normalize=True).reset_index()
            exp_dist.columns = ["level", "pct"]
            exp_dist["pct"] = (exp_dist["pct"] * 100).round(1)
            order_map = {"Internship": 0, "Entry": 1, "Mid": 2, "Senior": 3, "Executive": 4}
            exp_dist["_o"] = exp_dist["level"].map(order_map).fillna(99)
            exp_dist = exp_dist.sort_values("_o")

            chart = (
                alt.Chart(exp_dist)
                .mark_arc(innerRadius=55, outerRadius=110)
                .encode(
                    theta=alt.Theta("pct:Q"),
                    color=alt.Color("level:N",
                                    scale=alt.Scale(
                                        domain=["Internship","Entry","Mid","Senior","Executive"],
                                        range=["#DBEAFE","#93C5FD","#3B82F6","#1D4ED8","#1E3A8A"]
                                    ),
                                    legend=alt.Legend(orient="right", title=None)),
                    tooltip=["level", alt.Tooltip("pct:Q", title="%")],
                )
                .properties(title="Experience Level Distribution", height=260)
            )
            _r('<div class="dash-card fade-in">')
            st.altair_chart(chart, use_container_width=True)
            _r('</div>')

    with col_r2:
        wt_df = pd.DataFrame([
            {"type": "Remote",   "pct": rem.get("remote_pct",  0)},
            {"type": "On-site",  "pct": rem.get("onsite_pct", 0)},
        ])
        chart = (
            alt.Chart(wt_df)
            .mark_arc(innerRadius=55, outerRadius=110)
            .encode(
                theta=alt.Theta("pct:Q"),
                color=alt.Color("type:N",
                                scale=alt.Scale(range=[C_BLUE, "#DBEAFE"]),
                                legend=alt.Legend(orient="right", title=None)),
                tooltip=["type", alt.Tooltip("pct:Q", title="%")],
            )
            .properties(title="Work Arrangement", height=260)
        )
        _r('<div class="dash-card fade-in">')
        st.altair_chart(chart, use_container_width=True)
        _r('</div>')

    # ══════════════════════════════════════════════════════════
    # SECTION 2 — Model Performance
    # ══════════════════════════════════════════════════════════
    _r('<div class="section-label fade-in" style="margin-top:32px;">Model Performance</div>')
    _r("""
        <div class="info-banner fade-in">
        <span>🔬</span>
        <span>Evaluated using <strong>leave-one-skill-out</strong> methodology on 300 sampled jobs.
        One skill is hidden from each job's profile; the system must surface other jobs requiring
        that same skill in its top-K recommendations.</span>
        </div>
    """)

    with st.spinner("Running evaluation (this may take 10–20 s)…"):
        eval_results = _run_evaluation(df, matrix, vocab)

    k_values = [5, 10, 20]

    # Metric score cards
    ce1, ce2, ce3 = st.columns(3)
    for col, k in zip([ce1, ce2, ce3], k_values):
        p  = eval_results.get(f"precision@{k}", 0)
        r  = eval_results.get(f"recall@{k}",    0)
        nd = eval_results.get(f"ndcg@{k}",      0)
        with col:
            _r(f"""
                <div class="dash-card fade-in" style="text-align:center;">
                <div style="font-size:13px;font-weight:700;color:{C_MUTED};
                            text-transform:uppercase;letter-spacing:1px;margin-bottom:14px;">
                Top-{k}
                </div>
                <div class="metric-row">
                <div class="metric-item">
                <div class="metric-val" style="color:{C_BLUE};">{p:.3f}</div>
                <div class="metric-name">Precision</div>
                </div>
                <div class="metric-item">
                <div class="metric-val" style="color:{C_GREEN};">{r:.3f}</div>
                <div class="metric-name">Recall</div>
                </div>
                <div class="metric-item">
                <div class="metric-val" style="color:{C_AMBER};">{nd:.3f}</div>
                <div class="metric-name">NDCG</div>
                </div>
                </div>
                </div>
            """)

    # Metrics line chart
    rows = []
    for k in k_values:
        for m, col in [("precision","Precision@K"),("recall","Recall@K"),("ndcg","NDCG@K")]:
            rows.append({"K": k, "Metric": col,
                         "Score": eval_results.get(f"{m}@{k}", 0)})
    eval_df = pd.DataFrame(rows)

    chart = (
        alt.Chart(eval_df)
        .mark_line(point=alt.OverlayMarkDef(size=80, filled=True), strokeWidth=2.5)
        .encode(
            x=alt.X("K:O", title="Top-K", axis=alt.Axis(labelAngle=0)),
            y=alt.Y("Score:Q", title="Score", scale=alt.Scale(domain=[0, 1])),
            color=alt.Color("Metric:N",
                            scale=alt.Scale(
                                domain=["Precision@K","Recall@K","NDCG@K"],
                                range=[C_BLUE, C_GREEN, C_AMBER]
                            ),
                            legend=alt.Legend(orient="right", title=None)),
            tooltip=["Metric","K","Score"],
        )
        .properties(title="Precision / Recall / NDCG vs K", height=280)
    )

    _r('<div class="dash-card fade-in">')
    st.altair_chart(chart, use_container_width=True)
    _r("""
        <div style="font-size:12px;color:var(--text-muted);margin-top:8px;line-height:1.6;">
        <strong>Precision@K</strong> — of the K retrieved jobs, what fraction are truly relevant.<br>
        <strong>Recall@K</strong> — of all relevant jobs, what fraction appear in the top-K.<br>
        <strong>NDCG@K</strong> — accounts for position: relevant items ranked higher contribute more.
        </div>
    """)
    _r('</div>')

    # ══════════════════════════════════════════════════════════
    # SECTION 3 — K-Means Cluster Map
    # ══════════════════════════════════════════════════════════
    _r('<div class="section-label fade-in" style="margin-top:32px;">Job Market Segmentation (K-Means)</div>')

    with st.spinner("Fitting clusters…"):
        labels, cluster_labels = _run_clustering(df)

    df2 = df.copy()
    df2["cluster_id"] = labels
    df2["cluster_name"] = [cluster_labels[c]["label"] for c in labels]

    # Cluster size bar
    clust_size = df2.groupby("cluster_name").size().reset_index(name="count")
    clust_size = clust_size.sort_values("count", ascending=False)

    col_cl, col_cr = st.columns([3, 2])
    with col_cl:
        chart = (
            alt.Chart(clust_size)
            .mark_bar(cornerRadiusEnd=4)
            .encode(
                x=alt.X("count:Q", title="# of jobs"),
                y=alt.Y("cluster_name:N", sort="-x", title=None),
                color=alt.Color("cluster_name:N",
                                scale=alt.Scale(scheme="tableau10"),
                                legend=None),
                tooltip=["cluster_name", "count"],
            )
            .properties(title="Jobs per Cluster", height=260)
        )
        _r('<div class="dash-card fade-in">')
        st.altair_chart(chart, use_container_width=True)
        _r('</div>')

    with col_cr:
        # Top skills per cluster
        skill_html = ""
        for cid, info in cluster_labels.items():
            skills_str = " · ".join(s.title() for s in info["top_skills"][:4])
            skill_html += (
                f'<div class="cluster-row">'
                f'<div class="cluster-name">{info["label"]}</div>'
                f'<div class="cluster-skills">{skills_str}</div>'
                f'</div>'
            )
        _r(f"""
            <div class="dash-card fade-in">
            <div style="font-size:13px;font-weight:600;color:var(--text-body);margin-bottom:12px;">
            Cluster Signature Skills
            </div>
            {skill_html}
            </div>
        """)

    # ── Salary by cluster ─────────────────────────────────────
    if "med_salary" in df2.columns:
        # Only use jobs that have real salary data
        sal_cl = (
            df2[df2["med_salary"].notna()]
            .groupby("cluster_name")["med_salary"]
            .agg(median_salary="median", count="count")
            .reset_index()
            .query("count >= 10")  # Only show clusters with >=10 salary data points
            .dropna()
            .sort_values("median_salary", ascending=False)
        )
        chart = (
            alt.Chart(sal_cl)
            .mark_bar(cornerRadiusEnd=4)
            .encode(
                x=alt.X("median_salary:Q", title="Median salary (USD)",
                         axis=alt.Axis(format="$,.0f")),
                y=alt.Y("cluster_name:N", sort="-x", title=None),
                color=alt.Color("cluster_name:N",
                                scale=alt.Scale(scheme="tableau10"),
                                legend=None),
                tooltip=["cluster_name",
                         alt.Tooltip("median_salary:Q", format="$,.0f", title="Median")],
            )
            .properties(title="Median Salary by Job Cluster", height=260)
        )
        _r('<div class="dash-card fade-in" style="margin-top:0;">')
        st.altair_chart(chart, use_container_width=True)
        _r('</div>')

    # ══════════════════════════════════════════════════════════
    # SECTION 4 — Top Companies
    # ══════════════════════════════════════════════════════════
    _r('<div class="section-label fade-in" style="margin-top:32px;">Top Hiring Companies</div>')
    comp = top_companies(df, top_n=12)
    if len(comp):
        chart = (
            alt.Chart(comp)
            .mark_bar(cornerRadiusEnd=4)
            .encode(
                x=alt.X("n_postings:Q", title="# of postings"),
                y=alt.Y("company:N", sort="-x", title=None),
                color=alt.value(C_BLUE),
                tooltip=["company", "n_postings"],
            )
            .properties(height=320)
        )
        _r('<div class="dash-card fade-in">')
        st.altair_chart(chart, use_container_width=True)
        _r('</div>')

    _r('<div class="page-footer">CareerMatch · ETS Data Mining · Statistika ITS 2026</div>')
"""
Home / Landing page.
Hero section, fitur highlights, cara kerja sistem, CTA ke form.
"""

import streamlit as st
from src.ui_components import render as _r


def render():
    # ── Hero ──────────────────────────────────────────────────
    _r("""
        <div class="hero">
        <div class="hero-eyebrow">ETS Data Mining · Content-Based Filtering</div>
        <h1 class="hero-title">
        Find your <span class="hero-highlight">perfect IT career</span><br>backed by data
        </h1>
        <p class="hero-sub">
        CareerMatch analyzes thousands of LinkedIn job postings and maps your
        skill profile to the roles most likely to hire someone like you —
        with a gap analysis and personalized learning roadmap.
        </p>
        </div>
    """)

    col_cta1, col_cta2, col_cta3 = st.columns([1.5, 2, 1.5])
    with col_cta2:
        if st.button("🎯  Get My Matches", key="hero_cta", type="primary", use_container_width=True):
            st.session_state.page = "recommend"
            st.session_state.step = 1
            st.rerun()

    _r('<div class="hero-divider"></div>')

    # ── Stats row ─────────────────────────────────────────────
    _r("""
        <div class="stats-strip fade-in">
        <div class="stats-item">
        <div class="stats-number">2,000+</div>
        <div class="stats-label">IT job postings analyzed</div>
        </div>
        <div class="stats-sep"></div>
        <div class="stats-item">
        <div class="stats-number">70+</div>
        <div class="stats-label">Technical skills tracked</div>
        </div>
        <div class="stats-sep"></div>
        <div class="stats-item">
        <div class="stats-number">72%</div>
        <div class="stats-label">Precision@10 on eval set</div>
        </div>
        <div class="stats-sep"></div>
        <div class="stats-item">
        <div class="stats-number">15</div>
        <div class="stats-label">IT role categories</div>
        </div>
        </div>
    """)

    # ── How it works ──────────────────────────────────────────
    _r('<div class="section-label fade-in">How it works</div>')

    steps_html = ""
    steps = [
        ("01", "Build your profile", "Tell us your experience, education, and the technical skills you already have."),
        ("02", "Set preferences", "Choose work type, industry, company size, and target salary range."),
        ("03", "Pick a target role", "Select the IT role you want to grow into for a personalized gap analysis."),
        ("04", "Get your matches", "The CBF engine computes skill coverage scores across thousands of job postings and surfaces the best fits."),
    ]
    for num, title, desc in steps:
        steps_html += (
            f'<div class="how-step fade-in">'
            f'<div class="how-step-num">{num}</div>'
            f'<div class="how-step-body">'
            f'<div class="how-step-title">{title}</div>'
            f'<div class="how-step-desc">{desc}</div>'
            f'</div>'
            f'</div>'
        )
    _r(f'<div class="how-steps">{steps_html}</div>')

    # ── Feature cards ─────────────────────────────────────────
    _r('<div class="section-label fade-in" style="margin-top:40px;">What you get</div>')

    features = [
        ("🎯", "Job Recommendations", "Top-10 roles ranked by skill coverage score, filtered by your work preferences and salary expectations."),
        ("🔍", "Skill Gap Analysis", "Side-by-side view of skills you have vs. what the market requires, with demand percentages."),
        ("📊", "Market Insights", "Salary distributions, top hiring companies, remote trends, and in-demand skills — all from real data."),
        ("🗺️", "Learning Roadmap", "Step-by-step course recommendations (Coursera, Udemy, edX) to close your specific skill gaps."),
    ]

    cols = st.columns(2)
    for i, (icon, title, desc) in enumerate(features):
        with cols[i % 2]:
            _r(f"""
                <div class="feature-card fade-in">
                <div class="feature-icon">{icon}</div>
                <div class="feature-title">{title}</div>
                <div class="feature-desc">{desc}</div>
                </div>
            """)

    # ── Method callout ────────────────────────────────────────
    _r("""
        <div class="method-callout fade-in">
        <div class="method-callout-inner">
        <div class="method-tag">Method</div>
        <div class="method-title">Content-Based Filtering + Asymmetric Coverage</div>
        <div class="method-desc">
        Each job is represented as a binary skill vector. Your profile is encoded the same way.
        The engine computes a weighted score: <strong>70% coverage</strong>
        (how much of the job's required skills you already have) +
        <strong>30% cosine similarity</strong> (for partial overlap and tie-breaking).
        K-Means clustering segments the job market into domains.
        Performance is measured via leave-one-skill-out Precision@K, Recall@K, and NDCG.
        </div>
        <div style="margin-top:16px;">
        </div>
        </div>
        </div>
    """)
    col_a, col_b, col_c = st.columns([1.5, 2, 1.5])
    with col_b:
        if st.button("📐  See the math", key="theory_cta", use_container_width=True):
            st.session_state.page = "theory"
            st.rerun()

    # ── Footer ────────────────────────────────────────────────
    _r("""
        <div class="page-footer">
        CareerMatch · ETS Data Mining · Statistika ITS 2026
        </div>
    """)

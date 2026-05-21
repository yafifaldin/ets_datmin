"""
Step 5: Loading animation.

Menjalankan analisis di background dengan animasi pesan bertahap
yang menjelaskan apa yang sedang dilakukan sistem.
"""

import streamlit as st
import time
from src.ui_components import render_step_indicator
from src.data_loader import load_jobs_data, get_vocabulary_and_matrix
from src.recommender import compute_similarity, apply_preference_filter, get_top_recommendations
from src.feature_engineering import build_user_vector, parse_skills_list, normalize_skill_name
from src.gap_analysis import gap_to_target_job
from src.roadmap import build_roadmap


STEP_LABELS = ["Basic", "Skills", "Preferences", "Target", "Analysis", "Results"]

# Map UI experience option to internal canonical level
EXP_MAP = {
    "Internship / Fresh Graduate": "Entry",
    "Entry level (0-2 years)": "Entry",
    "Mid level (2-5 years)": "Mid",
    "Senior (5-10 years)": "Senior",
    "Executive (10+ years)": "Executive",
}


def _run_analysis(profile):
    """Jalankan full pipeline analisis, return dict of results."""
    df, _ = load_jobs_data()
    vocab, job_matrix = get_vocabulary_and_matrix(df)

    # Build user vector
    user_vec = build_user_vector(profile["tech_skills"], vocab)

    # Compute similarity + apply preference filter
    scores = compute_similarity(user_vec, job_matrix)
    prefs = {
        "experience_level": EXP_MAP.get(profile["experience_level"], "Mid"),
        "work_type": profile["work_type"],
        "industry": profile.get("industry", "Any"),
        "company_size": profile.get("company_size", "Any"),
        "min_salary": profile["min_salary"],
        "max_salary": profile["max_salary"],
    }
    scores = apply_preference_filter(df, scores, prefs)
    top = get_top_recommendations(df, scores, top_n=10)

    # Enrich with matched/missing skills per job
    user_skills_norm = set(normalize_skill_name(s) for s in profile["tech_skills"])
    matched_list, missing_list = [], []
    for _, row in top.iterrows():
        job_skills = parse_skills_list(row.get("skills_list", []))
        job_skills_norm = set(normalize_skill_name(s) for s in job_skills if s)
        matched_list.append(sorted(user_skills_norm & job_skills_norm))
        missing_list.append(sorted(job_skills_norm - user_skills_norm))
    top["matched_skills"] = matched_list
    top["missing_skills"] = missing_list

    # Gap analysis for target job
    gap = gap_to_target_job(profile["tech_skills"], profile["target_job"], df)

    # Build roadmap
    roadmap = build_roadmap(gap.get("skill_priority", []), max_skills=8)

    return {
        "recommendations": top,
        "gap_analysis": gap,
        "roadmap": roadmap,
    }


def render():
    render_step_indicator(current_step=5, total_steps=6, labels=STEP_LABELS)

    loading_placeholder = st.empty()

    messages = [
        "Reading your profile…",
        "Building skill vector representation…",
        "Loading job dataset…",
        "Computing cosine similarity with thousands of jobs…",
        "Analyzing skill gap for your target role…",
        "Generating personalized learning roadmap…",
        "Finalizing recommendations…",
    ]

    profile = st.session_state.profile

    # Show first few messages with delays for UX
    for i, msg in enumerate(messages[:3]):
        loading_placeholder.markdown(f"""
            <div class="loading-container fade-in">
                <div class="loading-spinner"></div>
                <div class="loading-text">{msg}</div>
                <div class="loading-substep">Step {i+1} of {len(messages)}</div>
            </div>
        """, unsafe_allow_html=True)
        time.sleep(0.6)

    # Show "computing similarity" message during actual heavy work
    loading_placeholder.markdown(f"""
        <div class="loading-container fade-in">
            <div class="loading-spinner"></div>
            <div class="loading-text">{messages[3]}</div>
            <div class="loading-substep">Step 4 of {len(messages)}</div>
        </div>
    """, unsafe_allow_html=True)

    # Heavy lifting happens here
    try:
        results = _run_analysis(profile)
        st.session_state.recommendations = results["recommendations"]
        st.session_state.gap_analysis = results["gap_analysis"]
        st.session_state.roadmap = results["roadmap"]
    except Exception as e:
        loading_placeholder.empty()
        st.error(f"❌ Analysis failed: {e}")
        if st.button("← Back to start", key="step5_error_back"):
            st.session_state.step = 1
            st.rerun()
        return

    # Remaining UX messages
    for i, msg in enumerate(messages[4:], start=4):
        loading_placeholder.markdown(f"""
            <div class="loading-container fade-in">
                <div class="loading-spinner"></div>
                <div class="loading-text">{msg}</div>
                <div class="loading-substep">Step {i+1} of {len(messages)}</div>
            </div>
        """, unsafe_allow_html=True)
        time.sleep(0.6)

    loading_placeholder.empty()
    st.session_state.submitted = True
    st.session_state.step = 6
    st.rerun()

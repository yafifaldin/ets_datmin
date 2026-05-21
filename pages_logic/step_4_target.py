"""Step 4: Pilih target job yang ingin diraih untuk gap analysis."""

import streamlit as st
from src.ui_components import render_step_indicator, render_form_header
from src.data_loader import load_jobs_data, get_target_job_titles


STEP_LABELS = ["Basic", "Skills", "Preferences", "Target", "Analysis", "Results"]


def render():
    render_step_indicator(current_step=4, total_steps=6, labels=STEP_LABELS)
    render_form_header(
        "What's your target role?",
        "Choose the job you'd like to grow into. We'll show you the skill gap and build a learning roadmap to get there."
    )

    df, is_demo = load_jobs_data()
    target_titles = get_target_job_titles(df, top_n=25)

    st.markdown('<div class="li-card fade-in">', unsafe_allow_html=True)

    if is_demo:
        st.markdown(
            '<div style="margin-bottom: 16px; padding: 10px 14px; background: var(--li-blue-light); '
            'border-radius: 6px; color: var(--li-blue-dark); font-size: 12px;">'
            'ℹ️ Demo mode: Using synthetic job dataset. Add the real Kaggle dataset to data/raw/ for production use.'
            '</div>',
            unsafe_allow_html=True
        )

    st.markdown('<div class="li-label">Select your target IT role</div>', unsafe_allow_html=True)
    st.markdown('<div class="li-helper" style="margin-bottom: 12px;">This determines the gap analysis and learning roadmap we generate for you.</div>', unsafe_allow_html=True)

    default_idx = 0
    current_target = st.session_state.profile.get("target_job")
    if current_target and current_target in target_titles:
        default_idx = target_titles.index(current_target)

    target_job = st.selectbox(
        "Target job",
        target_titles,
        index=default_idx,
        label_visibility="collapsed",
        key="step4_target"
    )

    # Show preview info about target
    n_matching = sum(1 for t in df["title"].fillna("").astype(str)
                     if target_job.lower() in t.lower())
    st.markdown(f"""<div style="margin-top: 16px; padding: 12px 16px; background: var(--li-bg);border-radius: 6px; font-size: 13px; color: var(--li-text-secondary);"><span style="color: var(--li-blue); font-weight: 600;">{n_matching:,}</span>job postings found matching this target in our dataset.</div>""", unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

    # Profile Summary Preview
    st.markdown('<div class="li-card fade-in" style="margin-top: 16px;">', unsafe_allow_html=True)
    st.markdown('<h3 class="li-h3">Profile summary</h3>', unsafe_allow_html=True)
    p = st.session_state.profile

    summary_rows = [
        ("Experience", p.get("experience_level", "—")),
        ("Education", p.get("education", "—")),
        ("Field", p.get("major", "—")),
        ("Skills", f"{len(p.get('tech_skills', []))} technical, {len(p.get('soft_skills', []))} soft"),
        ("Work type", p.get("work_type", "Any")),
        ("Salary expectation", f"${p.get('min_salary', 0):,} – ${p.get('max_salary', 0):,}"),
    ]
    rows_html = ""
    for label, value in summary_rows:
        rows_html += (
            '<div style="display:flex;justify-content:space-between;padding:6px 0;'
            'border-bottom:1px solid var(--li-divider);font-size:14px;">'
            f'<span style="color:var(--li-text-secondary);">{label}</span>'
            f'<span style="color:var(--li-text);font-weight:500;">{value}</span>'
            '</div>'
        )
    st.markdown(rows_html, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

    # Navigation
    st.markdown('<div style="margin-top: 24px;"></div>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        if st.button("←  Back", key="step4_back", width="stretch", type="secondary"):
            st.session_state.profile["target_job"] = target_job
            st.session_state.step = 3
            st.rerun()
    with col3:
        if st.button("Submit  ✓", key="step4_submit", width="stretch"):
            st.session_state.profile["target_job"] = target_job
            st.session_state.step = 5
            st.rerun()

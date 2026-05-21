"""Step 3: Preferensi kerja - tipe, ukuran company, industri, gaji."""

import streamlit as st
from src.ui_components import render_step_indicator, render_form_header


STEP_LABELS = ["Basic", "Skills", "Preferences", "Target", "Analysis", "Results"]


def render():
    render_step_indicator(current_step=3, total_steps=6, labels=STEP_LABELS)
    render_form_header(
        "Your work preferences",
        "Help us understand what kind of work environment you're looking for."
    )

    st.markdown('<div class="li-card fade-in">', unsafe_allow_html=True)

    # Work Type
    st.markdown('<div class="li-label">Preferred work type</div>', unsafe_allow_html=True)
    work_options = ["Any", "Remote", "On-site", "Hybrid"]
    wt_idx = work_options.index(st.session_state.profile.get("work_type", "Any"))
    work_type = st.radio(
        "Work type",
        work_options,
        index=wt_idx,
        horizontal=True,
        label_visibility="collapsed",
        key="step3_work"
    )

    st.markdown('<div style="margin-top: 20px;"></div>', unsafe_allow_html=True)

    # Company Size
    st.markdown('<div class="li-label">Company size</div>', unsafe_allow_html=True)
    size_options = ["Any", "Startup (1-50)", "Mid-size (51-500)",
                    "Large (501-5000)", "Enterprise (5000+)"]
    size_idx = size_options.index(st.session_state.profile.get("company_size", "Any")) \
        if st.session_state.profile.get("company_size", "Any") in size_options else 0
    company_size = st.selectbox(
        "Company size",
        size_options,
        index=size_idx,
        label_visibility="collapsed",
        key="step3_size"
    )

    st.markdown('<div style="margin-top: 20px;"></div>', unsafe_allow_html=True)

    # Industry
    st.markdown('<div class="li-label">Preferred industry</div>', unsafe_allow_html=True)
    industry_options = [
        "Any",
        "Technology",
        "Financial Services / Fintech",
        "Healthcare / Healthtech",
        "E-commerce / Retail",
        "Consulting",
        "Telecommunications",
        "Manufacturing",
        "Education",
    ]
    ind_idx = industry_options.index(st.session_state.profile.get("industry", "Any")) \
        if st.session_state.profile.get("industry", "Any") in industry_options else 0
    industry = st.selectbox(
        "Industry",
        industry_options,
        index=ind_idx,
        label_visibility="collapsed",
        key="step3_industry"
    )

    st.markdown('<div style="margin-top: 24px;"></div>', unsafe_allow_html=True)

    # Salary Range
    st.markdown('<div class="li-label">Expected salary range (USD/year)</div>', unsafe_allow_html=True)
    st.markdown('<div class="li-helper" style="margin-bottom: 12px;">Drag to set your minimum and maximum expected annual salary</div>', unsafe_allow_html=True)
    salary_range = st.slider(
        "Salary range",
        min_value=30000,
        max_value=250000,
        value=(
            st.session_state.profile.get("min_salary", 60000),
            st.session_state.profile.get("max_salary", 150000),
        ),
        step=5000,
        format="$%d",
        label_visibility="collapsed",
        key="step3_salary"
    )

    st.markdown(f"""<div style="text-align: center; margin-top: 12px;"><span style="font-weight: 600; color: var(--li-blue); font-size: 16px;">${salary_range[0]:,} – ${salary_range[1]:,}</span></div>""", unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

    # Navigation
    st.markdown('<div style="margin-top: 24px;"></div>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 3, 1])
    with col1:
        if st.button("←  Back", key="step3_back", width="stretch", type="secondary"):
            st.session_state.profile["work_type"] = work_type
            st.session_state.profile["company_size"] = company_size
            st.session_state.profile["industry"] = industry
            st.session_state.profile["min_salary"] = salary_range[0]
            st.session_state.profile["max_salary"] = salary_range[1]
            st.session_state.step = 2
            st.rerun()
    with col3:
        if st.button("Next  →", key="step3_next", width="stretch"):
            st.session_state.profile["work_type"] = work_type
            st.session_state.profile["company_size"] = company_size
            st.session_state.profile["industry"] = industry
            st.session_state.profile["min_salary"] = salary_range[0]
            st.session_state.profile["max_salary"] = salary_range[1]
            st.session_state.step = 4
            st.rerun()

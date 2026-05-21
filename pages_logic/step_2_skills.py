"""Step 2: Pilih technical skills dan soft skills."""

import streamlit as st
from src.ui_components import render_step_indicator, render_form_header
from src.data_loader import load_skill_taxonomy


STEP_LABELS = ["Basic", "Skills", "Preferences", "Target", "Analysis", "Results"]


def render():
    render_step_indicator(current_step=2, total_steps=6, labels=STEP_LABELS)
    render_form_header(
        "What are your skills?",
        "Select the technical and soft skills you currently have. The more accurate this is, the better your recommendations."
    )

    taxonomy = load_skill_taxonomy()

    st.markdown('<div class="li-card fade-in">', unsafe_allow_html=True)
    st.markdown('<h3 class="li-h3">Technical skills</h3>', unsafe_allow_html=True)
    st.markdown('<div class="li-helper" style="margin-bottom: 16px;">Pick from any category. There\'s no minimum or maximum.</div>', unsafe_allow_html=True)

    all_selected_tech = list(st.session_state.profile.get("tech_skills", []))
    new_selection = []

    for category, skills in taxonomy.items():
        st.markdown(f'<div class="li-label" style="margin-top: 12px;">{category}</div>', unsafe_allow_html=True)
        default_in_cat = [s for s in all_selected_tech if s in skills]
        selected = st.multiselect(
            category,
            skills,
            default=default_in_cat,
            label_visibility="collapsed",
            key=f"step2_tech_{category}"
        )
        new_selection.extend(selected)

    st.markdown('</div>', unsafe_allow_html=True)

    # Soft Skills
    st.markdown('<div class="li-card fade-in" style="margin-top: 16px;">', unsafe_allow_html=True)
    st.markdown('<h3 class="li-h3">Soft skills</h3>', unsafe_allow_html=True)
    st.markdown('<div class="li-helper" style="margin-bottom: 12px;">Pick your top 3 strongest soft skills</div>', unsafe_allow_html=True)

    soft_options = [
        "Leadership", "Communication", "Problem Solving", "Critical Thinking",
        "Teamwork", "Adaptability", "Creativity", "Time Management",
        "Conflict Resolution", "Emotional Intelligence",
    ]
    # Defensive: ensure default doesn't exceed max_selections
    soft_default = st.session_state.profile.get("soft_skills", [])[:3]
    soft_skills = st.multiselect(
        "Soft skills",
        soft_options,
        default=soft_default,
        max_selections=3,
        label_visibility="collapsed",
        key="step2_soft"
    )

    st.markdown('</div>', unsafe_allow_html=True)

    # Warning if no tech skills
    if len(new_selection) == 0:
        st.markdown(
            '<div style="margin-top: 16px; padding: 12px 16px; background: var(--li-warning-light); '
            'border-radius: 6px; color: var(--li-warning); font-size: 13px;">'
            '⚠️ Please select at least one technical skill to continue.'
            '</div>',
            unsafe_allow_html=True
        )

    # Navigation
    st.markdown('<div style="margin-top: 24px;"></div>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 3, 1])
    with col1:
        if st.button("←  Back", key="step2_back", width="stretch", type="secondary"):
            st.session_state.profile["tech_skills"] = new_selection
            st.session_state.profile["soft_skills"] = soft_skills
            st.session_state.step = 1
            st.rerun()
    with col3:
        if st.button("Next  →", key="step2_next", width="stretch", disabled=(len(new_selection) == 0)):
            st.session_state.profile["tech_skills"] = new_selection
            st.session_state.profile["soft_skills"] = soft_skills
            st.session_state.step = 3
            st.rerun()

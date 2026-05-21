"""Step 1: Profile dasar - level pengalaman, pendidikan, sertifikasi."""

import streamlit as st
from src.ui_components import render_step_indicator, render_form_header


STEP_LABELS = ["Basic", "Skills", "Preferences", "Target", "Analysis", "Results"]


def render():
    render_step_indicator(current_step=1, total_steps=6, labels=STEP_LABELS)
    render_form_header(
        "Tell us about yourself",
        "Let's start with your professional background. This helps us tailor recommendations to your career stage."
    )

    st.markdown('<div class="li-card fade-in">', unsafe_allow_html=True)

    # Experience Level
    st.markdown('<div class="li-label">Experience level</div>', unsafe_allow_html=True)
    st.markdown('<div class="li-helper" style="margin-bottom: 8px;">How many years of professional experience do you have?</div>', unsafe_allow_html=True)
    exp_options = [
        "Internship / Fresh Graduate",
        "Entry level (0-2 years)",
        "Mid level (2-5 years)",
        "Senior (5-10 years)",
        "Executive (10+ years)",
    ]
    exp_idx = 0
    if st.session_state.profile["experience_level"]:
        try:
            exp_idx = exp_options.index(st.session_state.profile["experience_level"])
        except ValueError:
            exp_idx = 0
    exp = st.radio(
        "Experience level",
        exp_options,
        index=exp_idx,
        label_visibility="collapsed",
        key="step1_exp"
    )

    st.markdown('<div style="margin-top: 20px;"></div>', unsafe_allow_html=True)

    # Education
    st.markdown('<div class="li-label">Highest education</div>', unsafe_allow_html=True)
    edu_options = ["High School", "Diploma (D3)", "Bachelor's (S1)", "Master's (S2)", "Doctorate (S3)"]
    edu_idx = 2
    if st.session_state.profile["education"]:
        try:
            edu_idx = edu_options.index(st.session_state.profile["education"])
        except ValueError:
            edu_idx = 2
    education = st.selectbox(
        "Education",
        edu_options,
        index=edu_idx,
        label_visibility="collapsed",
        key="step1_edu"
    )

    st.markdown('<div style="margin-top: 20px;"></div>', unsafe_allow_html=True)

    # Major
    st.markdown('<div class="li-label">Field of study</div>', unsafe_allow_html=True)
    major_options = [
        "Computer Science",
        "Information Systems",
        "Information Technology",
        "Data Science / Statistics",
        "Software Engineering",
        "Electrical / Computer Engineering",
        "Mathematics",
        "Business / Management",
        "Other",
    ]
    major_idx = 0
    if st.session_state.profile["major"]:
        try:
            major_idx = major_options.index(st.session_state.profile["major"])
        except ValueError:
            major_idx = 0
    major = st.selectbox(
        "Major",
        major_options,
        index=major_idx,
        label_visibility="collapsed",
        key="step1_major"
    )

    st.markdown('<div style="margin-top: 20px;"></div>', unsafe_allow_html=True)

    # Certifications
    st.markdown('<div class="li-label">Certifications (optional)</div>', unsafe_allow_html=True)
    st.markdown('<div class="li-helper" style="margin-bottom: 8px;">Select all that apply</div>', unsafe_allow_html=True)
    cert_options = [
        "AWS Certified",
        "Google Cloud Professional",
        "Microsoft Azure",
        "TensorFlow Developer",
        "Scrum / Agile",
        "PMP",
        "Cisco (CCNA/CCNP)",
        "CompTIA Security+",
        "Kubernetes (CKA/CKAD)",
        "Tableau Certified",
        "None",
    ]
    certifications = st.multiselect(
        "Certifications",
        cert_options,
        default=st.session_state.profile["certifications"],
        label_visibility="collapsed",
        key="step1_certs"
    )

    st.markdown('</div>', unsafe_allow_html=True)

    # Navigation
    st.markdown('<div style="margin-top: 24px;"></div>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 4, 1])
    with col3:
        if st.button("Next  →", key="step1_next", width="stretch"):
            st.session_state.profile["experience_level"] = exp
            st.session_state.profile["education"] = education
            st.session_state.profile["major"] = major
            st.session_state.profile["certifications"] = certifications
            st.session_state.step = 2
            st.rerun()

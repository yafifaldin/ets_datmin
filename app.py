"""
CareerMatch — IT Job Recommendation System
==========================================
Multi-page app dengan navigasi top-bar:
  - Home      : Landing page + CTA ke form
  - Recommend : Google Form wizard (6 steps)
  - Dashboard : Overview data + model performance
  - Theory    : Dasar teori + rumus LaTeX
"""

import streamlit as st
from src.ui_components import inject_css

st.set_page_config(
    page_title="CareerMatch — IT Job Recommendation",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="collapsed",
)

inject_css()

# ===== Session State =====
DEFAULTS = {
    "page": "home",   # home | recommend | dashboard | theory
    "step": 1,
    "profile": {
        "experience_level": None, "education": None, "major": None,
        "certifications": [], "tech_skills": [], "soft_skills": [],
        "work_type": "Any", "company_size": "Any", "industry": "Any",
        "min_salary": 50000, "max_salary": 150000, "target_job": None,
    },
    "submitted": False, "recommendations": None,
    "gap_analysis": None, "roadmap": None,
}
for k, v in DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ===== Top Navigation =====
from pages_logic.navbar import render_topnav
render_topnav()

# ===== Router =====
page = st.session_state.page

if page == "home":
    from pages_logic import page_home
    page_home.render()
elif page == "recommend":
    step = st.session_state.step
    if step == 1:
        from pages_logic import step_1_basics; step_1_basics.render()
    elif step == 2:
        from pages_logic import step_2_skills; step_2_skills.render()
    elif step == 3:
        from pages_logic import step_3_preferences; step_3_preferences.render()
    elif step == 4:
        from pages_logic import step_4_target; step_4_target.render()
    elif step == 5:
        from pages_logic import step_5_loading; step_5_loading.render()
    elif step == 6:
        from pages_logic import step_6_results; step_6_results.render()
    else:
        st.session_state.step = 1; st.rerun()
elif page == "dashboard":
    from pages_logic import page_dashboard
    page_dashboard.render()
elif page == "theory":
    from pages_logic import page_theory
    page_theory.render()
else:
    st.session_state.page = "home"; st.rerun()

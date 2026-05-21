"""
Step 6: Results page.

Menampilkan output lengkap sistem:
  Section 1 — Profile summary
  Section 2 — Top job recommendations (CBF output)
  Section 3 — Gap analysis ke target job
  Section 4 — Market insights (descriptive analytics)
  Section 5 — Learning roadmap
"""

import streamlit as st
import pandas as pd
import altair as alt

from src.ui_components import (
    render as _render,
    render_step_indicator, render_form_header,
    render_job_card, render_stats_row, render_section_header,
    render_skill_match_bar
)
from src.market_insights import (
    salary_distribution, salary_by_title, salary_by_experience,
    remote_distribution, top_companies, top_skills_for_title,
    applies_views_summary
)


STEP_LABELS = ["Basic", "Skills", "Preferences", "Target", "Analysis", "Results"]

# ============== Color Tokens for Charts ==============
LI_BLUE = "#0A66C2"
LI_BLUE_DARK = "#004182"
LI_BLUE_LIGHT = "#DCE6F1"
LI_SUCCESS = "#057642"
LI_WARNING = "#915907"
LI_DANGER = "#B24020"
LI_GRAY = "#666666"


def render():
    render_step_indicator(current_step=6, total_steps=6, labels=STEP_LABELS)

    # Header with restart button
    col_h1, col_h2 = st.columns([5, 1])
    with col_h1:
        render_form_header(
            "Your career matches",
            "Personalized recommendations based on your profile and the current job market."
        )
    with col_h2:
        if st.button("⟲ Reset", key="reset_btn"):
            # Clear all session state
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            # Clear cached data so next session starts fresh
            st.cache_data.clear()
            st.rerun()

    # ===== Section 1 — Profile Summary =====
    _render_profile_summary()

    # ===== Section 2 — Top Recommendations =====
    _render_recommendations()

    # ===== Section 3 — Gap Analysis =====
    _render_gap_analysis()

    # ===== Section 4 — Market Insights =====
    _render_market_insights()

    # ===== Section 5 — Learning Roadmap =====
    _render_learning_roadmap()


def _render_profile_summary():
    profile = st.session_state.profile
    render_section_header("Your profile snapshot", icon="👤")

    stats = [
        {"label": "Skills", "value": str(len(profile.get("tech_skills", [])))},
        {"label": "Experience", "value": _short_exp(profile.get("experience_level", ""))},
        {"label": "Target role", "value": profile.get("target_job", "—")},
        {"label": "Salary target",
         "value": f"${profile.get('min_salary', 0)//1000}k–${profile.get('max_salary', 0)//1000}k"},
    ]
    render_stats_row(stats)


def _short_exp(exp):
    if "Internship" in exp or "Fresh" in exp:
        return "Fresh Grad"
    if "Entry" in exp:
        return "0-2 yrs"
    if "Mid" in exp:
        return "2-5 yrs"
    if "Senior" in exp:
        return "5-10 yrs"
    if "Executive" in exp:
        return "10+ yrs"
    return exp or "—"


def _render_recommendations():
    render_section_header("Top job matches", icon="💼",
                          subtitle="Ranked by how well your skills align with each role.")

    recs = st.session_state.get("recommendations")
    if recs is None or len(recs) == 0:
        st.info("No recommendations found.")
        return

    for i, (_, job) in enumerate(recs.iterrows()):
        render_job_card(job.to_dict(), rank=i + 1)


def _render_gap_analysis():
    profile = st.session_state.profile
    gap = st.session_state.get("gap_analysis")
    if gap is None or not gap.get("found"):
        return

    render_section_header(
        f"Gap analysis · {gap['target_title']}",
        icon="🎯",
        subtitle=f"How ready you are for this role, based on {gap['n_jobs_found']:,} similar job postings."
    )

    # Match score
    st.markdown('<div class="li-card fade-in">', unsafe_allow_html=True)

    pct = gap["match_percentage"]
    n_matched = len(gap["matched"])
    n_total = len(gap["matched"]) + len(gap["missing"])

    st.markdown(
        f'<div style="margin-bottom:12px;">'
        f'<div style="font-size:15px;font-weight:600;color:var(--li-text);margin-bottom:4px;">'
        f'Skill readiness for <em>{gap["target_title"]}</em></div>'
        f'<div style="font-size:12px;color:var(--li-text-secondary);">'
        f'You have <strong>{n_matched}</strong> of <strong>{n_total}</strong> skills '
        f'commonly required across {gap["n_jobs_found"]:,} job postings for this role. '
        f'<em>(Note: job card "match %" is a ranking score based on cosine similarity — '
        f'this readiness % is your actual skill coverage.)</em>'
        f'</div>'
        f'</div>',
        unsafe_allow_html=True
    )

    render_skill_match_bar(pct, label=None)

    interpretation = _interpret_match(pct)
    st.markdown(f'<div style="margin-top:10px;font-size:13px;color:var(--li-text-secondary);">{interpretation}</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

    # Skills you have vs need
    col1, col2 = st.columns(2)
    with col1:
        _skill_box("Skills you have", gap["matched"], "have", icon="✓")
    with col2:
        _skill_box("Skills you need", gap["missing"], "miss", icon="!")

    # Priority skills (top 5 missing by demand)
    priority = gap.get("skill_priority", [])[:5]
    if priority:
        st.markdown('<div class="li-card fade-in" style="margin-top: 16px;">', unsafe_allow_html=True)
        st.markdown('<h3 class="li-h3">Most critical skills to learn next</h3>', unsafe_allow_html=True)
        st.markdown('<div class="li-helper" style="margin-bottom: 12px;">'
                    'Ranked by how frequently they appear in target job postings.</div>',
                    unsafe_allow_html=True)

        chart_df = pd.DataFrame(priority)
        chart_df["skill"] = chart_df["skill"].str.title()
        chart = alt.Chart(chart_df).mark_bar(color=LI_BLUE, cornerRadiusEnd=3).encode(
            x=alt.X("demand_pct:Q", title="% of target jobs that require this", scale=alt.Scale(domain=[0, 100])),
            y=alt.Y("skill:N", sort="-x", title=None),
            tooltip=["skill", "demand_pct"]
        ).properties(height=max(180, 40 * len(chart_df)))
        st.altair_chart(chart, width="stretch")
        st.markdown('</div>', unsafe_allow_html=True)


def _interpret_match(pct):
    if pct >= 80:
        return f"🎉 Excellent match. You're job-ready for this role. Focus on portfolio projects to stand out."
    if pct >= 60:
        return f"👍 Strong foundation. Bridge a few skill gaps and you'll be ready to apply."
    if pct >= 40:
        return f"📚 You're partway there. Focus on the top priority skills below to close the gap."
    return f"🚀 This is a stretch goal. Consider intermediate roles first, then build toward this target."


def _skill_box(title, skills, kind, icon="•"):
    if kind == "have":
        chip_class = "skill-chip-have"
        empty_msg = "No matched skills yet"
    else:
        chip_class = "skill-chip-miss"
        empty_msg = "You have all required skills!"

    chips_html = ""
    for s in skills[:15]:
        chips_html += f'<span class="skill-chip {chip_class}">{icon} {s.title()}</span>'
    if len(skills) > 15:
        chips_html += f'<span style="font-size:12px;color:var(--li-text-secondary);">+{len(skills)-15} more</span>'

    if not chips_html:
        chips_html = f'<div style="color: var(--li-text-tertiary); font-size: 13px;">{empty_msg}</div>'

    st.markdown(f"""<div class="li-card fade-in" style="margin-top: 16px; min-height: 130px;"><h3 class="li-h3" style="margin-bottom: 12px;">{title} <span style="color:var(--li-text-tertiary);font-weight:400;">({len(skills)})</span></h3><div>{chips_html}</div></div>""", unsafe_allow_html=True)


def _render_market_insights():
    from src.data_loader import load_jobs_data
    df, _ = load_jobs_data()
    if df is None or len(df) == 0:
        return

    profile = st.session_state.profile
    target = profile.get("target_job", "")

    render_section_header(
        "Market insights",
        icon="📊",
        subtitle=f"Descriptive analytics of the IT job market based on {len(df):,} postings."
    )

    # Stats row
    sal_dist = salary_distribution(df)
    remote_dist = remote_distribution(df)
    av_summary = applies_views_summary(df)

    stats = [
        {
            "label": "Median salary",
            "value": f"${int(sal_dist['median']/1000)}k" if sal_dist else "—",
            "helper": "across all IT roles"
        },
        {
            "label": "Remote roles",
            "value": f"{remote_dist.get('remote_pct', 0)}%",
            "helper": f"{remote_dist.get('remote_count', 0):,} positions"
        },
        {
            "label": "Avg applies",
            "value": f"{int(av_summary.get('avg_applies', 0))}",
            "helper": "per posting"
        },
        {
            "label": "Total postings",
            "value": f"{len(df):,}",
            "helper": "in dataset"
        },
    ]
    render_stats_row(stats)

    st.markdown('<div style="margin-top: 24px;"></div>', unsafe_allow_html=True)

    # Two-column layout for charts
    col1, col2 = st.columns(2)

    # Chart 1: Top skills in market
    with col1:
        st.markdown('<div class="li-card fade-in">', unsafe_allow_html=True)
        st.markdown('<h3 class="li-h3">Most demanded skills</h3>', unsafe_allow_html=True)
        st.markdown('<div class="li-helper" style="margin-bottom: 8px;">Across all IT job postings</div>', unsafe_allow_html=True)

        from src.gap_analysis import compute_market_skill_frequency
        top_skills_df = compute_market_skill_frequency(df, top_n=10)
        if len(top_skills_df) > 0:
            top_skills_df["skill"] = top_skills_df["skill"].str.title()
            chart = alt.Chart(top_skills_df).mark_bar(color=LI_BLUE, cornerRadiusEnd=3).encode(
                x=alt.X("frequency_pct:Q", title="% of postings"),
                y=alt.Y("skill:N", sort="-x", title=None),
                tooltip=["skill", "frequency_pct"]
            ).properties(height=300)
            st.altair_chart(chart, width="stretch")
        st.markdown('</div>', unsafe_allow_html=True)

    # Chart 2: Salary by experience
    with col2:
        st.markdown('<div class="li-card fade-in">', unsafe_allow_html=True)
        st.markdown('<h3 class="li-h3">Salary by experience</h3>', unsafe_allow_html=True)
        st.markdown('<div class="li-helper" style="margin-bottom: 8px;">Median annual compensation</div>', unsafe_allow_html=True)

        sal_exp = salary_by_experience(df)
        if len(sal_exp) > 0:
            chart = alt.Chart(sal_exp).mark_bar(color=LI_BLUE_DARK, cornerRadiusEnd=3).encode(
                x=alt.X("experience_level:N", title=None, sort=None),
                y=alt.Y("median_salary:Q", title="Median salary (USD)"),
                tooltip=["experience_level", "median_salary"]
            ).properties(height=300)
            st.altair_chart(chart, width="stretch")
        st.markdown('</div>', unsafe_allow_html=True)

    # Chart 3 + 4: Target-specific
    if target:
        col3, col4 = st.columns(2)

        with col3:
            st.markdown('<div class="li-card fade-in">', unsafe_allow_html=True)
            st.markdown(f'<h3 class="li-h3">Top skills for {target}</h3>', unsafe_allow_html=True)
            st.markdown('<div class="li-helper" style="margin-bottom: 8px;">What employers ask for</div>', unsafe_allow_html=True)

            target_skills_df, n_target = top_skills_for_title(df, target, top_n=8)
            if len(target_skills_df) > 0:
                target_skills_df["skill"] = target_skills_df["skill"].str.title()
                chart = alt.Chart(target_skills_df).mark_bar(color=LI_SUCCESS, cornerRadiusEnd=3).encode(
                    x=alt.X("frequency_pct:Q", title="% of target jobs"),
                    y=alt.Y("skill:N", sort="-x", title=None),
                    tooltip=["skill", "frequency_pct"]
                ).properties(height=280)
                st.altair_chart(chart, width="stretch")
            st.markdown('</div>', unsafe_allow_html=True)

        with col4:
            st.markdown('<div class="li-card fade-in">', unsafe_allow_html=True)
            st.markdown('<h3 class="li-h3">Top hiring companies</h3>', unsafe_allow_html=True)
            st.markdown('<div class="li-helper" style="margin-bottom: 8px;">Most active in IT recruitment</div>', unsafe_allow_html=True)

            companies = top_companies(df, top_n=8)
            if len(companies) > 0:
                chart = alt.Chart(companies).mark_bar(color=LI_BLUE, cornerRadiusEnd=3).encode(
                    x=alt.X("n_postings:Q", title="# of postings"),
                    y=alt.Y("company:N", sort="-x", title=None),
                    tooltip=["company", "n_postings"]
                ).properties(height=280)
                st.altair_chart(chart, width="stretch")
            st.markdown('</div>', unsafe_allow_html=True)

    # Chart 5: Remote vs On-site (donut equivalent: stacked bar)
    if remote_dist.get("remote_pct") is not None:
        st.markdown('<div class="li-card fade-in" style="margin-top: 16px;">', unsafe_allow_html=True)
        st.markdown('<h3 class="li-h3">Work arrangement</h3>', unsafe_allow_html=True)
        st.markdown('<div class="li-helper" style="margin-bottom: 12px;">Distribution of remote vs on-site positions</div>', unsafe_allow_html=True)

        wd_df = pd.DataFrame([
            {"type": "Remote", "pct": remote_dist["remote_pct"]},
            {"type": "On-site / Hybrid", "pct": remote_dist["onsite_pct"]},
        ])
        chart = alt.Chart(wd_df).mark_arc(innerRadius=60).encode(
            theta=alt.Theta("pct:Q"),
            color=alt.Color("type:N",
                            scale=alt.Scale(range=[LI_BLUE, LI_BLUE_LIGHT]),
                            legend=alt.Legend(title=None, orient="right")),
            tooltip=["type", "pct"]
        ).properties(height=240)
        st.altair_chart(chart, width="stretch")
        st.markdown('</div>', unsafe_allow_html=True)


def _render_learning_roadmap():
    roadmap = st.session_state.get("roadmap", [])
    if not roadmap:
        return

    profile = st.session_state.profile
    render_section_header(
        "Your learning roadmap",
        icon="🎓",
        subtitle=f"Step-by-step path to close your skill gap for {profile.get('target_job', 'your target role')}."
    )

    from src.roadmap import estimate_total_duration
    total_duration = estimate_total_duration(roadmap)

    st.markdown(f"""<div style="margin-bottom: 16px; padding: 12px 16px; background: var(--li-blue-light);border-radius: 6px; color: var(--li-blue-dark); font-size: 13px;">⏱ Estimated total duration: <strong>{total_duration}</strong>(assuming ~5 hours of study per week)</div>""", unsafe_allow_html=True)

    for step_info in roadmap:
        course = step_info.get("course")
        skill = step_info["skill"]
        demand = step_info["demand_pct"]

        if course:
            course_html = (
                '<div style="background:var(--li-bg);padding:12px 16px;border-radius:6px;margin-top:8px;">'
                f'<div style="font-weight:600;font-size:14px;color:var(--li-text);margin-bottom:4px;">📚 {course["course"]}</div>'
                f'<div style="font-size:12px;color:var(--li-text-secondary);margin-bottom:4px;">{course["provider"]} · {course["duration"]} · {course["level"]}</div>'
                f'<a href="{course["url"]}" target="_blank" style="font-size:12px;color:var(--li-blue);font-weight:600;text-decoration:none;">Open course →</a>'
                '</div>'
            )
        else:
            course_html = (
                '<div style="background:var(--li-bg);padding:12px 16px;border-radius:6px;margin-top:8px;">'
                '<div style="font-size:12px;color:var(--li-text-secondary);">No matching course in our directory. Try searching Coursera or Udemy.</div>'
                '</div>'
            )

        st.markdown(f"""<div class="li-card fade-in" style="margin-bottom: 12px;"><div style="display: flex; align-items: center; gap: 16px;"><div style="width: 32px; height: 32px; border-radius: 50%; background: var(--li-blue);color: white; display: flex; align-items: center; justify-content: center;font-weight: 700; flex-shrink: 0;">{step_info['step']}</div><div style="flex: 1;"><div style="font-weight: 600; font-size: 16px; color: var(--li-text);">{skill.title()}</div><div style="font-size: 12px; color: var(--li-text-secondary); margin-top: 2px;">Required in <strong>{demand}%</strong> of {profile.get('target_job', 'target')} positions</div></div></div>{course_html}</div>""", unsafe_allow_html=True)

    # Final CTA
    st.markdown(f"""<div class="li-card fade-in" style="margin-top: 24px; text-align: center; background: linear-gradient(135deg, var(--li-blue) 0%, var(--li-blue-dark) 100%); color: white;"><div style="font-size: 18px; font-weight: 600; margin-bottom: 8px;">You're on your way to becoming a {profile.get('target_job', 'professional')}.</div><div style="font-size: 13px; opacity: 0.9;">Bookmark this roadmap and track your progress. Come back anytime to update your profile.</div></div>""", unsafe_allow_html=True)

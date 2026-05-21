"""
UI Components Module
====================
Komponen UI reusable untuk halaman-halaman Streamlit CareerMatch.
"""

import streamlit as st
import textwrap
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
ASSETS_DIR = PROJECT_ROOT / "assets"


def _html(markup: str) -> str:
    """Strip and clean HTML for st.markdown (avoids code-block interpretation)."""
    cleaned = textwrap.dedent(markup).strip()
    lines = [line.lstrip() for line in cleaned.split("\n")]
    return "".join(lines)


def render(markup: str):
    """Shortcut: st.markdown(_html(...), unsafe_allow_html=True)."""
    st.markdown(_html(markup), unsafe_allow_html=True)


def inject_css():
    """Inject custom CSS dari assets/style.css."""
    css_path = ASSETS_DIR / "style.css"
    if css_path.exists():
        with open(css_path, "r", encoding="utf-8") as f:
            css = f.read()
        st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)


def render_navbar(subtitle: str = "IT Job Recommendation System"):
    """Top navigation bar."""
    render(f"""
        <div class="li-navbar">
            <div class="li-navbar-brand">
                <span class="li-navbar-brand-icon">in</span>
                <span>CareerMatch</span>
            </div>
            <div class="li-navbar-subtitle">{subtitle}</div>
        </div>
    """)


def render_step_indicator(current_step: int, total_steps: int = 6, labels=None):
    """Render step progress indicator."""
    if labels is None:
        labels = [f"Step {i+1}" for i in range(total_steps)]

    items_html = ""
    for i in range(total_steps):
        step_num = i + 1
        if step_num < current_step:
            cls = "step-item completed"
            content = "✓"
        elif step_num == current_step:
            cls = "step-item active"
            content = str(step_num)
        else:
            cls = "step-item"
            content = str(step_num)

        label = labels[i] if i < len(labels) else ""
        items_html += (
            f'<div class="{cls}">'
            f'<div class="step-line"></div>'
            f'<div class="step-circle">{content}</div>'
            f'<div class="step-label">{label}</div>'
            f"</div>"
        )

    render(f'<div class="step-indicator">{items_html}</div>')


def render_form_header(title: str, subtitle: str = None):
    """Form page header."""
    sub_html = f'<p class="li-subtitle">{subtitle}</p>' if subtitle else ""
    render(f'<div class="fade-in"><h1 class="li-h1">{title}</h1>{sub_html}</div>')


def render_section_header(title: str, subtitle: str = None, icon: str = None):
    """Section h2 header with optional divider."""
    icon_html = f'<span style="margin-right:8px;">{icon}</span>' if icon else ""
    sub_html = f'<p class="li-subtitle" style="margin-top:4px;">{subtitle}</p>' if subtitle else ""
    render(f"""
        <div class="section-header fade-in">
            <h2 class="li-h2">{icon_html}{title}</h2>
            {sub_html}
        </div>
    """)


def render_job_card(job: dict, rank: int = None):
    """Render a single job card."""
    match_score = job.get("match_score", 0)
    if match_score >= 80:
        pill_class = "match-pill-high"
    elif match_score >= 60:
        pill_class = "match-pill-mid"
    else:
        pill_class = "match-pill-low"

    salary = job.get("med_salary", 0)
    salary_str = f"${int(salary/1000)}k/yr" if salary and salary > 0 else "Salary undisclosed"

    remote = job.get("remote_allowed", 0)
    work_loc = "Remote" if remote == 1 else job.get("location", "—")

    title_display = f"#{rank} · {job['title']}" if rank else job["title"]

    matched_skills = job.get("matched_skills", [])
    missing_skills = job.get("missing_skills", [])

    matched_html = "".join(
        f'<span class="skill-chip skill-chip-have">✓ {s.title()}</span>'
        for s in matched_skills[:6]
    )
    if len(matched_skills) > 6:
        matched_html += f'<span style="font-size:12px;color:var(--text-muted);">+{len(matched_skills)-6} more</span>'
    if not matched_html:
        matched_html = '<span style="font-size:12px;color:var(--text-subtle);">No matched skills</span>'

    missing_html = "".join(
        f'<span class="skill-chip skill-chip-miss">{s.title()}</span>'
        for s in missing_skills[:5]
    )
    if len(missing_skills) > 5:
        missing_html += f'<span style="font-size:12px;color:var(--text-muted);">+{len(missing_skills)-5} more</span>'
    if not missing_html:
        missing_html = '<span style="font-size:12px;color:var(--text-subtle);">All required skills matched!</span>'

    company = job.get("company_name", "Company")
    exp = job.get("experience_level", "—")

    render(f"""
        <div class="job-card fade-in">
            <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:14px;">
                <div style="flex:1;min-width:0;">
                    <div class="job-card-title">{title_display}</div>
                    <div class="job-card-company">{company}</div>
                    <div class="job-card-meta">
                        <span>📍 {work_loc}</span>
                        <span>💼 {exp}</span>
                        <span>💰 {salary_str}</span>
                    </div>
                </div>
                <span class="match-pill {pill_class}" style="margin-left:12px;" title="Skill relevance score (cosine similarity). Higher = more skills overlap between your profile and this job.">{match_score}% skill match</span>
            </div>
            <div style="margin-bottom:10px;">
                <div class="li-label" style="margin-bottom:5px;">Matched skills</div>
                <div>{matched_html}</div>
            </div>
            <div>
                <div class="li-label" style="margin-bottom:5px;">Skills to develop</div>
                <div>{missing_html}</div>
            </div>
        </div>
    """)


def _stat_card_html(label: str, value: str, helper: str = None) -> str:
    """Build stat card HTML string."""
    helper_html = (
        f'<div style="font-size:11px;color:var(--text-subtle);margin-top:4px;">{helper}</div>'
        if helper else ""
    )
    return (
        f'<div class="stat-card">'
        f'<div class="stat-card-value">{value}</div>'
        f'<div class="stat-card-label">{label}</div>'
        f"{helper_html}"
        f"</div>"
    )


def render_stat_card(label: str, value: str, helper: str = None) -> str:
    """Return raw stat card HTML."""
    return _stat_card_html(label, value, helper)


def render_stats_row(stats: list):
    """Render a row of stat cards."""
    cols = st.columns(len(stats))
    for col, stat in zip(cols, stats):
        with col:
            st.markdown(
                _stat_card_html(stat["label"], stat["value"], stat.get("helper")),
                unsafe_allow_html=True,
            )


def render_skill_match_bar(match_pct: int, label: str = None):
    """Horizontal bar showing match percentage."""
    if match_pct >= 80:
        color = "var(--green)"
    elif match_pct >= 60:
        color = "var(--blue)"
    else:
        color = "var(--amber)"

    label_html = (
        f'<div class="li-label" style="margin-bottom:6px;">{label}</div>'
        if label else ""
    )

    render(f"""
        <div style="margin-bottom:12px;">
            {label_html}
            <div style="display:flex;align-items:center;gap:12px;">
                <div style="flex:1;height:6px;background:var(--divider);border-radius:3px;overflow:hidden;">
                    <div style="width:{match_pct}%;height:100%;background:{color};border-radius:3px;transition:width 0.6s var(--ease-out);"></div>
                </div>
                <div style="font-size:14px;font-weight:700;color:{color};min-width:44px;text-align:right;">{match_pct}%</div>
            </div>
        </div>
    """)


def render_info_banner(message: str, icon: str = "ℹ️"):
    """Render a subtle info banner."""
    render(f"""
        <div class="info-banner">
            <span style="flex-shrink:0;font-size:15px;">{icon}</span>
            <span>{message}</span>
        </div>
    """)


def render_empty_state(title: str, subtitle: str = None, icon: str = "🔍"):
    """Render empty / no-results state."""
    sub_html = f'<div class="empty-state-subtitle">{subtitle}</div>' if subtitle else ""
    render(f"""
        <div class="empty-state">
            <div class="empty-state-icon">{icon}</div>
            <div class="empty-state-title">{title}</div>
            {sub_html}
        </div>
    """)


def render_card_container_start():
    """Open .li-card div. Pair with render_card_container_end()."""
    st.markdown('<div class="li-card fade-in">', unsafe_allow_html=True)


def render_card_container_end():
    """Close .li-card div."""
    st.markdown("</div>", unsafe_allow_html=True)


def render_loading_animation(messages: list):
    """Render loading animation with stepped messages."""
    import time
    placeholder = st.empty()
    for msg, dur in messages:
        with placeholder.container():
            render(f"""
                <div class="loading-container fade-in">
                    <div class="loading-spinner"></div>
                    <div class="loading-text">{msg}</div>
                </div>
            """)
        time.sleep(dur)
    placeholder.empty()

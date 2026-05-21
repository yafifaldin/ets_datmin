"""
Learning Roadmap Module
=======================
Bertanggung jawab untuk:
- Mapping skill gap ke kursus rekomendasi
- Mengurutkan prioritas pembelajaran berdasarkan demand pasar
"""

import json
from pathlib import Path
from .feature_engineering import normalize_skill_name


PROJECT_ROOT = Path(__file__).parent.parent
COURSES_PATH = PROJECT_ROOT / "assets" / "roadmap_courses.json"


def load_courses():
    """Load roadmap courses dictionary dari file JSON."""
    with open(COURSES_PATH, "r", encoding="utf-8") as f:
        courses = json.load(f)
    # Normalize keys for case-insensitive lookup
    return {k.lower(): {"skill": k, **v} for k, v in courses.items()}


def get_course_for_skill(skill, courses_db=None):
    """Cari kursus yang sesuai untuk satu skill."""
    if courses_db is None:
        courses_db = load_courses()
    key = skill.lower().strip()
    return courses_db.get(key)


def build_roadmap(skill_priority, courses_db=None, max_skills=10):
    """
    Bangun learning roadmap dari hasil gap analysis.

    Args:
        skill_priority: list of dict dari gap_to_target_job
            (format: [{"skill", "demand_pct", "demand_count"}, ...])
        courses_db: dictionary kursus (optional, akan di-load otomatis)
        max_skills: jumlah maksimum skill yang dimasukkan roadmap

    Returns:
        list of dict berisi roadmap step lengkap
    """
    if courses_db is None:
        courses_db = load_courses()

    roadmap = []
    for i, item in enumerate(skill_priority[:max_skills]):
        skill = item["skill"]
        course = get_course_for_skill(skill, courses_db)

        step = {
            "step": i + 1,
            "skill": skill,
            "demand_pct": item.get("demand_pct", 0),
            "course": course,
        }
        roadmap.append(step)

    return roadmap


def estimate_total_duration(roadmap):
    """Estimasi total durasi pembelajaran berdasarkan kursus yang ada."""
    # Simple heuristic: kalau durasi mengandung "month", convert to months
    import re

    total_weeks = 0
    for step in roadmap:
        if not step.get("course"):
            continue
        duration_str = step["course"].get("duration", "")
        # Parse "X months", "X weeks", "X hours"
        months = re.search(r"(\d+)\s*month", duration_str, re.IGNORECASE)
        weeks = re.search(r"(\d+)\s*week", duration_str, re.IGNORECASE)
        hours = re.search(r"(\d+)\s*hour", duration_str, re.IGNORECASE)

        if months:
            total_weeks += int(months.group(1)) * 4
        elif weeks:
            total_weeks += int(weeks.group(1))
        elif hours:
            # Assume 5 hours/week study
            total_weeks += int(hours.group(1)) / 5

    months = total_weeks / 4
    if months < 2:
        return f"~{int(total_weeks)} minggu"
    return f"~{months:.1f} bulan"

import logging
from typing import Dict, List, Tuple

from app.services.filter import check_cgpa
from app.services.similarity import calculate_skill_score
from app.services.skill_extractor import extract_skills, rank_skills

logger = logging.getLogger(__name__)


def apply_filters(resume, jd) -> Tuple[float, List[str], List[str], Dict[str, object]]:
    reasons: List[str] = []

    resume_text = resume.extracted_text or ""
    jd_text = jd.text or ""

    resume_skills = extract_skills(resume_text)
    jd_skills = extract_skills(jd_text)

    resume_skill_set = set(resume_skills)
    jd_skill_set = set(jd_skills)
    matched_skills = rank_skills(resume_skill_set.intersection(jd_skill_set))
    missing_skills = rank_skills(jd_skill_set.difference(resume_skill_set))
    skill_score = calculate_skill_score(matched_skills, jd_skills)

    if not check_cgpa(getattr(resume, "cgpa", None), getattr(jd, "min_cgpa", None)):
        if getattr(resume, "cgpa", None) is None:
            reasons.append("CGPA missing")
        else:
            reasons.append("CGPA below requirement")

    top_missing_critical = [
        skill for skill in missing_skills if skill in {"algorithms", "data structures", "system design"}
    ][:3]
    if top_missing_critical:
        reasons.append("Missing critical skills: " + ", ".join(top_missing_critical))

    details: Dict[str, object] = {
        "resume_skills": resume_skills,
        "jd_skills": jd_skills,
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "matched_important_skills": rank_skills(matched_skills, limit=5),
        "missing_important_skills": rank_skills(missing_skills, limit=3),
        "skill_score": skill_score,
    }

    logger.info(
        "Filter results | resume_id=%s matched=%s missing=%s skill_score=%.3f",
        getattr(resume, "id", "unknown"),
        len(matched_skills),
        len(missing_skills),
        skill_score,
    )

    return skill_score, matched_skills, reasons, details

def get_matched_and_missing_skills(resume_skills, jd_skills):
    resume_set = set(resume_skills)
    jd_set = set(jd_skills)

    matched = list(resume_set.intersection(jd_set))
    missing = list(jd_set.difference(resume_set))

    return matched, missing

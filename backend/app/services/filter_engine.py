import logging
from typing import List, Tuple

from app.services.filter import check_cgpa, check_skills
from app.services.skill_extractor import extract_skills

logger = logging.getLogger(__name__)


def apply_filters(resume, jd) -> Tuple[float, List[str], List[str]]:
    logger.info("Applying filters for resume_id=%s", getattr(resume, "id", "unknown"))

    resume_text = (getattr(resume, "extracted_text", "") or "").lower()
    jd_text = (
        getattr(jd, "required_skills", None)
        or getattr(jd, "jd_skills", None)
        or getattr(jd, "text", "")
        or ""
    ).lower()

    resume_skills = extract_skills(resume_text)
    jd_skills = extract_skills(jd_text)
    matched_skills, missing_skills = check_skills(resume_skills, jd_skills)

    reasons: List[str] = []
    if not check_cgpa(getattr(resume, "cgpa", None), getattr(jd, "min_cgpa", None)):
        if getattr(resume, "cgpa", None) is None:
            reasons.append("CGPA missing")
        else:
            reasons.append("CGPA below requirement")

    if jd_skills and not resume_skills:
        reasons.append("No skills found in resume")
    elif missing_skills:
        reasons.append("Missing required skills: " + ", ".join(missing_skills))

    skill_score = len(matched_skills) / len(jd_skills) if jd_skills else 0.0
    logger.info(
        "Filter results for resume_id=%s skill_score=%.3f reasons=%s",
        getattr(resume, "id", "unknown"),
        skill_score,
        reasons,
    )
    return skill_score, matched_skills, reasons

import logging
from typing import Iterable, List, Optional, Tuple

logger = logging.getLogger(__name__)


def check_cgpa(cgpa: Optional[float], min_cgpa: Optional[float]) -> bool:
    if min_cgpa in (None, 0):
        logger.info("CGPA check skipped because job description has no minimum CGPA.")
        return True

    if cgpa is None:
        logger.info("CGPA check failed because candidate CGPA is missing.")
        return False

    passed = cgpa >= min_cgpa
    logger.info("CGPA check completed. candidate=%s minimum=%s passed=%s", cgpa, min_cgpa, passed)
    return passed


def check_skills(resume_skills: Iterable[str], jd_skills: Iterable[str]) -> Tuple[List[str], List[str]]:
    normalized_resume_skills = [skill.strip().lower() for skill in resume_skills if skill and skill.strip()]
    normalized_jd_skills = [skill.strip().lower() for skill in jd_skills if skill and skill.strip()]

    if not normalized_jd_skills:
        logger.info("Skill check skipped because no job skills were identified.")
        return [], []

    matched_skills: List[str] = []
    missing_skills: List[str] = []

    for jd_skill in normalized_jd_skills:
        is_matched = any(jd_skill in resume_skill or resume_skill in jd_skill for resume_skill in normalized_resume_skills)
        if is_matched:
            matched_skills.append(jd_skill)
        else:
            missing_skills.append(jd_skill)

    logger.info(
        "Skill check completed. matched=%s missing=%s",
        len(matched_skills),
        len(missing_skills),
    )
    return matched_skills, missing_skills

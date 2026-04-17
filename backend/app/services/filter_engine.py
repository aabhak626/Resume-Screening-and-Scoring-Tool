import logging
from typing import List, Tuple

from app.services.filter import check_cgpa, check_skills
from app.services.skill_extractor import extract_skills

logger = logging.getLogger(__name__)


def apply_filters(resume, jd):
    reasons = []

    resume_text = resume.extracted_text or ""
    jd_text = jd.text or ""

    # Extract skills properly
    resume_skills = set(extract_skills(resume_text))
    jd_skills = set(extract_skills(jd_text))

    # CORRECT MATCHING (intersection)
    matched_skills = list(resume_skills.intersection(jd_skills))

    # CGPA check 
    eligible = True
    if resume.cgpa and jd.min_cgpa and resume.cgpa < jd.min_cgpa:
        reasons.append("CGPA below requirement")
        eligible = False

    return eligible, matched_skills, reasons

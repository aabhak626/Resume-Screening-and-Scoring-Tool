import logging
from typing import Iterable, Optional

from app.services.skill_extractor import get_skill_weight, normalize_skill

logger = logging.getLogger(__name__)


def calculate_skill_score(matched_skills: Iterable[str], jd_skills: Iterable[str]) -> float:
    normalized_jd_skills = {normalize_skill(skill) for skill in jd_skills if skill and skill.strip()}
    normalized_matched_skills = {normalize_skill(skill) for skill in matched_skills if skill and skill.strip()}

    if not normalized_jd_skills:
        return 0.0

    total_weight = sum(get_skill_weight(skill) for skill in normalized_jd_skills)
    matched_weight = sum(get_skill_weight(skill) for skill in normalized_matched_skills)

    if total_weight == 0:
        return 0.0

    score = matched_weight / total_weight
    logger.info("Weighted skill score calculated: %.3f", score)
    return round(score, 3)


def calculate_cgpa_score(cgpa: Optional[float]) -> float:
    if cgpa is None:
        return 0.0
    return round(min(max(cgpa / 10.0, 0.0), 1.0), 3)


def calculate_final_score(similarity: float, cgpa: Optional[float], skill_score: float) -> float:
    safe_similarity = max(0.0, similarity or 0.0)
    safe_skill_score = max(0.0, skill_score or 0.0)
    safe_cgpa_score = calculate_cgpa_score(cgpa)
    score = round(
        (safe_similarity * 0.5) +
        (safe_skill_score * 0.4) +
        (safe_cgpa_score * 0.1),
        3,
    )
    logger.info(
        "Final ranking score calculated: %.3f | semantic=%.3f skill=%.3f cgpa=%.3f",
        score,
        safe_similarity,
        safe_skill_score,
        safe_cgpa_score,
    )
    return score


def build_score_breakdown(similarity: float, skill_score: float, cgpa: Optional[float]) -> dict:
    return {
        "semantic_score": round(max(0.0, similarity or 0.0), 3),
        "skill_score": round(max(0.0, skill_score or 0.0), 3),
        "cgpa_score": calculate_cgpa_score(cgpa),
    }


def explain_score(score: float) -> str:
    if score >= 0.75:
        return "Strong match"
    if score >= 0.55:
        return "Good match"
    if score >= 0.4:
        return "Moderate match"
    return "Weak match"

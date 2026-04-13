import logging
from typing import Optional

logger = logging.getLogger(__name__)


def calculate_final_score(similarity: float, cgpa: Optional[float]) -> float:
    safe_similarity = max(0.0, similarity or 0.0)
    safe_cgpa = cgpa if cgpa is not None else 0.0
    score = round((safe_similarity * 80) + (safe_cgpa * 2), 2)
    logger.info("Final ranking score calculated: %.2f", score)
    return score


def explain_score(score: float) -> str:
    if score > 0.8:
        return "Strong match"
    if score > 0.7:
        return "Good match"
    if score > 0.5:
        return "Weak match"
    return "Poor match"

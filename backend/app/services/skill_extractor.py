import logging
import re
from typing import List

COMMON_WORDS = [
    "experience", "knowledge", "ability", "understanding",
    "good", "strong", "working", "familiar"
]

SKILL_NORMALIZATION = {
    "ml": "machine learning",
    "ai": "artificial intelligence",
    "dl": "deep learning",
}

logger = logging.getLogger(__name__)


def extract_dynamic_skills(text: str) -> List[str]:
    try:
        if not text:
            logger.warning("Skill extraction skipped because input text is empty.")
            return []

        lines = text.lower().split("\n")
        skills: List[str] = []
        seen = set()

        for line in lines:
            if len(line) >= 100:
                continue

            words = re.findall(r"\b[a-zA-Z]+\b", line)

            for word in words:
                normalized_word = SKILL_NORMALIZATION.get(word.strip(), word.strip())
                if normalized_word in COMMON_WORDS or len(normalized_word) <= 2:
                    continue
                if normalized_word not in seen:
                    seen.add(normalized_word)
                    skills.append(normalized_word)

        logger.info("Extracted %s unique skills.", len(skills))
        return skills
    except Exception:
        logger.exception("Failed to extract skills from text.")
        return []


def extract_skills(text: str) -> List[str]:
    return extract_dynamic_skills(text)

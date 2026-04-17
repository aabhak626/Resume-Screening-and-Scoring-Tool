import logging
import re
from typing import List

logger = logging.getLogger(__name__)

# STRONG SKILL DATABASE (VERY IMPORTANT)
SKILL_DB = {
    # Programming
    "python", "java", "c", "c++", "javascript",

    # Core CS
    "data structures", "algorithms", "complexity analysis",

    # Systems
    "distributed systems", "system design", "scalability",
    "performance", "reliability",

    # Networking
    "networking", "ip networking", "tcpdump",

    # OS / infra
    "unix", "linux",

    # Data / ML
    "machine learning", "deep learning", "data analysis",
    "pandas", "numpy",

    # Web / backend
    "django", "flask", "fastapi",

    # Cloud
    "cloud computing", "aws", "gcp",

    # Tools
    "git", "github"
}

# Normalization
SKILL_NORMALIZATION = {
    "ml": "machine learning",
    "ai": "machine learning",
    "dl": "deep learning",
}


def extract_skills(text: str) -> List[str]:
    try:
        if not text:
            return []

        text = text.lower()
        found_skills = set()

        # 1. Phrase matching (MOST IMPORTANT)
        for skill in SKILL_DB:
            if skill in text:
                found_skills.add(skill)

        # 2. Word matching fallback
        words = re.findall(r"\b[a-zA-Z]+\b", text)

        for word in words:
            word = SKILL_NORMALIZATION.get(word, word)
            if word in SKILL_DB:
                found_skills.add(word)

        return list(found_skills)

    except Exception:
        logger.exception("Skill extraction failed")
        return []
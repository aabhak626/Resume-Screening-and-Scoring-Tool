import logging
import re
from typing import Iterable, List

logger = logging.getLogger(__name__)

# ROLE-BASED SKILL WEIGHTS

ROLE_SKILL_WEIGHTS = {
    "software_engineer": {
        "algorithms": 3,
        "data structures": 3,
        "system design": 3,
        "python": 2,
        "java": 2,
    },
    "product_manager": {
        "product strategy": 3,
        "roadmap": 3,
        "stakeholder management": 3,
        "user research": 2,
        "agile": 2,
        "scrum": 2,
    },
    "data_scientist": {
        "machine learning": 3,
        "data analysis": 3,
        "statistics": 3,
        "python": 2,
        "pandas": 2,
    }
}

DEFAULT_SKILL_WEIGHT = 1

# NORMALIZATION

SKILL_NORMALIZATION = {
    "ml": "machine learning",
    "ai": "artificial intelligence",
    "dl": "deep learning",
    "js": "javascript",
}

# SKILL DATABASE

SKILL_DB = {
    "python", "java", "c", "c++", "javascript",
    "data structures", "algorithms", "complexity analysis",
    "distributed systems", "system design", "scalability",
    "performance", "reliability", "networking", "ip networking", "tcpdump",
    "unix", "linux", "machine learning", "artificial intelligence",
    "deep learning", "data analysis", "pandas", "numpy",
    "django", "flask", "fastapi", "cloud computing", "aws", "gcp",
    "git", "github", "sql", "postgresql", "oop", "operating systems",
    # PM skills
    "product strategy", "roadmap", "stakeholder management",
    "user research", "agile", "scrum"
}

# REMOVE OVER-GENERIC SKILLS
COMMON_SKILLS_TO_IGNORE = {"python", "java", "c"}

# ROLE DETECTION

def detect_role(jd_text: str) -> str:
    jd_text = jd_text.lower()

    if "product manager" in jd_text:
        return "product_manager"
    elif "data scientist" in jd_text:
        return "data_scientist"
    else:
        return "software_engineer"


# --------------------------
# HELPERS
# --------------------------
def normalize_text(text: str) -> str:
    text = text.lower()

    for short, full in SKILL_NORMALIZATION.items():
        text = re.sub(rf"(?<!\w){re.escape(short)}(?!\w)", full, text)

    text = re.sub(r"[^a-z0-9+#\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def normalize_skill(skill: str) -> str:
    return re.sub(r"\s+", " ", skill.strip().lower())


def get_skill_weight(skill: str, role: str) -> int:
    skill = normalize_skill(skill)
    role_weights = ROLE_SKILL_WEIGHTS.get(role, {})

    if skill in role_weights:
        return role_weights[skill]

    return DEFAULT_SKILL_WEIGHT


def rank_skills(skills: Iterable[str], role: str, limit: int = 10) -> List[str]:
    unique = {normalize_skill(s) for s in skills if s.strip()}
    ranked = sorted(unique, key=lambda x: (-get_skill_weight(x, role), x))
    return ranked[:limit]


def build_pattern(skill: str) -> str:
    pattern = re.escape(skill).replace(r"\ ", r"\s+")
    return rf"(?<!\w){pattern}(?!\w)"

# MAIN FUNCTION

def extract_skills(text: str, role: str = "software_engineer") -> List[str]:
    try:
        if not text:
            return []

        text = normalize_text(text)
        found = set()

        for skill in SKILL_DB:
            if re.search(build_pattern(skill), text):
                found.add(skill)

        filtered = [
            s for s in found
            if normalize_skill(s) not in COMMON_SKILLS_TO_IGNORE
        ]

        return rank_skills(filtered, role)

    except Exception:
        logger.exception("Skill extraction failed")
        return []
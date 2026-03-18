import re

def extract_min_cgpa(text):
    text = text.lower()

    patterns = [
        r'cgpa\s*(?:>=|>|at least)?\s*(\d+\.?\d*)',
        r'(\d+\.?\d*)\s*cgpa',
        r'minimum\s*(\d+\.?\d*)',
        r'at least\s*(\d+\.?\d*)'
    ]

    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return float(match.group(1))

    return None


def extract_skills(text):
    skills_db = [
        "python", "java", "c++", "sql",
        "machine learning", "deep learning",
        "data analysis", "nlp", "pandas", "numpy"
    ]

    text = text.lower()

    # Try extracting from skills section
    if "skills" in text:
        text = text.split("skills")[-1][:300]

    found = []

    for skill in skills_db:
        if skill in text:
            found.append(skill)

    return list(set(found))
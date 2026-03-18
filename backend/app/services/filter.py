import re

def extract_cgpa(text):
    matches = re.findall(r'(\d+\.\d+)', text)

    if matches:
        return max([float(m) for m in matches])

    return None


def match_skills(text, required_skills):
    text = text.lower()
    matched = []

    for skill in required_skills:
        if skill.lower() in text:
            matched.append(skill)

    return matched


def check_eligibility(text, jd_data):
    cgpa = extract_cgpa(text)
    matched_skills = match_skills(text, jd_data["required_skills"])

    reasons = []
    eligible = True

    # CGPA check
    if jd_data["min_cgpa"] is not None:
        if cgpa is None or cgpa < jd_data["min_cgpa"]:
            eligible = False
            reasons.append("CGPA below requirement")

    # Skill matching (50% rule)
    required = len(jd_data["required_skills"])
    matched = len(matched_skills)

    if required > 0:
        if matched / required < 0.5:
            eligible = False
            reasons.append("Insufficient skill match")

    return {
        "eligible": eligible,
        "cgpa": cgpa,
        "matched_skills": matched_skills,
        "reasons": reasons
    }
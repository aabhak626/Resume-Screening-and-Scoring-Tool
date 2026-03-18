def check_eligibility(resume, jd):
    resume_skills = set(resume.skills.split(","))
    jd_skills = set(jd.required_skills.split(","))

    skill_match = jd_skills.issubset(resume_skills)

    cgpa_match = True
    if jd.min_cgpa:
        cgpa_match = resume.cgpa and resume.cgpa >= jd.min_cgpa

    if not cgpa_match:
        return False, "Low CGPA"

    if not skill_match:
        return False, "Missing Skills"

    return True, "Eligible"
import spacy
from spacy.matcher import PhraseMatcher

nlp = spacy.load("en_core_web_sm")


# Extract skills dynamically from JD
def extract_skills_dynamic(text):
    doc = nlp(text.lower())

    skills = set()

    for chunk in doc.noun_chunks:
        if len(chunk.text.split()) <= 3:
            skills.add(chunk.text.strip())

    return list(skills)


# Extract only JD-relevant skills from resume
def extract_relevant_skills(text, jd_skills):
    doc = nlp(text.lower())

    matcher = PhraseMatcher(nlp.vocab)
    patterns = [nlp(skill) for skill in jd_skills]
    matcher.add("JD_SKILLS", patterns)

    matches = matcher(doc)

    found = set()

    for _, start, end in matches:
        found.add(doc[start:end].text)

    return list(found)
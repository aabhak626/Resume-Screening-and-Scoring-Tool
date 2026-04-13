import re


def extract_requirements_section(text: str):
    if not text:
        return ""

    text = text.lower()

    patterns = [
        r"requirements(.*?)(responsibilities|preferred|benefits|$)",
        r"qualifications(.*?)(responsibilities|$)",
        r"skills(.*?)(responsibilities|$)"
    ]

    for pattern in patterns:
        match = re.search(pattern, text, re.DOTALL)
        if match:
            return match.group(1)

    return text


def extract_min_cgpa(text: str):
    if not text:
        return 0.0

    text = text.lower()

    patterns = [
        r'cgpa\s*[:\-]?\s*(\d\.\d+)',
        r'minimum cgpa\s*[:\-]?\s*(\d\.\d+)',
        r'(\d\.\d+)\s*cgpa'
    ]

    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return float(match.group(1))

    return 0.0
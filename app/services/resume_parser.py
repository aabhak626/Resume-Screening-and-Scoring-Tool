import logging
import re
from typing import Optional

logger = logging.getLogger(__name__)


def extract_cgpa(text: str) -> Optional[float]:
    try:
        if not text:
            logger.warning("CGPA extraction skipped because resume text is empty.")
            return None

        patterns = [
            r"\b(?:cgpa|gpa|score)\s*[:\-]?\s*(\d{1,2}(?:\.\d{1,2})?)(?:\s*/\s*10)?\b",
            r"\b(\d{1,2}(?:\.\d{1,2})?)\s*/\s*10\b",
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if not match:
                continue

            cgpa = float(match.group(1))
            if 0 <= cgpa <= 10:
                logger.info("Extracted CGPA %.2f from resume text.", cgpa)
                return cgpa

        logger.info("No valid CGPA found in resume text.")
        return None
    except Exception:
        logger.exception("Failed to extract CGPA from resume text.")
        return None

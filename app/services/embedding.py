import logging
import re
from typing import Optional

from sentence_transformers import SentenceTransformer, util

model = SentenceTransformer('all-MiniLM-L6-v2')
logger = logging.getLogger(__name__)


def clean_text(text: str) -> str:
    """Normalize text so JD and resume embeddings are built from comparable input."""
    if not text:
        return ""

    cleaned_text = text.lower()

    # Expand short forms that frequently appear in resumes and JDs differently.
    term_replacements = {
        r"\bml\b": "machine learning",
        r"\bai\b": "artificial intelligence",
    }
    for pattern, replacement in term_replacements.items():
        cleaned_text = re.sub(pattern, replacement, cleaned_text)

    # Keep alphanumeric content while removing punctuation noise from PDFs.
    cleaned_text = re.sub(r"[^a-z0-9\s]", " ", cleaned_text)
    cleaned_text = re.sub(r"\s+", " ", cleaned_text).strip()
    return cleaned_text


def get_embedding(text: str) -> Optional[object]:
    try:
        cleaned_text = clean_text(text)
        if not cleaned_text:
            logger.warning("Embedding skipped because input text is empty.")
            return None
        return model.encode(cleaned_text, convert_to_tensor=True)
    except Exception:
        logger.exception("Failed to generate embedding.")
        return None


def compute_similarity(text1: str, text2: str) -> float:
    try:
        cleaned_text1 = clean_text(text1)
        cleaned_text2 = clean_text(text2)

        if not cleaned_text1 or not cleaned_text2:
            logger.warning("Similarity computation skipped because one or both texts are empty.")
            return 0.0

        logger.info(
            "Similarity input debug | jd_length=%s | resume_length=%s | jd_preview=%r | resume_preview=%r",
            len(cleaned_text1),
            len(cleaned_text2),
            cleaned_text1[:200],
            cleaned_text2[:200],
        )

        try:
            emb1 = get_embedding(cleaned_text1)
            emb2 = get_embedding(cleaned_text2)
        except Exception:
            logger.exception("Embedding computation failed during similarity calculation.")
            return 0.0

        if emb1 is None or emb2 is None:
            logger.warning("Similarity computation returned 0.0 because embeddings could not be created.")
            return 0.0

        similarity = float(util.cos_sim(emb1, emb2))
        logger.info("Similarity computed successfully: %.3f", similarity)
        return similarity
    except Exception:
        logger.exception("Failed to compute similarity safely.")
        return 0.0

import logging
import os
from pathlib import Path

from fastapi import APIRouter, UploadFile, File
from app.database import SessionLocal
from app.models import JobDescription, Resume

from app.services.jd_parser import extract_requirements_section, extract_min_cgpa
from app.services.embedding import clean_text, compute_similarity
from app.services.filter_engine import apply_filters
from app.services.similarity import calculate_final_score, explain_score
from app.services.text_extractor import extract_text_from_file

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/hr", tags=["HR"])

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

MAX_FILE_SIZE = 2 * 1024 * 1024



# JD Upload (Improved)

@router.post("/upload-jd")
async def upload_jd(file: UploadFile = File(...)):
    db = SessionLocal()

    try:
        content = await file.read()

        if len(content) > MAX_FILE_SIZE:
            logger.warning("JD upload failed: file too large")
            return {"error": "JD file too large"}

        file_path = os.path.join(UPLOAD_FOLDER, file.filename)

        with open(file_path, "wb") as f:
            f.write(content)

        text = extract_text_from_file(file_path)

        if not text:
            logger.error("JD text extraction failed")
            return {"error": "Could not extract JD text"}

        requirements = extract_requirements_section(text) or ""
        min_cgpa = extract_min_cgpa(text)

        # Store the full JD text so similarity compares full-document context
        # instead of a short requirements-only slice.
        jd_text_for_storage = text

        if len(clean_text(requirements).split()) < 20:
            logger.info("Requirements section too short; keeping full JD text for similarity.")

        logger.info("JD parsed | min_cgpa=%s", min_cgpa)

        jd = JobDescription(
            file_path=file_path,
            text=jd_text_for_storage,
            min_cgpa=min_cgpa
        )

        db.add(jd)
        db.commit()

        return {
            "message": "JD uploaded",
            "min_cgpa": min_cgpa,
        }

    except Exception as e:
        logger.exception("Error uploading JD")
        return {"error": str(e)}

    finally:
        db.close()


# Screening 

@router.get("/screen")
def screen():
    db = SessionLocal()

    try:
        jd = db.query(JobDescription).first()
        resumes = db.query(Resume).all()

        if not jd:
            logger.warning("Screening attempted without JD")
            return {"error": "No JD uploaded"}

        if not resumes:
            logger.warning("No resumes found for screening")
            return {"error": "No resumes uploaded"}

        results = []

        for resume in resumes:
            logger.info("Screening resume_id=%s", resume.id)

            try:
                jd_text = jd.text or ""
                resume_text = resume.extracted_text or ""

                # Old rows may still contain only a short requirements snippet.
                # Re-extract the full JD text if the stored content is too small.
                if len(clean_text(jd_text).split()) < 20 and jd.file_path:
                    logger.info(
                        "Stored JD text is too short for resume_id=%s; falling back to full JD file text.",
                        resume.id,
                    )
                    jd_text = extract_text_from_file(jd.file_path) or jd_text

                cleaned_jd_text = clean_text(jd_text)
                cleaned_resume_text = clean_text(resume_text)

                logger.info(
                    "Screening text debug for resume_id=%s | jd_words=%s | resume_words=%s | jd_preview=%r | resume_preview=%r",
                    resume.id,
                    len(cleaned_jd_text.split()),
                    len(cleaned_resume_text.split()),
                    cleaned_jd_text[:200],
                    cleaned_resume_text[:200],
                )

                # Filtering 
               
                _, matched_skills, reasons = apply_filters(resume, jd)

                # Similarity
               
                try:
                    similarity = compute_similarity(cleaned_jd_text, cleaned_resume_text)
                except Exception as e:
                    logger.error("Similarity failed for resume_id=%s", resume.id)
                    similarity = 0.0
                    reasons.append("Similarity computation failed")

                # Score Calculation
                
                score = calculate_final_score(similarity, resume.cgpa or 0)

                # Robustness Check
                
                if similarity <= 0.5:
                    reasons.append("Low semantic similarity with job description")

                eligible = len(reasons) == 0

                
                # Save to DB
                
                resume.matched_skills = ",".join(matched_skills) if matched_skills else ""
                resume.score = score
                resume.eligible = eligible

                
                # Output (Improved)
            
                results.append({
                    "name": Path(resume.file_path).name if resume.file_path else f"Resume {resume.id}",
                    "status": "Eligible" if eligible else "Rejected",
                    "score": round(score, 3),
                    "explanation": explain_score(similarity),
                    "reasons": reasons if reasons else ["Eligible"],
                })

            except Exception as e:
                logger.exception("Error processing resume_id=%s", resume.id)
                results.append({
                    "name": f"Resume {resume.id}",
                    "status": "Error",
                    "score": 0,
                    "explanation": "Processing failed",
                    "reasons": [str(e)],
                })

        db.commit()

        # Sorted Output
       
        return sorted(results, key=lambda x: x["score"], reverse=True)

    finally:
        db.close()

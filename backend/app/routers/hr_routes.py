from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import JobDescription, Resume
from app.routers.auth_routes import require_admin

from app.services.jd_parser import extract_min_cgpa
from app.services.embedding import clean_text, compute_similarity
from app.services.filter_engine import apply_filters
from app.services.similarity import calculate_final_score, explain_score
from app.services.text_extractor import extract_text_from_file

import logging
import os
import json
from pathlib import Path

logger = logging.getLogger(__name__)

# MUST BE BEFORE ROUTES
router = APIRouter(prefix="/hr", tags=["HR"])

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

MAX_FILE_SIZE = 2 * 1024 * 1024

# DB Dependency

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Upload JD

@router.post("/upload-jd")
async def upload_jd(
    file: UploadFile = File(...),
    current_user=Depends(require_admin),
    db: Session = Depends(get_db)
):
    try:
        content = await file.read()

        if len(content) > MAX_FILE_SIZE:
            raise HTTPException(status_code=400, detail="JD file too large")

        file_path = os.path.join(UPLOAD_FOLDER, file.filename)

        with open(file_path, "wb") as f:
            f.write(content)

        text = extract_text_from_file(file_path)

        if not text:
            raise HTTPException(status_code=400, detail="Could not extract JD text")

        min_cgpa = extract_min_cgpa(text)

        jd = JobDescription(
            file_path=file_path,
            text=text,
            min_cgpa=min_cgpa
        )

        db.add(jd)
        db.commit()
        db.refresh(jd)

        return {
            "message": "JD uploaded successfully",
            "jd_id": jd.id,
            "min_cgpa": min_cgpa
        }

    except Exception as e:
        logger.exception("Error uploading JD")
        raise HTTPException(status_code=500, detail=str(e))

# Get All JDs

@router.get("/jds")
def list_jds(
    current_user=Depends(require_admin),
    db: Session = Depends(get_db)
):
    try:
        jds = db.query(JobDescription).all()

        return [
            {
                "id": jd.id,
                "file_path": Path(jd.file_path).name if jd.file_path else f"JD {jd.id}"
            }
            for jd in jds
        ]

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Screening 

@router.get("/screen/{jd_id}")
def screen(
    jd_id: int,
    current_user=Depends(require_admin),
    db: Session = Depends(get_db)
):
    try:
        from app.services.skill_extractor import extract_skills

        jd = db.query(JobDescription).filter(JobDescription.id == jd_id).first()
        resumes = db.query(Resume).all()

        if not jd:
            raise HTTPException(status_code=404, detail="Job description not found")

        if not resumes:
            raise HTTPException(status_code=400, detail="No resumes uploaded")

        results = []

        # Extract JD skills once
        jd_text = jd.text or ""
        jd_skills = extract_skills(jd_text)

        for resume in resumes:
            try:
                resume_text = resume.extracted_text or ""

                cleaned_jd = clean_text(jd_text)
                cleaned_resume = clean_text(resume_text)

                # Apply filters
                _, matched_skills, reasons = apply_filters(resume, jd)

                # Similarity
                try:
                    similarity = compute_similarity(cleaned_jd, cleaned_resume)
                except Exception:
                    similarity = 0.0
                    reasons.append("Similarity computation failed")

                # Score
                score = calculate_final_score(similarity, resume.cgpa or 0)

                # Missing skills
                matched_skills = matched_skills or []
                missing_skills = list(set(jd_skills) - set(matched_skills))

                # Better reasons
                improved_reasons = []

                if similarity <= 0.5:
                    improved_reasons.append("Low semantic similarity with job description")

                if missing_skills:
                    improved_reasons.append(
                        f"Missing key skills: {', '.join(missing_skills[:5])}"
                    )

                if matched_skills:
                    improved_reasons.append(
                        f"Matched skills: {', '.join(matched_skills[:5])}"
                    )

                if resume.cgpa and jd.min_cgpa and resume.cgpa < jd.min_cgpa:
                    improved_reasons.append(
                        f"CGPA below requirement ({resume.cgpa} < {jd.min_cgpa})"
                    )

                # Final eligibility
                eligible = len(improved_reasons) == 0

                # Store JSON correctly
                resume.matched_skills = json.dumps(matched_skills)

                resume.score = score
                resume.eligible = eligible

                results.append({
                    "name": Path(resume.file_path).name,
                    "status": "Eligible" if eligible else "Rejected",
                    "score": round(score, 2),
                    "matched_skills": matched_skills,
                    "missing_skills": missing_skills[:5],
                    "explanation": explain_score(similarity),
                    "reasons": improved_reasons if improved_reasons else ["Strong match"]
                })

            except Exception as e:
                logger.exception("Error processing resume")

                results.append({
                    "name": f"Resume {resume.id}",
                    "status": "Error",
                    "score": 0,
                    "explanation": "Processing failed",
                    "reasons": [str(e)]
                })

        db.commit()

        # Better sorting
        return sorted(results, key=lambda x: x["score"], reverse=True)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
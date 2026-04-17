from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import JobDescription, Resume
from app.routers.auth_routes import require_admin

from app.services.jd_parser import extract_min_cgpa
from app.services.embedding import clean_text, compute_similarity
from app.services.similarity import explain_score
from app.services.text_extractor import extract_text_from_file

# NEW IMPORTS
from app.services.skill_extractor import (
    extract_skills,
    detect_role,
    get_skill_weight
)
from app.services.filter_engine import get_matched_and_missing_skills

import logging
import os
import json
from pathlib import Path

logger = logging.getLogger(__name__)

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

# List JDs

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

# SCREENING (FINAL VERSION)

@router.get("/screen/{jd_id}")
def screen(
    jd_id: int,
    current_user=Depends(require_admin),
    db: Session = Depends(get_db)
):
    try:
        jd = db.query(JobDescription).filter(JobDescription.id == jd_id).first()
        resumes = db.query(Resume).all()

        if not jd:
            raise HTTPException(status_code=404, detail="Job description not found")

        if not resumes:
            raise HTTPException(status_code=400, detail="No resumes uploaded")

        results = []

        jd_text = jd.text or ""

        # Detect role
        role = detect_role(jd_text)

        # Extract JD skills
        jd_skills = extract_skills(jd_text, role)

        for resume in resumes:
            try:
                resume_text = resume.extracted_text or ""

                # Clean text
                cleaned_jd = clean_text(jd_text)
                cleaned_resume = clean_text(resume_text)

                # Similarity
                try:
                    similarity = compute_similarity(cleaned_jd, cleaned_resume)
                except Exception:
                    similarity = 0.0

                # Extract resume skills
                resume_skills = extract_skills(resume_text, role)

                # Correct matching
                matched_skills, missing_skills = get_matched_and_missing_skills(
                    resume_skills,
                    jd_skills
                )

                # Weighted skill score
                total_weight = sum(get_skill_weight(s, role) for s in jd_skills)
                matched_weight = sum(get_skill_weight(s, role) for s in matched_skills)

                skill_score = matched_weight / total_weight if total_weight > 0 else 0

                # Final score (hybrid)
                final_score = (0.6 * similarity) + (0.4 * skill_score)

                # Reasons
                reasons = []

                if similarity < 0.5:
                    reasons.append("Low semantic similarity")

                if missing_skills:
                    reasons.append(f"Missing skills: {', '.join(missing_skills[:3])}")

                if matched_skills:
                    reasons.append(f"Matched skills: {', '.join(matched_skills[:3])}")

                # Store JSON safely
                resume.matched_skills = json.dumps(matched_skills)
                resume.score = final_score
                resume.eligible = len(reasons) == 0

                results.append({
                    "name": Path(resume.file_path).name,
                    "role": role,
                    "status": "Eligible" if len(reasons) == 0 else "Rejected",
                    "score": round(final_score, 2),
                    "matched_skills": matched_skills[:5],
                    "missing_skills": missing_skills[:5],
                    "explanation": explain_score(similarity),
                    "reasons": reasons if reasons else ["Strong match"]
                })

            except Exception as e:
                logger.exception("Error processing resume")
                results.append({
                    "name": f"Resume {resume.id}",
                    "status": "Error",
                    "score": 0,
                    "reasons": [str(e)]
                })

        db.commit()

        return sorted(results, key=lambda x: x["score"], reverse=True)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
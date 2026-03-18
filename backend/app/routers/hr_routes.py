from fastapi import APIRouter, UploadFile, File, HTTPException
import os

from app.database import SessionLocal
from app.models import JobDescription
from app.services.resume_parser import get_resume_text
from app.services.jd_parser import extract_min_cgpa, extract_skills

router = APIRouter(prefix="/hr", tags=["HR"])

UPLOAD_FOLDER = "uploads"

@router.post("/upload-jd")
async def upload_jd(file: UploadFile = File(...)):
    db = SessionLocal()

    try:
        file_path = os.path.join(UPLOAD_FOLDER, file.filename)

        with open(file_path, "wb") as f:
            f.write(await file.read())

        text = get_resume_text(file_path)

        if not text:
            raise HTTPException(status_code=400, detail="JD text extraction failed")

        min_cgpa = extract_min_cgpa(text)
        skills = extract_skills(text)

        jd = JobDescription(
            file_path=file_path,
            min_cgpa=min_cgpa,
            required_skills=",".join(skills)
        )

        db.add(jd)
        db.commit()
        db.refresh(jd)

        return {
            "jd_id": jd.id,
            "min_cgpa": min_cgpa,
            "required_skills": skills
        }

    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="JD upload failed")

    finally:
        db.close()
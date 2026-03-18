from fastapi import APIRouter, UploadFile, File, HTTPException
import os

from app.database import SessionLocal
from app.models import Resume, JobDescription
from app.services.resume_parser import get_resume_text
from app.services.filter import check_eligibility

router = APIRouter(prefix="/user", tags=["User"])

UPLOAD_FOLDER = "uploads"

@router.post("/upload-resume")
async def upload_resume(jd_id: int, file: UploadFile = File(...)):
    db = SessionLocal()

    try:
        jd = db.query(JobDescription).filter(JobDescription.id == jd_id).first()

        if not jd:
            raise HTTPException(status_code=400, detail="Invalid jd_id")

        file_path = os.path.join(UPLOAD_FOLDER, file.filename)

        with open(file_path, "wb") as f:
            f.write(await file.read())

        text = get_resume_text(file_path)

        if not text:
            raise HTTPException(status_code=400, detail="Resume text extraction failed")

        jd_data = {
            "min_cgpa": jd.min_cgpa,
            "required_skills": jd.required_skills.split(",") if jd.required_skills else []
        }

        result = check_eligibility(text, jd_data)

        resume = Resume(
            file_path=file_path,
            extracted_text=text,
            cgpa=result["cgpa"],
            matched_skills=",".join(result["matched_skills"]),
            eligible=result["eligible"],
            jd_id=jd_id
        )

        db.add(resume)
        db.commit()

        return result

    except HTTPException as e:
        raise e

    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Internal Server Error")

    finally:
        db.close()
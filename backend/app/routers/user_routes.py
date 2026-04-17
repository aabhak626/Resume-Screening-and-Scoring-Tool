from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import Resume
from app.routers.auth_routes import get_current_user
from app.services.resume_parser import extract_cgpa
from app.services.text_extractor import extract_text_from_file
import os

router = APIRouter(prefix="/user", tags=["User"])

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

MAX_FILE_SIZE = 2 * 1024 * 1024


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/upload-resume")
async def upload_resume(
    file: UploadFile = File(...),
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        content = await file.read()

        if len(content) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=400,
                detail="File too large (max 2MB)"
            )

        file_path = os.path.join(UPLOAD_FOLDER, file.filename)

        with open(file_path, "wb") as f:
            f.write(content)

        text = extract_text_from_file(file_path)

        if not text:
            raise HTTPException(
                status_code=400,
                detail="Could not extract text from resume"
            )

        cgpa = extract_cgpa(text)

        resume = Resume(
            file_path=file_path,
            extracted_text=text,
            cgpa=cgpa,
            # Optional (recommended if model supports it)
            # user_id=current_user.id
        )

        db.add(resume)
        db.commit()

        return {
            "message": "Resume uploaded successfully",
            "uploaded_by": current_user.email
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
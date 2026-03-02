import os
from fastapi import APIRouter, UploadFile, File, HTTPException
from app.database import SessionLocal
from app.models import JobDescription

router = APIRouter(prefix="/hr", tags=["HR"])

UPLOAD_FOLDER = "uploads"

@router.post("/upload-jd")
def upload_jd(file: UploadFile = File(...)):

    allowed_extensions = ["pdf", "doc", "docx"]
    file_extension = file.filename.split(".")[-1].lower()

    if file_extension not in allowed_extensions:
        raise HTTPException(status_code=400, detail="Only PDF and Word files allowed")

    file_path = os.path.join(UPLOAD_FOLDER, file.filename)

    with open(file_path, "wb") as buffer:
        buffer.write(file.file.read())

    db = SessionLocal()

    new_jd = JobDescription(
        title=file.filename,
        description=file_path
    )

    db.add(new_jd)
    db.commit()
    db.close()

    return {"message": "Job Description uploaded successfully"}
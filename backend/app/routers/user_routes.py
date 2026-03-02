import os
from fastapi import APIRouter, UploadFile, File, HTTPException
from app.database import SessionLocal
from app.models import Resume

router = APIRouter(prefix="/user", tags=["User"])

UPLOAD_FOLDER = "uploads"

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@router.post("/upload-resume")
def upload_resume(file: UploadFile = File(...)):

    allowed_extensions = ["pdf", "doc", "docx"]
    file_extension = file.filename.split(".")[-1].lower()

    if file_extension not in allowed_extensions:
        raise HTTPException(status_code=400, detail="Only PDF and Word files allowed")

    file_path = os.path.join(UPLOAD_FOLDER, file.filename)

    with open(file_path, "wb") as buffer:
        buffer.write(file.file.read())

    db = SessionLocal()

    new_resume = Resume(
        filename=file.filename,
        user_id=1
    )

    db.add(new_resume)
    db.commit()
    db.close()

    return {"message": "Resume uploaded successfully"}
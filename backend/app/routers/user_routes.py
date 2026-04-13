from fastapi import APIRouter, UploadFile, File
from app.database import SessionLocal
from app.models import Resume
from app.services.resume_parser import extract_cgpa
from app.services.text_extractor import extract_text_from_file
import os

router = APIRouter(prefix="/user", tags=["User"])

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

MAX_FILE_SIZE = 2 * 1024 * 1024


@router.post("/upload-resume")
async def upload_resume(file: UploadFile = File(...)):
    db = SessionLocal()

    content = await file.read()

    if len(content) > MAX_FILE_SIZE:
        return {"error": "File too large"}

    file_path = os.path.join(UPLOAD_FOLDER, file.filename)

    with open(file_path, "wb") as f:
        f.write(content)

    text = extract_text_from_file(file_path)

    if not text:
        return {"error": "Could not extract text from resume"}

    cgpa = extract_cgpa(text)

    resume = Resume(
        file_path=file_path,
        extracted_text=text,
        cgpa=cgpa
    )

    db.add(resume)
    db.commit()
    db.close()

    return {"message": "Resume uploaded"}
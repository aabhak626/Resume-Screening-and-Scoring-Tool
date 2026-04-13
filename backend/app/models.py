from sqlalchemy import Column, Integer, String, Float, Boolean, Text
from app.database import Base

class JobDescription(Base):
    __tablename__ = "job_descriptions"

    id = Column(Integer, primary_key=True, index=True)
    file_path = Column(String)
    min_cgpa = Column(Float)
    text = Column(Text)

    from sqlalchemy import Column, Text

    jd_skills = Column(Text)   # store JSON string

class Resume(Base):
    __tablename__ = "resumes"

    id = Column(Integer, primary_key=True, index=True)
    file_path = Column(String)
    extracted_text = Column(Text)

    cgpa = Column(Float)
    matched_skills = Column(Text)
    score = Column(Float)

    eligible = Column(Boolean)
    jd_id = Column(Integer)
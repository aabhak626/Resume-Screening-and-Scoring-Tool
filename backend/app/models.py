from sqlalchemy import Column, Integer, String, Float, Boolean, Text
from app.database import Base

class JobDescription(Base):
    __tablename__ = "job_descriptions"

    id = Column(Integer, primary_key=True, index=True)
    file_path = Column(String, nullable=False)
    min_cgpa = Column(Float)
    required_skills = Column(Text)


class Resume(Base):
    __tablename__ = "resumes"

    id = Column(Integer, primary_key=True, index=True)
    file_path = Column(String, nullable=False)
    extracted_text = Column(Text)

    cgpa = Column(Float)
    matched_skills = Column(Text)
    eligible = Column(Boolean)

    jd_id = Column(Integer)
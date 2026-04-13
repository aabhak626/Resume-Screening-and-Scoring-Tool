from pydantic import BaseModel

class ResumeOut(BaseModel):
    id: int
    score: float
    eligible: bool

    class Config:
        from_attributes = True     
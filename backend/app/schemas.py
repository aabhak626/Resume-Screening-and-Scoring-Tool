from pydantic import BaseModel

class UserCreate(BaseModel):
    name: str
    email: str
    password: str
    role: str

class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    role: str

    class Config:
        from_attributes = True
        
class ResumeResponse(BaseModel):
    
    id: int
    filename: str
    skills: str

    class Config:
        from_attributes = True        
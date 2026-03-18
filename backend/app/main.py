from fastapi import FastAPI
from app.database import Base, engine
from app import models

from app.routers import hr_routes, user_routes

app = FastAPI()

# Create tables
Base.metadata.create_all(bind=engine)

app.include_router(hr_routes.router)
app.include_router(user_routes.router)


@app.get("/")
def root():
    return {"message": "Resume Screening API running"}
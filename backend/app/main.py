from fastapi import FastAPI
from app.database import engine, Base
from app.routers import auth_routes, user_routes, hr_routes

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Resume Screening System")

app.include_router(auth_routes.router)
app.include_router(user_routes.router)
app.include_router(hr_routes.router)

@app.get("/")
def root():
    return {"message": "Resume Screening Backend is running!"}
from fastapi import FastAPI
from app.database import Base, engine
from app import models
from app.routers import auth_routes, hr_routes, user_routes

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(auth_routes.router)
app.include_router(hr_routes.router)
app.include_router(user_routes.router)

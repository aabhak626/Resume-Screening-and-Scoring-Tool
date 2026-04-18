from app.database import SessionLocal
from app.models import User
from app.routers.auth_routes import hash_password  

db = SessionLocal()

existing = db.query(User).filter(User.email == "admin@gmail.com").first()

if not existing:
    admin = User(
        email="admin@gmail.com",
        password=hash_password("admin123"),
        role="admin"
    )

    db.add(admin)
    db.commit()

    print("Admin created successfully")
else:
    print("Admin already exists")
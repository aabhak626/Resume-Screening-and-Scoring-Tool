from app.database import SessionLocal
from app.models import User
from app.routers.auth_routes import hash_password

import os

# Create DB session
db = SessionLocal()

# Use environment variables (with defaults for easy testing)
email = os.getenv("ADMIN_EMAIL", "admin@gmail.com")
password = os.getenv("ADMIN_PASSWORD", "admin123")

try:
    # Check if admin already exists
    existing = db.query(User).filter(User.email == email).first()

    if existing:
        print("Admin already exists")
    else:
        # Create admin user
        admin = User(
            email=email,
            password=hash_password(password),
            role="admin"
        )

        db.add(admin)
        db.commit()

        print("Admin created successfully")

except Exception as e:
    print("Error creating admin:", str(e))

finally:
    db.close()
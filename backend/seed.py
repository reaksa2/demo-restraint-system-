"""
Run once to set up the database:

    python seed.py

Creates all tables (via SQLAlchemy metadata — fine for V1; switch to Alembic
migrations once the schema needs to evolve without dropping data) and the
very first LEVEL1 (developer/owner) account, using SEED_LEVEL1_* from .env.
Safe to re-run: skips user creation if that email already exists.
"""
from app.db.database import Base, engine, SessionLocal
from app.db import models  # noqa: F401 - ensures all models are registered on Base
from app.db.models.user import User, UserRole
from app.core.security import hash_password
from app.core.config import settings


def main():
    print("Creating tables...")
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        existing = db.query(User).filter(User.email == settings.SEED_LEVEL1_EMAIL).first()
        if existing:
            print(f"Level 1 user '{settings.SEED_LEVEL1_EMAIL}' already exists — skipping.")
            return

        owner = User(
            email=settings.SEED_LEVEL1_EMAIL,
            password_hash=hash_password(settings.SEED_LEVEL1_PASSWORD),
            full_name=settings.SEED_LEVEL1_NAME,
            role=UserRole.LEVEL1,
        )
        db.add(owner)
        db.commit()
        print(f"Created Level 1 user: {settings.SEED_LEVEL1_EMAIL}")
        print("IMPORTANT: log in and change this password, or set a strong one in .env before running seed.py.")
    finally:
        db.close()


if __name__ == "__main__":
    main()

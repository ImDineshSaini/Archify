"""
Quick script to make a user an admin

Usage:
    python make_admin.py <username>

Example:
    python make_admin.py testuser
"""

import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

# Load environment
load_dotenv()

def make_admin(username: str):
    """Make a user an admin"""
    database_url = os.getenv("DATABASE_URL")

    if not database_url:
        print("❌ DATABASE_URL not found in environment")
        return

    # Create database connection
    engine = create_engine(database_url)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()

    try:
        # Import User model
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from app.models.user import User

        # Find user
        user = db.query(User).filter(User.username == username).first()

        if not user:
            print(f"❌ User '{username}' not found")
            return

        if user.is_admin:
            print(f"✓ User '{username}' is already an admin")
            return

        # Make admin
        user.is_admin = True
        db.commit()

        print(f"✅ User '{username}' is now an admin!")
        print(f"   Email: {user.email}")
        print(f"   Active: {user.is_active}")

    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python make_admin.py <username>")
        sys.exit(1)

    username = sys.argv[1]
    make_admin(username)

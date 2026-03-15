#!/usr/bin/env python3
"""
Bootstrap script: create the first admin user when no users exist in the database.

Usage:
    cd backend && python create_admin.py

This script refuses to run if any user already exists, preventing misuse once
the system is bootstrapped.  After the first admin is created, additional
users should be registered through the /api/v1/auth/register endpoint.
"""

import sys
import getpass

from app.core.database import SessionLocal, engine, Base
from app.models.user import User, UserRole
from app.core.security import get_password_hash


def main() -> None:
    # Ensure tables exist
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        user_count = db.query(User).count()
        if user_count > 0:
            print(f"Error: database already contains {user_count} user(s). "
                  "Bootstrap is only allowed when no users exist.")
            sys.exit(1)

        print("=== Create first admin user ===")
        username = input("Username: ").strip()
        if not username:
            print("Error: username cannot be empty.")
            sys.exit(1)

        name = input("Display name: ").strip()
        if not name:
            print("Error: display name cannot be empty.")
            sys.exit(1)

        password = getpass.getpass("Password: ")
        if len(password) < 6:
            print("Error: password must be at least 6 characters.")
            sys.exit(1)

        password_confirm = getpass.getpass("Confirm password: ")
        if password != password_confirm:
            print("Error: passwords do not match.")
            sys.exit(1)

        admin = User(
            username=username,
            name=name,
            password_hash=get_password_hash(password),
            role=UserRole.ADMIN,
            is_active=True,
            is_superuser=True,
        )
        db.add(admin)
        db.commit()
        db.refresh(admin)

        print(f"\nAdmin user '{username}' (id={admin.id}) created successfully.")
        print("You can now log in and register additional users via the web UI.")
    finally:
        db.close()


if __name__ == "__main__":
    main()

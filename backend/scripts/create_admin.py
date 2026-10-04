"""Create an admin user:  python -m scripts.create_admin admin@hospital.com "Admin Name" """
import asyncio
import getpass
import sys

from app import models  # noqa: F401
from app.core.security import hash_password
from app.db.base import Base
from app.db.session import SessionLocal, engine
from app.models.user import Role, User
from app.repositories.user import UserRepository


async def main(email: str, full_name: str) -> None:
    password = getpass.getpass("Password (min 8 chars): ")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async with SessionLocal() as db:
        repo = UserRepository(db)
        if await repo.get_by_email(email):
            print("User already exists")
            return
        await repo.add(
            User(email=email.lower(), full_name=full_name,
                 hashed_password=hash_password(password), role=Role.ADMIN)
        )
        await db.commit()
        print("Admin created")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit('usage: python -m scripts.create_admin EMAIL "FULL NAME"')
    asyncio.run(main(sys.argv[1], sys.argv[2]))

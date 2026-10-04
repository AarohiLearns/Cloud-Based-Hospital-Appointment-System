"""Load demo data for local development:  python -m scripts.seed

Creates an admin, a demo patient and a few doctors with weekly schedules. Safe to re-run.
DEMO CREDENTIALS ONLY - never use these anywhere real.
"""
import asyncio
from datetime import time

from sqlalchemy import select

from app import models  # noqa: F401
from app.core.security import hash_password
from app.db.base import Base
from app.db.session import SessionLocal, engine
from app.models.doctor import Doctor, DoctorSchedule
from app.models.user import Role, User

ADMIN = ("admin@hospital.com", "Admin@123", "Hospital Admin")
PATIENT = ("patient@hospital.com", "Patient@123", "Demo Patient")

DOCTORS = [
    ("Dr. Asha Rao", "Cardiology", "Heart & Vascular", 30),
    ("Dr. Vikram Mehta", "Orthopedics", "Bone & Joint", 20),
    ("Dr. Neha Kapoor", "Dermatology", "Skin Care", 15),
    ("Dr. Rahul Sharma", "General Medicine", "OPD", 15),
]


async def main() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with SessionLocal() as db:
        for email, password, name in (ADMIN, PATIENT):
            exists = (await db.execute(select(User).where(User.email == email))).scalar_one_or_none()
            if not exists:
                role = Role.ADMIN if email == ADMIN[0] else Role.PATIENT
                db.add(User(email=email, full_name=name, role=role,
                            hashed_password=hash_password(password)))

        if not (await db.execute(select(Doctor))).first():
            for name, spec, dept, minutes in DOCTORS:
                schedules = [
                    DoctorSchedule(weekday=d, start_time=start, end_time=end)
                    for d in range(0, 6)  # Monday-Saturday
                    for start, end in ((time(9), time(13)), (time(14), time(17)))
                ]
                db.add(Doctor(full_name=name, specialization=spec, department=dept,
                              slot_minutes=minutes, schedules=schedules))
        await db.commit()

    print("Seed complete.")
    print(f"  Admin   : {ADMIN[0]} / {ADMIN[1]}")
    print(f"  Patient : {PATIENT[0]} / {PATIENT[1]}")


if __name__ == "__main__":
    asyncio.run(main())

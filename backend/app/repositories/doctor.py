import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.doctor import Doctor


class DoctorRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get(self, doctor_id: uuid.UUID) -> Doctor | None:
        return await self.db.get(Doctor, doctor_id)

    async def add(self, doctor: Doctor) -> Doctor:
        self.db.add(doctor)
        await self.db.flush()
        return doctor

    async def search(
        self, *, specialization: str | None, q: str | None, limit: int, offset: int
    ) -> list[Doctor]:
        stmt = select(Doctor).where(Doctor.is_active.is_(True))
        if specialization:
            stmt = stmt.where(Doctor.specialization.ilike(f"%{specialization}%"))
        if q:
            stmt = stmt.where(Doctor.full_name.ilike(f"%{q}%"))
        stmt = stmt.order_by(Doctor.full_name).limit(limit).offset(offset)
        return list((await self.db.execute(stmt)).scalars().all())

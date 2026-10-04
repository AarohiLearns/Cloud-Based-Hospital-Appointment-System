import uuid
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.appointment import Appointment, AppointmentStatus


class AppointmentRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get(self, appointment_id: uuid.UUID) -> Appointment | None:
        return await self.db.get(Appointment, appointment_id)

    async def add(self, appointment: Appointment) -> Appointment:
        self.db.add(appointment)
        await self.db.flush()  # raises IntegrityError if the slot was just taken
        return appointment

    async def booked_starts(
        self, doctor_id: uuid.UUID, start: datetime, end: datetime
    ) -> set[datetime]:
        stmt = select(Appointment.start_time).where(
            Appointment.doctor_id == doctor_id,
            Appointment.start_time >= start,
            Appointment.start_time < end,
            Appointment.status != AppointmentStatus.CANCELLED,
        )
        return set((await self.db.execute(stmt)).scalars().all())

    async def patient_has_booking_at(self, patient_id: uuid.UUID, start: datetime) -> bool:
        stmt = select(Appointment.id).where(
            Appointment.patient_id == patient_id,
            Appointment.start_time == start,
            Appointment.status != AppointmentStatus.CANCELLED,
        )
        return (await self.db.execute(stmt)).first() is not None

    async def list_for_patient(
        self, patient_id: uuid.UUID, *, limit: int, offset: int
    ) -> list[Appointment]:
        stmt = (
            select(Appointment)
            .where(Appointment.patient_id == patient_id)
            .order_by(Appointment.start_time.desc())
            .limit(limit)
            .offset(offset)
        )
        return list((await self.db.execute(stmt)).unique().scalars().all())

    async def list_for_doctor(
        self,
        doctor_id: uuid.UUID,
        *,
        start: datetime | None,
        end: datetime | None,
        limit: int,
        offset: int,
    ) -> list[Appointment]:
        stmt = select(Appointment).where(Appointment.doctor_id == doctor_id)
        if start:
            stmt = stmt.where(Appointment.start_time >= start)
        if end:
            stmt = stmt.where(Appointment.start_time < end)
        stmt = stmt.order_by(Appointment.start_time).limit(limit).offset(offset)
        return list((await self.db.execute(stmt)).unique().scalars().all())

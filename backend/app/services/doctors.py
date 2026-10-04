import uuid
from collections import defaultdict
from datetime import date, datetime

from app.core.exceptions import BusinessRuleError, NotFoundError
from app.models.doctor import Doctor, DoctorSchedule
from app.repositories.doctor import DoctorRepository
from app.schemas.doctor import DoctorCreate, ScheduleEntry
from app.services.availability import AvailabilityService


class DoctorService:
    def __init__(self, db, doctors: DoctorRepository, availability: AvailabilityService):
        self.db = db
        self.doctors = doctors
        self.availability = availability

    async def create(self, data: DoctorCreate) -> Doctor:
        doctor = Doctor(**data.model_dump(), schedules=[])
        await self.doctors.add(doctor)
        await self.db.commit()
        return doctor

    async def get(self, doctor_id: uuid.UUID) -> Doctor:
        doctor = await self.doctors.get(doctor_id)
        if doctor is None or not doctor.is_active:
            raise NotFoundError("Doctor not found")
        return doctor

    async def search(self, **filters) -> list[Doctor]:
        return await self.doctors.search(**filters)

    async def set_schedule(self, doctor_id: uuid.UUID, entries: list[ScheduleEntry]) -> Doctor:
        doctor = await self.get(doctor_id)
        by_day: dict[int, list] = defaultdict(list)
        for e in entries:
            by_day[e.weekday].append((e.start_time, e.end_time))
        for ranges in by_day.values():
            ranges.sort()
            for (_, end_a), (start_b, _) in zip(ranges, ranges[1:]):
                if start_b < end_a:
                    raise BusinessRuleError("Schedule windows on the same weekday overlap")
        doctor.schedules = [
            DoctorSchedule(weekday=e.weekday, start_time=e.start_time, end_time=e.end_time)
            for e in entries
        ]
        await self.db.commit()
        return doctor

    async def get_availability(self, doctor_id: uuid.UUID, day: date) -> tuple[Doctor, list[datetime]]:
        doctor = await self.get(doctor_id)
        return doctor, await self.availability.get_slots(doctor, day)

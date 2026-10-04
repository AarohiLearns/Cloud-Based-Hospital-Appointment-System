from datetime import date, datetime, timedelta, timezone
from zoneinfo import ZoneInfo

from app.core.config import settings
from app.models.doctor import Doctor
from app.repositories.appointment import AppointmentRepository
from app.services.slots import generate_slots


def clinic_tz() -> ZoneInfo:
    return ZoneInfo(settings.clinic_timezone)


class AvailabilityService:
    def __init__(self, appointments: AppointmentRepository):
        self.appointments = appointments

    async def get_slots(self, doctor: Doctor, day: date) -> list[datetime]:
        """Free future slots (UTC) for a doctor on a clinic-local date."""
        all_slots = generate_slots(day, doctor.schedules, doctor.slot_minutes, clinic_tz())
        if not all_slots:
            return []
        booked = await self.appointments.booked_starts(
            doctor.id, all_slots[0], all_slots[-1] + timedelta(minutes=1)
        )
        now = datetime.now(timezone.utc)
        return [s for s in all_slots if s not in booked and s > now]

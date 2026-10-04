import logging
import uuid
from datetime import date, datetime, time, timedelta, timezone

from sqlalchemy.exc import IntegrityError

from app.core.config import settings
from app.core.exceptions import (
    BusinessRuleError,
    ConflictError,
    NotFoundError,
    PermissionDeniedError,
)
from app.events.publisher import EventPublisher
from app.models.appointment import Appointment, AppointmentStatus
from app.models.user import Role, User
from app.repositories.appointment import AppointmentRepository
from app.repositories.doctor import DoctorRepository
from app.schemas.appointment import AppointmentCreate
from app.services.availability import AvailabilityService, clinic_tz

logger = logging.getLogger(__name__)


class AppointmentService:
    def __init__(
        self,
        db,
        appointments: AppointmentRepository,
        doctors: DoctorRepository,
        availability: AvailabilityService,
        publisher: EventPublisher,
    ):
        self.db = db
        self.appointments = appointments
        self.doctors = doctors
        self.availability = availability
        self.publisher = publisher

    # ---- commands ----
    async def book(self, patient: User, data: AppointmentCreate) -> Appointment:
        doctor = await self.doctors.get(data.doctor_id)
        if doctor is None or not doctor.is_active:
            raise NotFoundError("Doctor not found")

        start = data.start_time.astimezone(timezone.utc)
        now = datetime.now(timezone.utc)
        if start <= now:
            raise BusinessRuleError("Cannot book a slot in the past")
        if start > now + timedelta(days=settings.max_booking_days_ahead):
            raise BusinessRuleError(
                f"Bookings are limited to {settings.max_booking_days_ahead} days ahead"
            )

        local_day = start.astimezone(clinic_tz()).date()
        if start not in await self.availability.get_slots(doctor, local_day):
            raise ConflictError("Selected slot is not available")
        if await self.appointments.patient_has_booking_at(patient.id, start):
            raise ConflictError("You already have an appointment at this time")

        appointment = Appointment(
            patient=patient,
            doctor=doctor,
            start_time=start,
            end_time=start + timedelta(minutes=doctor.slot_minutes),
            reason=data.reason,
        )
        try:
            await self.appointments.add(appointment)
            await self.db.commit()
        except IntegrityError:
            # Another request won the race; the unique index is the final arbiter.
            await self.db.rollback()
            raise ConflictError("Selected slot was just taken")

        await self._publish("appointment.booked", appointment)
        return appointment

    async def cancel(self, user: User, appointment_id: uuid.UUID) -> Appointment:
        appointment = await self._get_for_update(user, appointment_id, allow_patient=True)
        if appointment.status != AppointmentStatus.BOOKED:
            raise BusinessRuleError("Only booked appointments can be cancelled")
        appointment.status = AppointmentStatus.CANCELLED
        await self.db.commit()
        await self._publish("appointment.cancelled", appointment)
        return appointment

    async def complete(self, user: User, appointment_id: uuid.UUID) -> Appointment:
        appointment = await self._get_for_update(user, appointment_id, allow_patient=False)
        if appointment.status != AppointmentStatus.BOOKED:
            raise BusinessRuleError("Only booked appointments can be completed")
        appointment.status = AppointmentStatus.COMPLETED
        await self.db.commit()
        await self._publish("appointment.completed", appointment)
        return appointment

    # ---- queries ----
    async def list_mine(self, user: User, *, limit: int, offset: int) -> list[Appointment]:
        return await self.appointments.list_for_patient(user.id, limit=limit, offset=offset)

    async def list_for_doctor(
        self, doctor_id: uuid.UUID, day: date | None, *, limit: int, offset: int
    ) -> list[Appointment]:
        start = end = None
        if day:
            tz = clinic_tz()
            start = datetime.combine(day, time.min, tzinfo=tz).astimezone(timezone.utc)
            end = datetime.combine(day + timedelta(days=1), time.min, tzinfo=tz).astimezone(
                timezone.utc
            )
        return await self.appointments.list_for_doctor(
            doctor_id, start=start, end=end, limit=limit, offset=offset
        )

    # ---- helpers ----
    async def _get_for_update(
        self, user: User, appointment_id: uuid.UUID, *, allow_patient: bool
    ) -> Appointment:
        appointment = await self.appointments.get(appointment_id)
        if appointment is None:
            raise NotFoundError("Appointment not found")
        is_staff = user.role in (Role.ADMIN, Role.DOCTOR)
        is_owner = allow_patient and appointment.patient_id == user.id
        if not (is_staff or is_owner):
            raise PermissionDeniedError("You cannot modify this appointment")
        return appointment

    async def _publish(self, event_type: str, appointment: Appointment) -> None:
        """Best-effort: a notification failure must never fail the booking itself."""
        try:
            await self.publisher.publish(
                event_type,
                {
                    "appointment_id": str(appointment.id),
                    "patient_email": appointment.patient.email,
                    "patient_name": appointment.patient.full_name,
                    "doctor_name": appointment.doctor.full_name,
                    "start_time": appointment.start_time.isoformat(),
                    "end_time": appointment.end_time.isoformat(),
                },
            )
        except Exception:
            logger.exception("failed to publish %s", event_type)

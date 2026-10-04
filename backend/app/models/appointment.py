import enum
import uuid
from datetime import datetime

from sqlalchemy import Enum, ForeignKey, Index, String, Uuid, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin, enum_values
from app.db.types import UTCDateTime
from app.models.doctor import Doctor
from app.models.user import User


class AppointmentStatus(str, enum.Enum):
    BOOKED = "booked"
    CANCELLED = "cancelled"
    COMPLETED = "completed"


class Appointment(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "appointments"
    __table_args__ = (
        # Database-level guarantee against double booking, even under heavy concurrency.
        Index(
            "uq_appointment_active_slot",
            "doctor_id",
            "start_time",
            unique=True,
            postgresql_where=text("status <> 'cancelled'"),
            sqlite_where=text("status <> 'cancelled'"),
        ),
        Index("ix_appointment_patient_start", "patient_id", "start_time"),
    )

    patient_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("users.id"))
    doctor_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("doctors.id"))
    start_time: Mapped[datetime] = mapped_column(UTCDateTime)
    end_time: Mapped[datetime] = mapped_column(UTCDateTime)
    status: Mapped[AppointmentStatus] = mapped_column(
        Enum(AppointmentStatus, native_enum=False, length=20, values_callable=enum_values),
        default=AppointmentStatus.BOOKED,
    )
    reason: Mapped[str | None] = mapped_column(String(500))

    doctor: Mapped[Doctor] = relationship(lazy="joined")
    patient: Mapped[User] = relationship(lazy="joined")

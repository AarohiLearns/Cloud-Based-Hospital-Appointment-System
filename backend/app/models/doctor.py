import uuid
from datetime import time

from sqlalchemy import ForeignKey, SmallInteger, String, Text, Time, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class Doctor(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "doctors"

    full_name: Mapped[str] = mapped_column(String(120))
    specialization: Mapped[str] = mapped_column(String(80), index=True)
    department: Mapped[str | None] = mapped_column(String(80))
    bio: Mapped[str | None] = mapped_column(Text)
    slot_minutes: Mapped[int] = mapped_column(SmallInteger, default=30)
    is_active: Mapped[bool] = mapped_column(default=True)

    schedules: Mapped[list["DoctorSchedule"]] = relationship(
        back_populates="doctor", cascade="all, delete-orphan", lazy="selectin"
    )


class DoctorSchedule(Base):
    """Weekly recurring working window, in the clinic's local time (0 = Monday)."""

    __tablename__ = "doctor_schedules"

    id: Mapped[int] = mapped_column(primary_key=True)
    doctor_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("doctors.id", ondelete="CASCADE"), index=True
    )
    weekday: Mapped[int] = mapped_column(SmallInteger)
    start_time: Mapped[time] = mapped_column(Time)
    end_time: Mapped[time] = mapped_column(Time)

    doctor: Mapped[Doctor] = relationship(back_populates="schedules")

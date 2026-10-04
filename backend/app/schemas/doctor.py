import uuid
from datetime import date, datetime, time

from pydantic import BaseModel, ConfigDict, Field, model_validator


class ScheduleEntry(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    weekday: int = Field(ge=0, le=6, description="0 = Monday ... 6 = Sunday")
    start_time: time
    end_time: time

    @model_validator(mode="after")
    def check_range(self):
        if self.start_time >= self.end_time:
            raise ValueError("start_time must be before end_time")
        return self


class ScheduleUpdate(BaseModel):
    entries: list[ScheduleEntry]


class DoctorCreate(BaseModel):
    full_name: str = Field(min_length=2, max_length=120)
    specialization: str = Field(min_length=2, max_length=80)
    department: str | None = Field(default=None, max_length=80)
    bio: str | None = None
    slot_minutes: int = Field(default=30, ge=5, le=240)


class DoctorBrief(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    full_name: str
    specialization: str


class DoctorOut(DoctorBrief):
    department: str | None
    bio: str | None
    slot_minutes: int
    schedules: list[ScheduleEntry]


class SlotOut(BaseModel):
    start_time: datetime
    end_time: datetime


class AvailabilityOut(BaseModel):
    doctor_id: uuid.UUID
    date: date
    timezone: str
    slots: list[SlotOut]

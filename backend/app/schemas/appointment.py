import uuid
from datetime import datetime

from pydantic import AwareDatetime, BaseModel, ConfigDict, Field

from app.models.appointment import AppointmentStatus
from app.schemas.doctor import DoctorBrief
from app.schemas.user import PatientBrief


class AppointmentCreate(BaseModel):
    doctor_id: uuid.UUID
    start_time: AwareDatetime = Field(description="Slot start, taken from the availability endpoint")
    reason: str | None = Field(default=None, max_length=500)


class AppointmentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    patient_id: uuid.UUID
    patient: PatientBrief
    doctor: DoctorBrief
    start_time: datetime
    end_time: datetime
    status: AppointmentStatus
    reason: str | None

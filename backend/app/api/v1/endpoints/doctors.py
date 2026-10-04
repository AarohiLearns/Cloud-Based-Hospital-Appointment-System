import uuid
from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, Query, status

from app.api.deps import AdminUser, get_doctor_service
from app.core.config import settings
from app.schemas.doctor import (
    AvailabilityOut,
    DoctorCreate,
    DoctorOut,
    ScheduleUpdate,
    SlotOut,
)
from app.services.doctors import DoctorService
from datetime import timedelta

router = APIRouter(prefix="/doctors", tags=["doctors"])
Svc = Annotated[DoctorService, Depends(get_doctor_service)]


@router.get("", response_model=list[DoctorOut])
async def list_doctors(
    svc: Svc,
    specialization: str | None = None,
    q: str | None = Query(default=None, description="Search by doctor name"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    return await svc.search(specialization=specialization, q=q, limit=limit, offset=offset)


@router.post("", response_model=DoctorOut, status_code=status.HTTP_201_CREATED)
async def create_doctor(data: DoctorCreate, _: AdminUser, svc: Svc):
    return await svc.create(data)


@router.get("/{doctor_id}", response_model=DoctorOut)
async def get_doctor(doctor_id: uuid.UUID, svc: Svc):
    return await svc.get(doctor_id)


@router.put("/{doctor_id}/schedule", response_model=DoctorOut)
async def set_schedule(doctor_id: uuid.UUID, data: ScheduleUpdate, _: AdminUser, svc: Svc):
    return await svc.set_schedule(doctor_id, data.entries)


@router.get("/{doctor_id}/availability", response_model=AvailabilityOut)
async def availability(
    doctor_id: uuid.UUID,
    svc: Svc,
    day: date = Query(alias="date", description="Clinic-local date, YYYY-MM-DD"),
):
    doctor, slots = await svc.get_availability(doctor_id, day)
    step = timedelta(minutes=doctor.slot_minutes)
    return AvailabilityOut(
        doctor_id=doctor.id,
        date=day,
        timezone=settings.clinic_timezone,
        slots=[SlotOut(start_time=s, end_time=s + step) for s in slots],
    )

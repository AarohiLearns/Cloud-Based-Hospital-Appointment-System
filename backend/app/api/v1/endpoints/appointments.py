import uuid
from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, Query, status

from app.api.deps import CurrentUser, StaffUser, get_appointment_service
from app.schemas.appointment import AppointmentCreate, AppointmentOut
from app.services.appointments import AppointmentService

router = APIRouter(prefix="/appointments", tags=["appointments"])
Svc = Annotated[AppointmentService, Depends(get_appointment_service)]


@router.post("", response_model=AppointmentOut, status_code=status.HTTP_201_CREATED)
async def book_appointment(data: AppointmentCreate, user: CurrentUser, svc: Svc):
    return await svc.book(user, data)


@router.get("/me", response_model=list[AppointmentOut])
async def my_appointments(
    user: CurrentUser,
    svc: Svc,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    return await svc.list_mine(user, limit=limit, offset=offset)


@router.get("", response_model=list[AppointmentOut])
async def doctor_appointments(
    _: StaffUser,
    svc: Svc,
    doctor_id: uuid.UUID,
    day: date | None = Query(default=None, alias="date"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
):
    return await svc.list_for_doctor(doctor_id, day, limit=limit, offset=offset)


@router.post("/{appointment_id}/cancel", response_model=AppointmentOut)
async def cancel_appointment(appointment_id: uuid.UUID, user: CurrentUser, svc: Svc):
    return await svc.cancel(user, appointment_id)


@router.post("/{appointment_id}/complete", response_model=AppointmentOut)
async def complete_appointment(appointment_id: uuid.UUID, user: StaffUser, svc: Svc):
    return await svc.complete(user, appointment_id)
'''appointments.py is the FastAPI route/controller file for appointments.
 It receives HTTP requests, checks/authenticates users through dependencies, and passes the actual work to AppointmentService
 appointments.py is the API/controller layer, while AppointmentService is where the actual appointment business logic lives.
'''
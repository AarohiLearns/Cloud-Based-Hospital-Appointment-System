from fastapi import APIRouter

from app.api.v1.endpoints import appointments, auth, doctors

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(doctors.router)
api_router.include_router(appointments.router)
# New feature? Add its router module under endpoints/ and include it here.

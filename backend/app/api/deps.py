import uuid
from typing import Annotated

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.exceptions import AuthenticationError, PermissionDeniedError
from app.core.security import decode_access_token
from app.db.session import get_db
from app.events.publisher import EventPublisher, get_publisher
from app.models.user import Role, User
from app.repositories.appointment import AppointmentRepository
from app.repositories.doctor import DoctorRepository
from app.repositories.user import UserRepository
from app.services.appointments import AppointmentService
from app.services.auth import AuthService
from app.services.availability import AvailabilityService
from app.services.doctors import DoctorService

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.api_v1_prefix}/auth/login")

DbSession = Annotated[AsyncSession, Depends(get_db)]


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)], db: DbSession
) -> User:
    payload = decode_access_token(token)
    try:
        user_id = uuid.UUID(payload["sub"])
    except (KeyError, ValueError):
        raise AuthenticationError("Invalid token")
    user = await UserRepository(db).get(user_id)
    if user is None or not user.is_active:
        raise AuthenticationError("User not found or inactive")
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


def require_roles(*roles: Role):
    async def checker(user: CurrentUser) -> User:
        if user.role not in roles:
            raise PermissionDeniedError("Insufficient permissions")
        return user

    return checker


AdminUser = Annotated[User, Depends(require_roles(Role.ADMIN))]
StaffUser = Annotated[User, Depends(require_roles(Role.ADMIN, Role.DOCTOR))]


# ---- service providers: the only place where the object graph is wired ----
def get_auth_service(db: DbSession) -> AuthService:
    return AuthService(db, UserRepository(db))


def get_doctor_service(db: DbSession) -> DoctorService:
    return DoctorService(db, DoctorRepository(db), AvailabilityService(AppointmentRepository(db)))


def get_appointment_service(
    db: DbSession, publisher: Annotated[EventPublisher, Depends(get_publisher)]
) -> AppointmentService:
    appointments = AppointmentRepository(db)
    return AppointmentService(
        db, appointments, DoctorRepository(db), AvailabilityService(appointments), publisher
    )

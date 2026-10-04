from typing import Annotated

from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm

from app.api.deps import CurrentUser, get_auth_service
from app.schemas.user import Token, UserCreate, UserOut
from app.services.auth import AuthService

router = APIRouter(tags=["auth"])


@router.post("/auth/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def register(data: UserCreate, svc: Annotated[AuthService, Depends(get_auth_service)]):
    return await svc.register_patient(data)


@router.post("/auth/login", response_model=Token)
async def login(
    form: Annotated[OAuth2PasswordRequestForm, Depends()],
    svc: Annotated[AuthService, Depends(get_auth_service)],
):
    return Token(access_token=await svc.login(form.username, form.password))


@router.get("/users/me", response_model=UserOut)
async def me(user: CurrentUser):
    return user

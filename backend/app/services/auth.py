from app.core.exceptions import AuthenticationError, ConflictError
from app.core.security import create_access_token, hash_password, verify_password
from app.models.user import Role, User
from app.repositories.user import UserRepository
from app.schemas.user import UserCreate


class AuthService:
    def __init__(self, db, users: UserRepository):
        self.db = db
        self.users = users

    async def register_patient(self, data: UserCreate) -> User:
        email = data.email.lower()
        if await self.users.get_by_email(email):
            raise ConflictError("Email is already registered")
        user = User(
            email=email,
            full_name=data.full_name,
            phone=data.phone,
            hashed_password=hash_password(data.password),
            role=Role.PATIENT,
        )
        await self.users.add(user)
        await self.db.commit()
        return user

    async def login(self, email: str, password: str) -> str:
        user = await self.users.get_by_email(email)
        if not user or not user.is_active or not verify_password(password, user.hashed_password):
            raise AuthenticationError("Incorrect email or password")
        return create_access_token(str(user.id), user.role.value)

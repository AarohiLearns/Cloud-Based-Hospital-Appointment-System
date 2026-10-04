import os

# Must be set before the app is imported.
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///./test.db"
os.environ["AUTO_CREATE_TABLES"] = "false"

import httpx  # noqa: E402
import pytest_asyncio  # noqa: E402

from app.core.security import hash_password  # noqa: E402
from app.db.base import Base  # noqa: E402
from app.db.session import SessionLocal, engine  # noqa: E402
from app.main import app  # noqa: E402
from app.models.user import Role, User  # noqa: E402

API = "/api/v1"


@pytest_asyncio.fixture(autouse=True)
async def fresh_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield


@pytest_asyncio.fixture
async def client():
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as c:
        yield c


async def login(client, email: str, password: str = "password123") -> dict:
    r = await client.post(f"{API}/auth/login", data={"username": email, "password": password})
    assert r.status_code == 200, r.text
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


@pytest_asyncio.fixture
async def admin_headers(client):
    async with SessionLocal() as db:
        db.add(User(email="admin@test.com", full_name="Admin", role=Role.ADMIN,
                    hashed_password=hash_password("password123")))
        await db.commit()
    return await login(client, "admin@test.com")


@pytest_asyncio.fixture
async def make_patient(client):
    async def _make(email: str) -> dict:
        r = await client.post(f"{API}/auth/register", json={
            "email": email, "full_name": "Test Patient", "password": "password123"})
        assert r.status_code == 201, r.text
        return await login(client, email)
    return _make

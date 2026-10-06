"""Test configuration and fixtures."""
import asyncio
from collections.abc import AsyncGenerator
from typing import AsyncGenerator as TypingAsyncGenerator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from mikehealth.config import Settings
from mikehealth.database import Base, db
from mikehealth.main import create_app
from mikehealth.models import User, UserRole, PatientRecord


# Test database URL (in-memory SQLite for fast tests)
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(scope="session")
def event_loop() -> asyncio.AbstractEventLoop:
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def test_engine():
    """Create test database engine."""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=False,
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest.fixture
async def test_session(test_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create test database session."""
    async_session = async_sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        yield session


@pytest.fixture
def test_settings() -> Settings:
    """Create test settings."""
    return Settings(
        environment="testing",
        debug=True,
        database_url=TEST_DATABASE_URL,
        secret_key="test-secret-key-for-testing-only-min-32-chars-long",
        cors_origins=["http://localhost:3000"],
    )


@pytest.fixture
async def test_app(test_settings, test_session):
    """Create test FastAPI app."""
    # Override database dependency
    async def override_get_db():
        yield test_session

    app = create_app()
    app.dependency_overrides[db.session] = override_get_db
    yield app
    app.dependency_overrides.clear()


@pytest.fixture
async def async_client(test_app) -> TypingAsyncGenerator[AsyncClient, None]:
    """Create async HTTP client for testing."""
    async with AsyncClient(
        transport=ASGITransport(app=test_app), base_url="http://test"
    ) as client:
        yield client


@pytest.fixture
async def test_user(test_session) -> User:
    """Create a test user."""
    from passlib.context import CryptContext
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    user = User(
        id="test-user-id",
        email="test@example.com",
        hashed_password=pwd_context.hash("password123"),
        full_name="Test User",
        role=UserRole.DOCTOR,
        is_active=True,
    )
    test_session.add(user)
    await test_session.commit()
    await test_session.refresh(user)
    return user


@pytest.fixture
async def test_patient(test_session) -> PatientRecord:
    """Create a test patient record."""
    patient = PatientRecord(
        patient_id="test-patient-id",
        name="John Doe",
        date_of_birth="1990-01-01",
        diagnoses=["I10"],
        clinical_notes="Initial visit",
        insurance_id="INS-123",
        balance_due=100.00,
    )
    test_session.add(patient)
    await test_session.commit()
    await test_session.refresh(patient)
    return patient
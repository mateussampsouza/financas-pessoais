import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app

# SQLite in-memory for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def db_session():
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()

@pytest.fixture
def register_user(client):
    """Factory fixture: registers a new user and returns their auth headers + username."""
    def _register(username="testuser", password="senha123"):
        res = client.post("/api/auth/register", json={"username": username, "password": password})
        assert res.status_code == 201, res.text
        token = res.json()["access_token"]
        return {"headers": {"Authorization": f"Bearer {token}"}, "username": username, "token": token}
    return _register

@pytest.fixture
def auth_headers(register_user):
    """Headers for a single default authenticated user, with default categories already seeded."""
    return register_user()["headers"]

@pytest.fixture
def second_user_headers(register_user):
    """Headers for a second, independent authenticated user (for isolation tests)."""
    return register_user(username="otheruser", password="outrasenha")["headers"]

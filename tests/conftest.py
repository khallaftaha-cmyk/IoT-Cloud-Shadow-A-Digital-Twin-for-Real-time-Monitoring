import sys
import os

# Add project root to sys.path so 'app' package is found automatically by pytest
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import Base, get_db

# Ensure default environment variables for testing
os.environ.setdefault("DATABASE_HOSTNAME", "localhost")
os.environ.setdefault("DATABASE_PORT", "5432")
os.environ.setdefault("DATABASE_USERNAME", "test_user")
os.environ.setdefault("DATABASE_PASSWORD", "test_password")
os.environ.setdefault("DATABASE_NAME", "test_db")
os.environ.setdefault("SECRET_KEY", "test-secret-key-1234567890")
os.environ.setdefault("ALGORITHM", "HS256")
os.environ.setdefault("ACCESS_TOKEN_EXPIRE_MINUTES", "30")
os.environ.setdefault("ANTHROPIC_API_KEY", "")

POSTGRES_URL = (
    f"postgresql://{os.getenv('DATABASE_USERNAME')}:"
    f"{os.getenv('DATABASE_PASSWORD')}@"
    f"{os.getenv('DATABASE_HOSTNAME')}:"
    f"{os.getenv('DATABASE_PORT')}/"
    f"{os.getenv('DATABASE_NAME')}"
)

# Try connecting to PostgreSQL first (CI environment); fallback to SQLite file if Postgres is not running locally
try:
    engine = create_engine(POSTGRES_URL, connect_args={"connect_timeout": 2})
    conn = engine.connect()
    conn.close()
except Exception:
    SQLITE_URL = "sqlite:///./test_temp.db"
    engine = create_engine(SQLITE_URL, connect_args={"check_same_thread": False})

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session", autouse=True)
def create_tables():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)
    if os.path.exists("./test_temp.db"):
        try:
            os.remove("./test_temp.db")
        except Exception:
            pass


@pytest.fixture()
def db():
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture()
def client(db):
    def override_get_db():
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()

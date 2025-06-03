import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from app.main import app
from app.database import Base, get_db
from app.config import settings

# Create a SQLAlchemy engine
engine = create_engine(
    settings.testing_database_url,
    echo=False,
)

# Create a sessionmaker to manage sessions
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Create tables in the database before any tests run
@pytest.fixture(scope="session", autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)  # Create all tables
    yield  # This allows the tests to run
    Base.metadata.drop_all(bind=engine)  # Drop all tables after tests


@pytest.fixture(scope="session")
def db_session():
    """Create a database session for all tests."""
    connection = engine.connect()
    session = TestingSessionLocal(bind=connection)
    yield session
    session.close()
    connection.close()


@pytest.fixture(scope="function")
def test_client(db_session):
    """Create a test client that uses the override_get_db fixture to return a session."""

    def override_get_db():
        try:
            yield db_session
        finally:
            db_session.close()

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture()
def item_payload():
    """Generate an item payload."""
    return {"owner_id": 1, "name": "Tomato", "price": 20}


@pytest.fixture()
def user_payload():
    """Generate a user payload"""
    return {"first_name": "Yusuf", "email": "yusuf@mail.com", "password": "123"}

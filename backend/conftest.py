import asyncio
import os
import tempfile
from typing import AsyncGenerator, Generator

import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.db.database import Base, get_async_session
from app.core.config import settings
from app.core.security import create_access_token
from app.models.user import User
from app.models.project import Project


# Test database URL
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

# Test engine with in-memory SQLite
test_engine = create_async_engine(
    TEST_DATABASE_URL,
    echo=False,
    poolclass=StaticPool,
    connect_args={"check_same_thread": False},
)

# Test session maker
TestSessionLocal = async_sessionmaker(
    test_engine,
    class_=AsyncSession,
    expire_on_commit=False
)


@pytest_asyncio.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Create test database session"""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async with TestSessionLocal() as session:
        yield session
    
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Create test client with database session override"""
    def get_test_db():
        return db_session
    
    app.dependency_overrides[get_async_session] = get_test_db
    
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
    
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def test_user(db_session: AsyncSession) -> User:
    """Create a test user"""
    from app.services.user_service import UserService
    
    user_service = UserService(db_session)
    user = await user_service.create(
        email="test@example.com",
        full_name="Test User",
        password="testpassword123"
    )
    return user


@pytest_asyncio.fixture
async def test_superuser(db_session: AsyncSession) -> User:
    """Create a test superuser"""
    from app.services.user_service import UserService
    
    user_service = UserService(db_session)
    user = await user_service.create(
        email="admin@example.com",
        full_name="Admin User",
        password="adminpassword123",
        is_superuser=True
    )
    return user


@pytest_asyncio.fixture
async def test_project(db_session: AsyncSession, test_user: User) -> Project:
    """Create a test project"""
    from app.services.project_service import ProjectService
    
    project_service = ProjectService(db_session)
    project = await project_service.create(
        user_id=test_user.id,
        name="Test Project",
        description="A test project for testing purposes"
    )
    return project


@pytest.fixture
def auth_headers(test_user: User) -> dict:
    """Create authorization headers for test user"""
    access_token = create_access_token(subject=test_user.id)
    return {"Authorization": f"Bearer {access_token}"}


@pytest.fixture
def superuser_auth_headers(test_superuser: User) -> dict:
    """Create authorization headers for test superuser"""
    access_token = create_access_token(subject=test_superuser.id)
    return {"Authorization": f"Bearer {access_token}"}


@pytest.fixture
def temp_file() -> Generator[str, None, None]:
    """Create a temporary file for testing"""
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        tmp.write(b"test content")
        tmp.flush()
        yield tmp.name
    
    # Cleanup
    if os.path.exists(tmp.name):
        os.unlink(tmp.name)


@pytest.fixture
def mock_api_responses():
    """Mock external API responses"""
    return {
        "google_search": {
            "items": [
                {
                    "title": "Test Result 1",
                    "snippet": "Test snippet 1",
                    "link": "https://example.com/1"
                },
                {
                    "title": "Test Result 2", 
                    "snippet": "Test snippet 2",
                    "link": "https://example.com/2"
                }
            ]
        },
        "yandex_search": {
            "grouping": [{
                "groups": [
                    {
                        "doclist": [{
                            "title": "Yandex Test Result",
                            "url": "https://yandex-example.com",
                            "content": "Yandex test snippet"
                        }]
                    }
                ]
            }]
        }
    }


@pytest.fixture
def sample_text_data():
    """Sample text data for analysis testing"""
    return [
        "I really love this product, it's amazing!",
        "This software is terrible, too many bugs.",
        "Great user interface, very intuitive.",
        "Poor customer service experience.",
        "Excellent features and functionality.",
        "The app crashes frequently, very frustrating.",
        "Outstanding performance and reliability.",
        "Difficult to use, confusing navigation."
    ]


@pytest.fixture
def sample_analysis_results():
    """Sample analysis results for testing"""
    return {
        "sentiment": {
            "total_analyzed": 100,
            "average_score": 0.2,
            "score_range": [-1.0, 1.0],
            "sentiment_distribution": {
                "positive": {"count": 40, "percentage": 40.0},
                "negative": {"count": 35, "percentage": 35.0},
                "neutral": {"count": 25, "percentage": 25.0}
            },
            "top_pain_points": [
                {"pain_point": "Software bugs", "frequency": 15},
                {"pain_point": "Poor performance", "frequency": 12},
                {"pain_point": "Bad UI/UX", "frequency": 8}
            ]
        },
        "clustering": {
            "total_clusters": 5,
            "avg_cluster_size": 20.0,
            "cluster_details": [
                {
                    "cluster_id": 0,
                    "size": 25,
                    "description": "Performance issues",
                    "keywords": ["slow", "lag", "performance", "speed"],
                    "avg_sentiment": -0.6
                },
                {
                    "cluster_id": 1,
                    "size": 20,
                    "description": "User interface feedback",
                    "keywords": ["UI", "interface", "design", "layout"],
                    "avg_sentiment": 0.3
                }
            ]
        },
        "frequency": {
            "total_terms": 500,
            "top_terms": [
                {"term": "bug", "frequency": 25, "tf_idf_score": 0.85},
                {"term": "slow", "frequency": 20, "tf_idf_score": 0.78},
                {"term": "feature", "frequency": 18, "tf_idf_score": 0.72}
            ]
        }
    }


# Override settings for testing
@pytest.fixture(autouse=True)
def override_settings():
    """Override settings for testing"""
    # Store original values
    original_database_url = settings.ASYNC_DATABASE_URL
    original_debug = settings.DEBUG
    
    # Set test values
    settings.ASYNC_DATABASE_URL = TEST_DATABASE_URL
    settings.DEBUG = True
    
    yield
    
    # Restore original values
    settings.ASYNC_DATABASE_URL = original_database_url
    settings.DEBUG = original_debug


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()
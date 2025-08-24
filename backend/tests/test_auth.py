import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import verify_password
from app.models.user import User


class TestAuthEndpoints:
    """Тесты эндпоинтов аутентификации"""

    @pytest.mark.asyncio
    async def test_register_new_user(self, client: AsyncClient):
        """Тест регистрации пользователя"""
        user_data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "newpassword123",
            "full_name": "New User"
        }
        
        response = await client.post("/api/v1/auth/register", json=user_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["username"] == user_data["username"]
        assert data["email"] == user_data["email"]
        assert data["full_name"] == user_data["full_name"]
        assert data["is_active"] is True

    @pytest.mark.asyncio
    async def test_login_valid_credentials(self, client: AsyncClient, test_user: User):
        """Тест авторизации с валидными данными"""
        login_data = {
            "username": test_user.username,
            "password": "testpassword123"
        }
        
        response = await client.post(
            "/api/v1/auth/login",
            data=login_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    @pytest.mark.asyncio
    async def test_login_invalid_credentials(self, client: AsyncClient):
        """Тест авторизации с неверными данными"""
        login_data = {
            "username": "nonexistent",
            "password": "wrongpassword"
        }
        
        response = await client.post(
            "/api/v1/auth/login",
            data=login_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        assert response.status_code == 401
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import verify_password
from app.models.user import User


class TestAuthEndpoints:
    """Test authentication endpoints"""

    @pytest.mark.asyncio
    @pytest.mark.auth
    async def test_register_new_user(self, client: AsyncClient):
        """Test user registration"""
        user_data = {
            "email": "newuser@example.com",
            "password": "newpassword123",
            "full_name": "New User"
        }
        
        response = await client.post("/api/v1/auth/register", json=user_data)
        
        assert response.status_code == 201
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
        assert data["user"]["email"] == user_data["email"]
        assert data["user"]["full_name"] == user_data["full_name"]
        assert data["user"]["is_active"] is True

    @pytest.mark.asyncio
    @pytest.mark.auth
    async def test_register_duplicate_email(self, client: AsyncClient, test_user: User):
        """Test registration with existing email"""
        user_data = {
            "email": test_user.email,
            "password": "somepassword123",
            "full_name": "Another User"
        }
        
        response = await client.post("/api/v1/auth/register", json=user_data)
        
        assert response.status_code == 400
        assert "already registered" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    @pytest.mark.auth
    async def test_register_invalid_email(self, client: AsyncClient):
        """Test registration with invalid email format"""
        user_data = {
            "email": "invalid-email",
            "password": "password123",
            "full_name": "Test User"
        }
        
        response = await client.post("/api/v1/auth/register", json=user_data)
        
        assert response.status_code == 422

    @pytest.mark.asyncio
    @pytest.mark.auth
    async def test_register_weak_password(self, client: AsyncClient):
        """Test registration with weak password"""
        user_data = {
            "email": "testuser@example.com",
            "password": "123",  # Too short
            "full_name": "Test User"
        }
        
        response = await client.post("/api/v1/auth/register", json=user_data)
        
        assert response.status_code == 422

    @pytest.mark.asyncio
    @pytest.mark.auth
    async def test_login_valid_credentials(self, client: AsyncClient, test_user: User):
        """Test login with valid credentials"""
        login_data = {
            "username": test_user.email,
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
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"

    @pytest.mark.asyncio
    @pytest.mark.auth
    async def test_login_invalid_email(self, client: AsyncClient):
        """Test login with non-existent email"""
        login_data = {
            "username": "nonexistent@example.com",
            "password": "password123"
        }
        
        response = await client.post(
            "/api/v1/auth/login",
            data=login_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        assert response.status_code == 401
        assert "incorrect" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    @pytest.mark.auth
    async def test_login_invalid_password(self, client: AsyncClient, test_user: User):
        """Test login with wrong password"""
        login_data = {
            "username": test_user.email,
            "password": "wrongpassword"
        }
        
        response = await client.post(
            "/api/v1/auth/login",
            data=login_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        assert response.status_code == 401
        assert "incorrect" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    @pytest.mark.auth
    async def test_get_current_user(self, client: AsyncClient, auth_headers: dict):
        """Test getting current user information"""
        response = await client.get("/api/v1/auth/me", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "email" in data
        assert "full_name" in data
        assert "is_active" in data
        assert data["email"] == "test@example.com"

    @pytest.mark.asyncio
    @pytest.mark.auth
    async def test_get_current_user_no_token(self, client: AsyncClient):
        """Test getting current user without token"""
        response = await client.get("/api/v1/auth/me")
        
        assert response.status_code == 401

    @pytest.mark.asyncio
    @pytest.mark.auth
    async def test_get_current_user_invalid_token(self, client: AsyncClient):
        """Test getting current user with invalid token"""
        headers = {"Authorization": "Bearer invalid_token"}
        response = await client.get("/api/v1/auth/me", headers=headers)
        
        assert response.status_code == 401

    @pytest.mark.asyncio
    @pytest.mark.auth
    async def test_refresh_token_valid(self, client: AsyncClient, test_user: User):
        """Test refreshing token with valid refresh token"""
        # First login to get refresh token
        login_data = {
            "username": test_user.email,
            "password": "testpassword123"
        }
        
        login_response = await client.post(
            "/api/v1/auth/login",
            data=login_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        refresh_token = login_response.json()["refresh_token"]
        
        # Test refresh
        refresh_data = {"refresh_token": refresh_token}
        response = await client.post("/api/v1/auth/refresh", json=refresh_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data

    @pytest.mark.asyncio
    @pytest.mark.auth
    async def test_refresh_token_invalid(self, client: AsyncClient):
        """Test refreshing token with invalid refresh token"""
        refresh_data = {"refresh_token": "invalid_refresh_token"}
        response = await client.post("/api/v1/auth/refresh", json=refresh_data)
        
        assert response.status_code == 401

    @pytest.mark.asyncio
    @pytest.mark.auth
    async def test_logout(self, client: AsyncClient, auth_headers: dict):
        """Test user logout"""
        response = await client.post("/api/v1/auth/logout", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data


class TestPasswordSecurity:
    """Test password security functions"""

    def test_password_hashing(self):
        """Test password hashing and verification"""
        from app.core.security import get_password_hash, verify_password
        
        password = "testpassword123"
        hashed = get_password_hash(password)
        
        assert hashed != password
        assert verify_password(password, hashed) is True
        assert verify_password("wrongpassword", hashed) is False

    def test_password_hash_different_each_time(self):
        """Test that password hashing produces different hashes"""
        from app.core.security import get_password_hash
        
        password = "testpassword123"
        hash1 = get_password_hash(password)
        hash2 = get_password_hash(password)
        
        assert hash1 != hash2

    def test_jwt_token_creation_and_verification(self):
        """Test JWT token creation and verification"""
        from app.core.security import create_access_token, verify_token
        
        user_id = 123
        token = create_access_token(subject=user_id)
        
        assert token is not None
        assert isinstance(token, str)
        
        # Verify token
        payload = verify_token(token)
        assert payload is not None
        assert payload.get("sub") == str(user_id)

    def test_invalid_jwt_token(self):
        """Test verification of invalid JWT token"""
        from app.core.security import verify_token
        
        invalid_token = "invalid.jwt.token"
        payload = verify_token(invalid_token)
        
        assert payload is None
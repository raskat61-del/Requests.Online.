import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.models.project import Project


class TestProjectEndpoints:
    """Test project management endpoints"""

    @pytest.mark.asyncio
    @pytest.mark.api
    async def test_create_project(self, client: AsyncClient, auth_headers: dict):
        """Test creating a new project"""
        project_data = {
            "name": "New Test Project",
            "description": "A project for testing purposes",
            "status": "active"
        }
        
        response = await client.post(
            "/api/v1/projects/",
            json=project_data,
            headers=auth_headers
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == project_data["name"]
        assert data["description"] == project_data["description"]
        assert data["status"] == project_data["status"]
        assert "id" in data
        assert "created_at" in data

    @pytest.mark.asyncio
    @pytest.mark.api
    async def test_create_project_no_auth(self, client: AsyncClient):
        """Test creating project without authentication"""
        project_data = {
            "name": "Unauthorized Project",
            "description": "This should fail"
        }
        
        response = await client.post("/api/v1/projects/", json=project_data)
        
        assert response.status_code == 401

    @pytest.mark.asyncio
    @pytest.mark.api
    async def test_create_project_invalid_data(self, client: AsyncClient, auth_headers: dict):
        """Test creating project with invalid data"""
        project_data = {
            "name": "",  # Empty name should fail
            "description": "Valid description"
        }
        
        response = await client.post(
            "/api/v1/projects/",
            json=project_data,
            headers=auth_headers
        )
        
        assert response.status_code == 422

    @pytest.mark.asyncio
    @pytest.mark.api
    async def test_get_projects(self, client: AsyncClient, auth_headers: dict, test_project: Project):
        """Test getting list of user projects"""
        response = await client.get("/api/v1/projects/", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        
        # Check if test project is in the list
        project_names = [proj["name"] for proj in data]
        assert test_project.name in project_names

    @pytest.mark.asyncio
    @pytest.mark.api
    async def test_get_projects_with_filters(self, client: AsyncClient, auth_headers: dict):
        """Test getting projects with query parameters"""
        response = await client.get(
            "/api/v1/projects/",
            params={"limit": 5, "skip": 0, "status": "active"},
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) <= 5

    @pytest.mark.asyncio
    @pytest.mark.api
    async def test_get_project_by_id(self, client: AsyncClient, auth_headers: dict, test_project: Project):
        """Test getting specific project by ID"""
        response = await client.get(
            f"/api/v1/projects/{test_project.id}",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_project.id
        assert data["name"] == test_project.name
        assert data["description"] == test_project.description
        assert "stats" in data

    @pytest.mark.asyncio
    @pytest.mark.api
    async def test_get_nonexistent_project(self, client: AsyncClient, auth_headers: dict):
        """Test getting non-existent project"""
        response = await client.get(
            "/api/v1/projects/99999",
            headers=auth_headers
        )
        
        assert response.status_code == 404

    @pytest.mark.asyncio
    @pytest.mark.api
    async def test_get_project_unauthorized(self, client: AsyncClient, test_project: Project):
        """Test getting project without authentication"""
        response = await client.get(f"/api/v1/projects/{test_project.id}")
        
        assert response.status_code == 401

    @pytest.mark.asyncio
    @pytest.mark.api
    async def test_update_project(self, client: AsyncClient, auth_headers: dict, test_project: Project):
        """Test updating a project"""
        update_data = {
            "name": "Updated Project Name",
            "description": "Updated description",
            "status": "completed"
        }
        
        response = await client.put(
            f"/api/v1/projects/{test_project.id}",
            json=update_data,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == update_data["name"]
        assert data["description"] == update_data["description"]
        assert data["status"] == update_data["status"]

    @pytest.mark.asyncio
    @pytest.mark.api
    async def test_update_project_partial(self, client: AsyncClient, auth_headers: dict, test_project: Project):
        """Test partially updating a project"""
        update_data = {
            "status": "paused"
        }
        
        response = await client.put(
            f"/api/v1/projects/{test_project.id}",
            json=update_data,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == update_data["status"]
        assert data["name"] == test_project.name  # Should remain unchanged

    @pytest.mark.asyncio
    @pytest.mark.api
    async def test_delete_project(self, client: AsyncClient, auth_headers: dict, test_project: Project):
        """Test deleting a project"""
        response = await client.delete(
            f"/api/v1/projects/{test_project.id}",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        
        # Verify project is deleted
        get_response = await client.get(
            f"/api/v1/projects/{test_project.id}",
            headers=auth_headers
        )
        assert get_response.status_code == 404

    @pytest.mark.asyncio
    @pytest.mark.api
    async def test_delete_nonexistent_project(self, client: AsyncClient, auth_headers: dict):
        """Test deleting non-existent project"""
        response = await client.delete(
            "/api/v1/projects/99999",
            headers=auth_headers
        )
        
        assert response.status_code == 404


class TestProjectPermissions:
    """Test project access permissions"""

    @pytest.mark.asyncio
    @pytest.mark.api
    async def test_user_cannot_access_other_user_project(
        self, 
        client: AsyncClient, 
        db_session: AsyncSession,
        test_project: Project
    ):
        """Test that users cannot access projects owned by others"""
        # Create another user
        from app.services.user_service import UserService
        from app.core.security import create_access_token
        
        user_service = UserService(db_session)
        other_user = await user_service.create(
            email="other@example.com",
            full_name="Other User",
            password="otherpassword123"
        )
        
        # Create auth headers for the other user
        access_token = create_access_token(subject=other_user.id)
        other_auth_headers = {"Authorization": f"Bearer {access_token}"}
        
        # Try to access test_project (owned by test_user)
        response = await client.get(
            f"/api/v1/projects/{test_project.id}",
            headers=other_auth_headers
        )
        
        assert response.status_code == 403

    @pytest.mark.asyncio
    @pytest.mark.api
    async def test_user_cannot_update_other_user_project(
        self, 
        client: AsyncClient, 
        db_session: AsyncSession,
        test_project: Project
    ):
        """Test that users cannot update projects owned by others"""
        # Create another user
        from app.services.user_service import UserService
        from app.core.security import create_access_token
        
        user_service = UserService(db_session)
        other_user = await user_service.create(
            email="another@example.com",
            full_name="Another User",
            password="anotherpassword123"
        )
        
        # Create auth headers for the other user
        access_token = create_access_token(subject=other_user.id)
        other_auth_headers = {"Authorization": f"Bearer {access_token}"}
        
        # Try to update test_project (owned by test_user)
        update_data = {"name": "Hacked Project Name"}
        response = await client.put(
            f"/api/v1/projects/{test_project.id}",
            json=update_data,
            headers=other_auth_headers
        )
        
        assert response.status_code == 403

    @pytest.mark.asyncio
    @pytest.mark.api
    async def test_user_cannot_delete_other_user_project(
        self, 
        client: AsyncClient, 
        db_session: AsyncSession,
        test_project: Project
    ):
        """Test that users cannot delete projects owned by others"""
        # Create another user
        from app.services.user_service import UserService
        from app.core.security import create_access_token
        
        user_service = UserService(db_session)
        other_user = await user_service.create(
            email="delete_test@example.com",
            full_name="Delete Test User",
            password="deletetestpassword123"
        )
        
        # Create auth headers for the other user
        access_token = create_access_token(subject=other_user.id)
        other_auth_headers = {"Authorization": f"Bearer {access_token}"}
        
        # Try to delete test_project (owned by test_user)
        response = await client.delete(
            f"/api/v1/projects/{test_project.id}",
            headers=other_auth_headers
        )
        
        assert response.status_code == 403


class TestProjectStats:
    """Test project statistics"""

    @pytest.mark.asyncio
    @pytest.mark.api
    async def test_project_stats_structure(
        self, 
        client: AsyncClient, 
        auth_headers: dict, 
        test_project: Project
    ):
        """Test that project stats have correct structure"""
        response = await client.get(
            f"/api/v1/projects/{test_project.id}",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "stats" in data
        stats = data["stats"]
        assert "total_tasks" in stats
        assert "completed_tasks" in stats
        assert "total_data_collected" in stats
        assert "total_reports" in stats
        
        # All stats should be integers
        assert isinstance(stats["total_tasks"], int)
        assert isinstance(stats["completed_tasks"], int)
        assert isinstance(stats["total_data_collected"], int)
        assert isinstance(stats["total_reports"], int)
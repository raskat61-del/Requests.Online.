import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.models.project import Project


class TestAPIIntegration:
    """Integration tests for the full API workflow"""

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_full_user_project_workflow(self, client: AsyncClient):
        """Test complete workflow: register -> login -> create project -> manage project"""
        
        # 1. Register a new user
        register_data = {
            "email": "integration@example.com",
            "password": "integration123",
            "full_name": "Integration Test User"
        }
        
        register_response = await client.post("/api/v1/auth/register", json=register_data)
        assert register_response.status_code == 201
        
        register_result = register_response.json()
        access_token = register_result["access_token"]
        user_id = register_result["user"]["id"]
        
        auth_headers = {"Authorization": f"Bearer {access_token}"}
        
        # 2. Verify user can access protected endpoints
        me_response = await client.get("/api/v1/auth/me", headers=auth_headers)
        assert me_response.status_code == 200
        assert me_response.json()["email"] == register_data["email"]
        
        # 3. Create a project
        project_data = {
            "name": "Integration Test Project",
            "description": "A project for integration testing",
            "status": "active"
        }
        
        create_project_response = await client.post(
            "/api/v1/projects/", 
            json=project_data, 
            headers=auth_headers
        )
        assert create_project_response.status_code == 201
        
        project = create_project_response.json()
        project_id = project["id"]
        
        # 4. Get project list
        projects_response = await client.get("/api/v1/projects/", headers=auth_headers)
        assert projects_response.status_code == 200
        
        projects = projects_response.json()
        assert len(projects) == 1
        assert projects[0]["id"] == project_id
        
        # 5. Get specific project
        project_detail_response = await client.get(
            f"/api/v1/projects/{project_id}", 
            headers=auth_headers
        )
        assert project_detail_response.status_code == 200
        
        project_detail = project_detail_response.json()
        assert project_detail["name"] == project_data["name"]
        assert "stats" in project_detail
        
        # 6. Update project
        update_data = {
            "name": "Updated Integration Project",
            "status": "completed"
        }
        
        update_response = await client.put(
            f"/api/v1/projects/{project_id}",
            json=update_data,
            headers=auth_headers
        )
        assert update_response.status_code == 200
        
        updated_project = update_response.json()
        assert updated_project["name"] == update_data["name"]
        assert updated_project["status"] == update_data["status"]
        
        # 7. Create a search task
        search_data = {
            "project_id": project_id,
            "query": "test search query",
            "sources": ["google", "yandex"]
        }
        
        search_response = await client.post(
            "/api/v1/search/",
            json=search_data,
            headers=auth_headers
        )
        assert search_response.status_code == 201
        
        search_task = search_response.json()
        search_task_id = search_task["id"]
        
        # 8. Get search task
        get_search_response = await client.get(
            f"/api/v1/search/{search_task_id}",
            headers=auth_headers
        )
        assert get_search_response.status_code == 200
        
        # 9. Get project search tasks
        project_searches_response = await client.get(
            f"/api/v1/search/project/{project_id}",
            headers=auth_headers
        )
        assert project_searches_response.status_code == 200
        
        project_searches = project_searches_response.json()
        assert len(project_searches) == 1
        assert project_searches[0]["id"] == search_task_id
        
        # 10. Delete project
        delete_response = await client.delete(
            f"/api/v1/projects/{project_id}",
            headers=auth_headers
        )
        assert delete_response.status_code == 200
        
        # 11. Verify project is deleted
        deleted_project_response = await client.get(
            f"/api/v1/projects/{project_id}",
            headers=auth_headers
        )
        assert deleted_project_response.status_code == 404

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_authentication_flow_with_token_refresh(self, client: AsyncClient):
        """Test authentication with token refresh"""
        
        # 1. Register user
        register_data = {
            "email": "refresh@example.com",
            "password": "refresh123",
            "full_name": "Refresh Test User"
        }
        
        register_response = await client.post("/api/v1/auth/register", json=register_data)
        assert register_response.status_code == 201
        
        register_result = register_response.json()
        refresh_token = register_result["refresh_token"]
        
        # 2. Use refresh token to get new access token
        refresh_data = {"refresh_token": refresh_token}
        refresh_response = await client.post("/api/v1/auth/refresh", json=refresh_data)
        assert refresh_response.status_code == 200
        
        refresh_result = refresh_response.json()
        new_access_token = refresh_result["access_token"]
        new_refresh_token = refresh_result["refresh_token"]
        
        # 3. Use new access token
        new_auth_headers = {"Authorization": f"Bearer {new_access_token}"}
        me_response = await client.get("/api/v1/auth/me", headers=new_auth_headers)
        assert me_response.status_code == 200
        
        # 4. Logout
        logout_response = await client.post("/api/v1/auth/logout", headers=new_auth_headers)
        assert logout_response.status_code == 200

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_analysis_workflow(self, client: AsyncClient, auth_headers: dict, test_project: Project):
        """Test analysis workflow"""
        
        # 1. Create analysis
        analysis_data = {
            "project_id": test_project.id,
            "analysis_type": "sentiment"
        }
        
        analysis_response = await client.post(
            "/api/v1/analysis/",
            json=analysis_data,
            headers=auth_headers
        )
        assert analysis_response.status_code == 201
        
        analysis = analysis_response.json()
        analysis_id = analysis["id"]
        
        # 2. Get analysis by ID
        get_analysis_response = await client.get(
            f"/api/v1/analysis/{analysis_id}",
            headers=auth_headers
        )
        assert get_analysis_response.status_code == 200
        
        # 3. Get project analyses
        project_analyses_response = await client.get(
            f"/api/v1/analysis/project/{test_project.id}",
            headers=auth_headers
        )
        assert project_analyses_response.status_code == 200
        
        project_analyses = project_analyses_response.json()
        assert len(project_analyses) >= 1

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_report_generation_workflow(self, client: AsyncClient, auth_headers: dict, test_project: Project):
        """Test report generation workflow"""
        
        # 1. Generate report
        report_data = {
            "project_id": test_project.id,
            "report_type": "comprehensive",
            "format": "pdf"
        }
        
        generate_response = await client.post(
            "/api/v1/reports/generate",
            json=report_data,
            headers=auth_headers
        )
        assert generate_response.status_code == 202  # Accepted for async processing
        
        generate_result = generate_response.json()
        task_id = generate_result["task_id"]
        
        # 2. Check report status
        status_response = await client.get(
            f"/api/v1/reports/status/{task_id}",
            headers=auth_headers
        )
        assert status_response.status_code == 200
        
        status_result = status_response.json()
        assert "status" in status_result

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_permission_boundaries(self, client: AsyncClient, db_session: AsyncSession):
        """Test that users cannot access each other's resources"""
        
        # Create two users
        user1_data = {
            "email": "user1@example.com",
            "password": "password123",
            "full_name": "User One"
        }
        
        user2_data = {
            "email": "user2@example.com", 
            "password": "password123",
            "full_name": "User Two"
        }
        
        # Register both users
        user1_response = await client.post("/api/v1/auth/register", json=user1_data)
        user2_response = await client.post("/api/v1/auth/register", json=user2_data)
        
        assert user1_response.status_code == 201
        assert user2_response.status_code == 201
        
        user1_token = user1_response.json()["access_token"]
        user2_token = user2_response.json()["access_token"]
        
        user1_headers = {"Authorization": f"Bearer {user1_token}"}
        user2_headers = {"Authorization": f"Bearer {user2_token}"}
        
        # User1 creates a project
        project_data = {
            "name": "User1 Project",
            "description": "Private project"
        }
        
        project_response = await client.post(
            "/api/v1/projects/",
            json=project_data,
            headers=user1_headers
        )
        assert project_response.status_code == 201
        
        project_id = project_response.json()["id"]
        
        # User2 tries to access User1's project - should fail
        forbidden_response = await client.get(
            f"/api/v1/projects/{project_id}",
            headers=user2_headers
        )
        assert forbidden_response.status_code == 403
        
        # User2 tries to update User1's project - should fail
        update_response = await client.put(
            f"/api/v1/projects/{project_id}",
            json={"name": "Hacked Project"},
            headers=user2_headers
        )
        assert update_response.status_code == 403
        
        # User2 tries to delete User1's project - should fail
        delete_response = await client.delete(
            f"/api/v1/projects/{project_id}",
            headers=user2_headers
        )
        assert delete_response.status_code == 403

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_api_error_handling(self, client: AsyncClient):
        """Test API error handling"""
        
        # Test 404 for non-existent resources
        response = await client.get("/api/v1/projects/99999")
        assert response.status_code == 401  # Unauthorized, not 404
        
        # Test 422 for validation errors
        invalid_project_data = {
            "name": "",  # Empty name
            "description": "Valid description"
        }
        
        # First need to authenticate
        user_data = {
            "email": "error@example.com",
            "password": "password123",
            "full_name": "Error Test User"
        }
        
        register_response = await client.post("/api/v1/auth/register", json=user_data)
        access_token = register_response.json()["access_token"]
        auth_headers = {"Authorization": f"Bearer {access_token}"}
        
        validation_response = await client.post(
            "/api/v1/projects/",
            json=invalid_project_data,
            headers=auth_headers
        )
        assert validation_response.status_code == 422
        
        # Test rate limiting (if implemented)
        # This would depend on your rate limiting configuration

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_cors_headers(self, client: AsyncClient):
        """Test CORS headers are properly set"""
        
        # Test preflight request
        preflight_response = await client.options(
            "/api/v1/projects/",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "Content-Type,Authorization"
            }
        )
        
        # Should allow the request
        assert preflight_response.status_code in [200, 204]
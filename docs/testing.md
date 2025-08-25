# Testing Guide for Analytics Bot

This document provides comprehensive information about testing the Analytics Bot application, including both backend and frontend testing strategies, setup instructions, and best practices.

## Overview

The Analytics Bot uses a comprehensive testing strategy covering:

- **Unit Tests**: Testing individual components in isolation
- **Integration Tests**: Testing component interactions and API workflows
- **Frontend Tests**: Testing React components and user interactions
- **API Tests**: Testing REST API endpoints and authentication
- **Mock Tests**: Testing with external service mocks

## Backend Testing

### Setup

Install testing dependencies:

```bash
cd backend
pip install -r requirements-test.txt
```

### Running Tests

#### Quick Start

```bash
# Run all tests
python -m pytest

# Run with coverage
python -m pytest --cov=app --cov-report=html

# Run specific test categories
python -m pytest -m unit
python -m pytest -m integration
python -m pytest -m auth
```

#### Using Test Scripts

**Linux/Mac:**
```bash
# Make executable and run
chmod +x run_tests.sh
./run_tests.sh --coverage --verbose
```

**Windows:**
```cmd
run_tests.bat --coverage --verbose
```

#### Test Script Options

- `--coverage`: Generate coverage report
- `--unit`: Run only unit tests
- `--integration`: Run only integration tests
- `--auth`: Run only authentication tests
- `--api`: Run only API endpoint tests
- `--collectors`: Run only data collector tests
- `--analyzers`: Run only text analyzer tests
- `--verbose`: Verbose output
- `--install`: Install test dependencies
- `--test=PATH`: Run specific test file or function

### Test Structure

```
backend/
├── tests/
│   ├── test_auth.py           # Authentication tests
│   ├── test_projects.py       # Project management tests
│   ├── test_collectors.py     # Data collector tests
│   ├── test_analyzers.py      # Text analyzer tests
│   ├── test_integration.py    # Integration tests
│   └── __init__.py
├── conftest.py                # Test configuration and fixtures
├── pytest.ini                # Pytest configuration
├── run_tests.sh              # Test runner (Linux/Mac)
├── run_tests.bat             # Test runner (Windows)
└── requirements-test.txt     # Testing dependencies
```

### Test Categories

#### Unit Tests (`-m unit`)
Test individual functions and classes in isolation:

```python
@pytest.mark.unit
async def test_password_hashing():
    \"\"\"Test password hashing functionality\"\"\"
    password = \"testpassword123\"
    hashed = get_password_hash(password)
    assert verify_password(password, hashed) is True
```

#### Integration Tests (`-m integration`)
Test complete workflows and component interactions:

```python
@pytest.mark.integration
async def test_full_user_project_workflow(client: AsyncClient):
    \"\"\"Test complete user registration -> project creation workflow\"\"\"
    # Register user -> Login -> Create project -> Manage project
```

#### Authentication Tests (`-m auth`)
Test authentication and authorization:

```python
@pytest.mark.auth
async def test_login_valid_credentials(client: AsyncClient, test_user: User):
    \"\"\"Test login with valid credentials\"\"\"
```

#### API Tests (`-m api`)
Test REST API endpoints:

```python
@pytest.mark.api
async def test_create_project(client: AsyncClient, auth_headers: dict):
    \"\"\"Test project creation API endpoint\"\"\"
```

### Test Fixtures

Common fixtures available in all tests:

- `client`: HTTP test client
- `db_session`: Database session for testing
- `test_user`: Pre-created test user
- `test_superuser`: Pre-created superuser
- `test_project`: Pre-created test project
- `auth_headers`: Authorization headers for test user
- `sample_text_data`: Sample text data for analysis
- `mock_api_responses`: Mock external API responses

### Mocking External Services

External services are mocked in tests:

```python
@patch('aiohttp.ClientSession.get')
async def test_google_search_success(mock_get):
    mock_response_data = {\"items\": [{\"title\": \"Test\", \"snippet\": \"Test\"}]}
    mock_response = AsyncMock()
    mock_response.status = 200
    mock_response.json = AsyncMock(return_value=mock_response_data)
    mock_get.return_value.__aenter__.return_value = mock_response
```

### Coverage Requirements

Minimum coverage thresholds:
- Overall: 80%
- Functions: 70%
- Lines: 70%
- Branches: 70%

Generate coverage report:
```bash
pytest --cov=app --cov-report=html --cov-report=term-missing
# View report: open htmlcov/index.html
```

## Frontend Testing

### Setup

Install testing dependencies:

```bash
cd frontend
npm install
```

### Running Tests

```bash
# Run all tests
npm run test

# Run tests with UI
npm run test:ui

# Run tests with coverage
npm run test:coverage

# Run tests once (CI mode)
npm run test:run
```

### Test Structure

```
frontend/
├── src/
│   ├── test/
│   │   ├── setup.ts              # Test setup and configuration
│   │   ├── utils.tsx             # Test utilities and helpers
│   │   ├── AuthContext.test.tsx  # Auth context tests
│   │   └── LoginPage.test.tsx    # Login page tests
│   └── ...
├── vitest.config.ts              # Vitest configuration
└── package.json                  # Test scripts
```

### Test Utilities

Custom render functions for testing React components:

```typescript
// Render with all providers
renderWithProviders(<LoginPage />)

// Render without authentication
renderWithoutAuth(<LoginPage />)

// Render with specific route
renderWithRoute(<App />, '/projects')
```

### Mock Data

Test utilities provide mock data:

```typescript
// Mock user data
const mockUser = {
  id: 1,
  email: 'test@example.com',
  full_name: 'Test User',
  is_active: true
}

// Mock API responses
const mockApiResponses = {
  auth: { login: { access_token: 'token', user: mockUser } },
  projects: { list: [mockProject] }
}
```

### Component Testing

Test React components with user interactions:

```typescript
it('should handle login form submission', async () => {
  const mockLogin = vi.fn()
  renderWithoutAuth(<LoginPage />, { authContextValue: { login: mockLogin } })
  
  await user.type(screen.getByLabelText(/email/i), 'test@example.com')
  await user.type(screen.getByLabelText(/password/i), 'password123')
  await user.click(screen.getByRole('button', { name: /sign in/i }))
  
  expect(mockLogin).toHaveBeenCalledWith({
    email: 'test@example.com',
    password: 'password123'
  })
})
```

## API Testing with Examples

### Authentication Flow

```python
# Test user registration
register_data = {
    \"email\": \"test@example.com\",
    \"password\": \"password123\",
    \"full_name\": \"Test User\"
}
response = await client.post(\"/api/v1/auth/register\", json=register_data)
assert response.status_code == 201

# Test login
login_data = {
    \"username\": \"test@example.com\",
    \"password\": \"password123\"
}
response = await client.post(\"/api/v1/auth/login\", data=login_data)
assert response.status_code == 200
token = response.json()[\"access_token\"]
```

### Project Management

```python
# Create project
project_data = {
    \"name\": \"Test Project\",
    \"description\": \"A test project\"
}
headers = {\"Authorization\": f\"Bearer {token}\"}
response = await client.post(\"/api/v1/projects/\", json=project_data, headers=headers)
assert response.status_code == 201
```

### Data Collection

```python
# Create search task
search_data = {
    \"project_id\": project_id,
    \"query\": \"test search\",
    \"sources\": [\"google\", \"yandex\"]
}
response = await client.post(\"/api/v1/search/\", json=search_data, headers=headers)
assert response.status_code == 201
```

## Best Practices

### Backend Testing

1. **Use proper test isolation**: Each test should be independent
2. **Mock external services**: Don't make real API calls in tests
3. **Test error conditions**: Test both success and failure scenarios
4. **Use descriptive test names**: Test names should describe what is being tested
5. **Follow AAA pattern**: Arrange, Act, Assert

```python
async def test_create_project_with_invalid_data():
    # Arrange
    invalid_data = {\"name\": \"\"}  # Empty name
    
    # Act
    response = await client.post(\"/api/v1/projects/\", json=invalid_data)
    
    # Assert
    assert response.status_code == 422
```

### Frontend Testing

1. **Test user behavior**: Focus on what users actually do
2. **Use semantic queries**: Query by role, label text, etc.
3. **Avoid implementation details**: Don't test internal state
4. **Test accessibility**: Ensure components are accessible
5. **Mock API calls**: Don't make real network requests

```typescript
// Good: Test user behavior
it('should show error message for invalid login', async () => {
  renderWithoutAuth(<LoginPage />)
  
  await user.click(screen.getByRole('button', { name: /sign in/i }))
  
  expect(screen.getByText(/email is required/i)).toBeInTheDocument()
})

// Avoid: Testing implementation details
// Don't test component state directly
```

### Test Data Management

1. **Use factories for test data**: Create reusable data generators
2. **Keep tests independent**: Don't rely on test execution order
3. **Clean up after tests**: Reset database state between tests
4. **Use meaningful test data**: Data should reflect real-world scenarios

## Continuous Integration

### GitHub Actions Example

```yaml
name: Tests

on: [push, pull_request]

jobs:
  backend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.9'
      - name: Install dependencies
        run: |
          cd backend
          pip install -r requirements.txt
          pip install -r requirements-test.txt
      - name: Run tests
        run: |
          cd backend
          pytest --cov=app --cov-report=xml
      - name: Upload coverage
        uses: codecov/codecov-action@v3

  frontend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '18'
      - name: Install dependencies
        run: |
          cd frontend
          npm ci
      - name: Run tests
        run: |
          cd frontend
          npm run test:coverage
```

## Debugging Tests

### Backend Debugging

1. **Use verbose output**: `pytest -v`
2. **Run specific tests**: `pytest tests/test_auth.py::test_login`
3. **Use pdb for debugging**: Add `import pdb; pdb.set_trace()` in tests
4. **Check test database**: Test database is preserved on failure

### Frontend Debugging

1. **Use test UI**: `npm run test:ui`
2. **Debug with browser**: Tests run in jsdom, use console.log
3. **Check component output**: Use `screen.debug()` to see rendered HTML

## Performance Testing

For performance testing:

1. **Load testing**: Use tools like `locust` for API load testing
2. **Database performance**: Test with larger datasets
3. **Memory usage**: Monitor memory usage during tests
4. **Response times**: Assert on API response times

```python
@pytest.mark.slow
async def test_large_dataset_analysis():
    \"\"\"Test analysis with large dataset\"\"\"
    large_dataset = generate_large_text_dataset(10000)
    
    start_time = time.time()
    results = await analyzer.analyze(large_dataset)
    elapsed = time.time() - start_time
    
    assert elapsed < 30  # Should complete within 30 seconds
    assert len(results) > 0
```

## Troubleshooting

### Common Issues

1. **Test database issues**: Ensure proper cleanup between tests
2. **Mock configuration**: Verify mocks are properly configured
3. **Async test issues**: Use `pytest-asyncio` for async tests
4. **Import errors**: Check Python path and module imports
5. **Environment variables**: Ensure test environment is properly set

### Getting Help

1. Check test output for specific error messages
2. Review test configuration in `pytest.ini` and `vitest.config.ts`
3. Verify all dependencies are installed
4. Check that database permissions are correct
5. Ensure external services are properly mocked

For additional help, refer to:
- [pytest documentation](https://docs.pytest.org/)
- [Vitest documentation](https://vitest.dev/)
- [Testing Library documentation](https://testing-library.com/)
- [FastAPI testing guide](https://fastapi.tiangolo.com/tutorial/testing/)
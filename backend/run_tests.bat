@echo off
echo Running Analytics Bot Tests...

REM Navigate to backend
cd backend

REM Install test dependencies
echo Installing test dependencies...
pip install -r requirements-test.txt

REM Run tests
echo Running backend tests...
pytest tests/ -v --cov=app --cov-report=html

REM Navigate to frontend
cd ..
cd frontend

REM Install dependencies if needed
if not exist "node_modules" (
    echo Installing frontend dependencies...
    npm install
)

REM Run frontend tests
echo Running frontend tests...
npm run test:run

echo.
echo All tests completed!
echo Backend coverage report: backend/htmlcov/index.html
echo.
pause
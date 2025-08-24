@echo off
echo 🚀 Starting Analytics Bot...

REM Check if we're in the correct directory
if not exist "backend" (
    echo ❌ Backend directory not found. Please run this script from the AnalyticsBot root directory
    pause
    exit /b 1
)

if not exist "frontend" (
    echo ❌ Frontend directory not found. Please run this script from the AnalyticsBot root directory
    pause
    exit /b 1
)

echo.
echo 🔧 Starting backend server...
start "Backend Server" cmd /k "cd backend && python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload"

REM Wait for backend to start
timeout /t 5 /nobreak > nul

echo 🎨 Starting frontend server...
cd frontend

REM Install dependencies if node_modules doesn't exist
if not exist "node_modules" (
    echo 📦 Installing frontend dependencies...
    npm install
)

start "Frontend Server" cmd /k "npm run dev"
cd ..

echo.
echo 🎉 Analytics Bot is starting!
echo.
echo Frontend: http://localhost:3000
echo Backend:  http://localhost:8000
echo API Docs: http://localhost:8000/docs
echo.
echo Close the terminal windows to stop the servers
pause
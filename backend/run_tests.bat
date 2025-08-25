@echo off
REM Test runner script for Analytics Bot backend (Windows)

echo 🧪 Analytics Bot Test Runner
echo ==============================

REM Check if we're in the backend directory
if not exist "requirements.txt" (
    echo ❌ Please run this script from the backend directory
    pause
    exit /b 1
)

REM Parse command line arguments
set COVERAGE=
set MARKERS=
set VERBOSE=
set SPECIFIC_TEST=
set INSTALL_DEPS=

:parse_args
if "%1"=="" goto end_parse
if "%1"=="--coverage" (
    set COVERAGE=--cov=app --cov-report=html --cov-report=term-missing
    shift
    goto parse_args
)
if "%1"=="--unit" (
    set MARKERS=-m unit
    shift
    goto parse_args
)
if "%1"=="--integration" (
    set MARKERS=-m integration
    shift
    goto parse_args
)
if "%1"=="--auth" (
    set MARKERS=-m auth
    shift
    goto parse_args
)
if "%1"=="--api" (
    set MARKERS=-m api
    shift
    goto parse_args
)
if "%1"=="--collectors" (
    set MARKERS=-m collectors
    shift
    goto parse_args
)
if "%1"=="--analyzers" (
    set MARKERS=-m analyzers
    shift
    goto parse_args
)
if "%1"=="--verbose" (
    set VERBOSE=-v
    shift
    goto parse_args
)
if "%1"=="-v" (
    set VERBOSE=-v
    shift
    goto parse_args
)
if "%1"=="--install" (
    set INSTALL_DEPS=true
    shift
    goto parse_args
)
if "%1"=="--help" goto show_help
if "%1"=="-h" goto show_help

REM Handle --test= argument
echo %1 | findstr /c:"--test=" >nul
if not errorlevel 1 (
    set SPECIFIC_TEST=%1
    set SPECIFIC_TEST=%SPECIFIC_TEST:--test=%
    shift
    goto parse_args
)

echo Unknown option: %1
echo Use --help for usage information
exit /b 1

:show_help
echo Usage: %0 [OPTIONS]
echo.
echo Options:
echo   --coverage     Run tests with coverage report
echo   --unit         Run only unit tests
echo   --integration  Run only integration tests
echo   --auth         Run only authentication tests
echo   --api          Run only API tests
echo   --collectors   Run only collector tests
echo   --analyzers    Run only analyzer tests
echo   --verbose, -v  Verbose output
echo   --install      Install test dependencies
echo   --test=PATH    Run specific test file or function
echo   --help, -h     Show this help message
echo.
echo Examples:
echo   %0 --coverage --unit
echo   %0 --integration --verbose
echo   %0 --test=tests/test_auth.py
exit /b 0

:end_parse

REM Install dependencies if requested
if "%INSTALL_DEPS%"=="true" (
    echo.
    echo Installing Test Dependencies
    echo ----------------------------------------
    pip install -r requirements-test.txt
    if errorlevel 1 (
        echo ❌ Failed to install test dependencies
        pause
        exit /b 1
    )
)

REM Check if pytest is available
python -m pytest --version >nul 2>&1
if errorlevel 1 (
    echo ❌ pytest not found. Install test dependencies with:
    echo pip install -r requirements-test.txt
    pause
    exit /b 1
)

REM Environment setup
echo.
echo Setting Up Test Environment
echo ----------------------------------------
set TESTING=true
set DATABASE_URL=sqlite:///./test.db
set ASYNC_DATABASE_URL=sqlite+aiosqlite:///./test.db
set SECRET_KEY=test-secret-key

REM Clean up any existing test database
if exist "test.db" (
    del test.db
    echo 🗑️  Cleaned up previous test database
)

REM Run pre-test checks
echo.
echo Pre-test Checks
echo ----------------------------------------

REM Check code formatting (if black is available)
python -m black --version >nul 2>&1
if not errorlevel 1 (
    python -m black --check app tests
    if errorlevel 1 (
        echo ⚠️  Code formatting issues found. Run 'black app tests' to fix.
    )
)

REM Check linting (if flake8 is available)
python -m flake8 --version >nul 2>&1
if not errorlevel 1 (
    python -m flake8 app tests
    if errorlevel 1 (
        echo ⚠️  Linting issues found
    )
)

REM Build pytest command
set PYTEST_CMD=python -m pytest

if not "%SPECIFIC_TEST%"=="" (
    set PYTEST_CMD=%PYTEST_CMD% %SPECIFIC_TEST%
) else (
    set PYTEST_CMD=%PYTEST_CMD% tests/
)

if not "%MARKERS%"=="" (
    set PYTEST_CMD=%PYTEST_CMD% %MARKERS%
)

if not "%VERBOSE%"=="" (
    set PYTEST_CMD=%PYTEST_CMD% %VERBOSE%
)

if not "%COVERAGE%"=="" (
    set PYTEST_CMD=%PYTEST_CMD% %COVERAGE%
)

REM Add standard options
set PYTEST_CMD=%PYTEST_CMD% --tb=short --disable-warnings

REM Run tests
echo.
echo Running Tests
echo ----------------------------------------
echo Command: %PYTEST_CMD%

%PYTEST_CMD%

if errorlevel 1 (
    echo.
    echo ❌ Some tests failed
    if exist "test.db" (
        echo ⚠️  Test database preserved for debugging: test.db
    )
    pause
    exit /b 1
) else (
    echo.
    echo 🎉 All tests passed!
    
    if not "%COVERAGE%"=="" (
        echo 📊 Coverage report available at: htmlcov/index.html
    )
    
    if exist "test.db" (
        del test.db
        echo 🗑️  Cleaned up test database
    )
    
    echo.
    echo Press any key to continue...
    pause >nul
    exit /b 0
)
#!/bin/bash

# Test runner script for Analytics Bot backend

set -e

echo "🧪 Analytics Bot Test Runner"
echo "=============================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if we're in the backend directory
if [ ! -f "requirements.txt" ]; then
    echo -e "${RED}❌ Please run this script from the backend directory${NC}"
    exit 1
fi

# Function to print section headers
print_section() {
    echo -e "\n${BLUE}$1${NC}"
    echo "----------------------------------------"
}

# Function to run command and check result
run_command() {
    local cmd="$1"
    local description="$2"
    
    echo -e "${YELLOW}Running: $description${NC}"
    if eval $cmd; then
        echo -e "${GREEN}✅ $description passed${NC}"
        return 0
    else
        echo -e "${RED}❌ $description failed${NC}"
        return 1
    fi
}

# Parse command line arguments
COVERAGE=""
MARKERS=""
VERBOSE=""
SPECIFIC_TEST=""
INSTALL_DEPS=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --coverage)
            COVERAGE="--cov=app --cov-report=html --cov-report=term-missing"
            shift
            ;;
        --unit)
            MARKERS="-m unit"
            shift
            ;;
        --integration)
            MARKERS="-m integration"
            shift
            ;;
        --auth)
            MARKERS="-m auth"
            shift
            ;;
        --api)
            MARKERS="-m api"
            shift
            ;;
        --collectors)
            MARKERS="-m collectors"
            shift
            ;;
        --analyzers)
            MARKERS="-m analyzers"
            shift
            ;;
        --verbose|-v)
            VERBOSE="-v"
            shift
            ;;
        --install)
            INSTALL_DEPS="true"
            shift
            ;;
        --test=*)
            SPECIFIC_TEST="${1#*=}"
            shift
            ;;
        --help|-h)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --coverage     Run tests with coverage report"
            echo "  --unit         Run only unit tests"
            echo "  --integration  Run only integration tests"
            echo "  --auth         Run only authentication tests"
            echo "  --api          Run only API tests"
            echo "  --collectors   Run only collector tests"
            echo "  --analyzers    Run only analyzer tests"
            echo "  --verbose, -v  Verbose output"
            echo "  --install      Install test dependencies"
            echo "  --test=PATH    Run specific test file or function"
            echo "  --help, -h     Show this help message"
            echo ""
            echo "Examples:"
            echo "  $0 --coverage --unit"
            echo "  $0 --integration --verbose"
            echo "  $0 --test=tests/test_auth.py"
            echo "  $0 --test=tests/test_auth.py::TestAuthEndpoints::test_login_valid_credentials"
            exit 0
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Install dependencies if requested
if [ "$INSTALL_DEPS" == "true" ]; then
    print_section "Installing Test Dependencies"
    run_command "pip install -r requirements-test.txt" "Installing test dependencies"
fi

# Check if pytest is available
if ! command -v pytest &> /dev/null; then
    echo -e "${RED}❌ pytest not found. Install test dependencies with:${NC}"
    echo "pip install -r requirements-test.txt"
    exit 1
fi

# Environment setup
print_section "Setting Up Test Environment"
export TESTING=true
export DATABASE_URL="sqlite:///./test.db"
export ASYNC_DATABASE_URL="sqlite+aiosqlite:///./test.db"
export SECRET_KEY="test-secret-key"

# Clean up any existing test database
if [ -f "test.db" ]; then
    rm test.db
    echo "🗑️  Cleaned up previous test database"
fi

# Run pre-test checks
print_section "Pre-test Checks"

# Check code formatting (if black is available)
if command -v black &> /dev/null; then
    run_command "black --check app tests" "Code formatting check" || echo -e "${YELLOW}⚠️  Code formatting issues found. Run 'black app tests' to fix.${NC}"
fi

# Check imports (if isort is available)
if command -v isort &> /dev/null; then
    run_command "isort --check-only app tests" "Import sorting check" || echo -e "${YELLOW}⚠️  Import sorting issues found. Run 'isort app tests' to fix.${NC}"
fi

# Check linting (if flake8 is available)
if command -v flake8 &> /dev/null; then
    run_command "flake8 app tests" "Linting check" || echo -e "${YELLOW}⚠️  Linting issues found${NC}"
fi

# Build pytest command
PYTEST_CMD="pytest"

if [ -n "$SPECIFIC_TEST" ]; then
    PYTEST_CMD="$PYTEST_CMD $SPECIFIC_TEST"
else
    PYTEST_CMD="$PYTEST_CMD tests/"
fi

if [ -n "$MARKERS" ]; then
    PYTEST_CMD="$PYTEST_CMD $MARKERS"
fi

if [ -n "$VERBOSE" ]; then
    PYTEST_CMD="$PYTEST_CMD $VERBOSE"
fi

if [ -n "$COVERAGE" ]; then
    PYTEST_CMD="$PYTEST_CMD $COVERAGE"
fi

# Add standard options
PYTEST_CMD="$PYTEST_CMD --tb=short --disable-warnings"

# Run tests
print_section "Running Tests"
echo -e "${YELLOW}Command: $PYTEST_CMD${NC}"

if eval $PYTEST_CMD; then
    echo -e "\n${GREEN}🎉 All tests passed!${NC}"
    
    # Show coverage report location if coverage was run
    if [ -n "$COVERAGE" ]; then
        echo -e "${BLUE}📊 Coverage report available at: htmlcov/index.html${NC}"
    fi
    
    # Clean up test database
    if [ -f "test.db" ]; then
        rm test.db
        echo "🗑️  Cleaned up test database"
    fi
    
    exit 0
else
    echo -e "\n${RED}❌ Some tests failed${NC}"
    
    # Don't clean up on failure for debugging
    if [ -f "test.db" ]; then
        echo -e "${YELLOW}⚠️  Test database preserved for debugging: test.db${NC}"
    fi
    
    exit 1
fi
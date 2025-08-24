#!/bin/bash

echo "Running Analytics Bot Tests..."

# Navigate to backend
cd backend

# Install test dependencies
echo "Installing test dependencies..."
pip install -r requirements-test.txt

# Run tests with coverage
echo "Running backend tests..."
pytest tests/ -v --cov=app --cov-report=html --cov-report=term

# Check test results
if [ $? -ne 0 ]; then
    echo "Backend tests failed!"
    exit 1
fi

# Navigate to frontend
cd ../frontend

# Install dependencies if needed
if [ ! -d "node_modules" ]; then
    echo "Installing frontend dependencies..."
    npm install
fi

# Run frontend tests
echo "Running frontend tests..."
npm run test:run

if [ $? -ne 0 ]; then
    echo "Frontend tests failed!"
    exit 1
fi

echo ""
echo "All tests completed successfully!"
echo "Backend coverage report: backend/htmlcov/index.html"
echo ""
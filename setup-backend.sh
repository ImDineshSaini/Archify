#!/bin/bash

echo "Setting up Archify backend locally..."

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "Python version: $python_version"

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r backend/requirements.txt

# Create .env file if it doesn't exist
if [ ! -f backend/.env ]; then
    echo "Creating .env file..."
    cp backend/.env.example backend/.env
    echo "⚠️  Please update backend/.env with your database URL and API keys"
fi

echo ""
echo "✅ Backend setup complete!"
echo ""
echo "To run the backend:"
echo "1. Make sure PostgreSQL is running locally"
echo "2. Update backend/.env with your database URL"
echo "3. Run migrations: cd backend && alembic upgrade head"
echo "4. Start server: cd backend && uvicorn app.main:app --reload"

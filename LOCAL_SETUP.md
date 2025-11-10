# Archify - Local Development Setup (Without Docker)

## Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL 15+
- Redis (optional, for caching)

## Setup Instructions

### 1. Database Setup

**Install PostgreSQL:**
```bash
# Ubuntu/Debian
sudo apt install postgresql postgresql-contrib

# macOS
brew install postgresql
brew services start postgresql

# Create database
sudo -u postgres psql
CREATE DATABASE archify;
CREATE USER archify WITH PASSWORD 'archify123';
GRANT ALL PRIVILEGES ON DATABASE archify TO archify;
\q
```

### 2. Redis Setup (Optional)

```bash
# Ubuntu/Debian
sudo apt install redis-server
sudo systemctl start redis

# macOS
brew install redis
brew services start redis
```

### 3. Backend Setup

```bash
# Run setup script
chmod +x setup-backend.sh
./setup-backend.sh

# OR manual setup:
cd backend
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your database URL and settings

# Run migrations
alembic upgrade head

# Start backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Backend will be available at: http://localhost:8000

### 4. Frontend Setup

```bash
# Run setup script
chmod +x setup-frontend.sh
./setup-frontend.sh

# OR manual setup:
cd frontend
npm install

# Start frontend
npm run dev
```

Frontend will be available at: http://localhost:3000

## Environment Configuration

### Backend (.env)

```bash
# Database
DATABASE_URL=postgresql://archify:archify123@localhost:5432/archify

# Redis (optional)
REDIS_URL=redis://localhost:6379/0

# Security
SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-here

# LLM Provider (configure via UI or set here)
ANTHROPIC_API_KEY=your-claude-api-key
# OR
OPENAI_API_KEY=your-openai-api-key
```

## Running the Application

### Terminal 1 - Backend
```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload
```

### Terminal 2 - Frontend
```bash
cd frontend
npm run dev
```

### Terminal 3 - Database Migrations (when needed)
```bash
cd backend
source venv/bin/activate
alembic upgrade head
```

## Development Workflow

### Create Database Migration
```bash
cd backend
source venv/bin/activate
alembic revision --autogenerate -m "description"
alembic upgrade head
```

### Run Tests
```bash
# Backend
cd backend
pytest

# Frontend
cd frontend
npm test
```

## Troubleshooting

### Database Connection Issues
```bash
# Check PostgreSQL is running
sudo systemctl status postgresql  # Linux
brew services list  # macOS

# Check connection
psql -U archify -d archify -h localhost
```

### Port Already in Use
```bash
# Find and kill process on port 8000
lsof -ti:8000 | xargs kill -9

# Find and kill process on port 3000
lsof -ti:3000 | xargs kill -9
```

### Module Not Found Errors
```bash
# Backend
cd backend
source venv/bin/activate
pip install -r requirements.txt

# Frontend
cd frontend
rm -rf node_modules
npm install
```

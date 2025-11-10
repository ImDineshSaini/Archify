#!/bin/bash
# Quick verification script to test if the application works

set -e

echo "🔍 Archify Application Verification Script"
echo "=========================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 1. Check Python syntax
echo "1️⃣  Checking Python syntax..."
cd backend
python3 -m py_compile app/main.py
python3 -m py_compile app/core/exceptions.py
python3 -m py_compile app/core/logging_config.py
python3 -m py_compile app/core/error_handlers.py
python3 -m py_compile app/repositories/user_repository.py
python3 -m py_compile app/use_cases/auth_use_cases.py
python3 -m py_compile app/api/auth_v2.py
echo -e "${GREEN}✅ Python syntax check passed${NC}"
echo ""

# 2. Check imports
echo "2️⃣  Checking imports..."
python3 -c "from app.core.exceptions import BaseAppException, InvalidCredentialsError"
python3 -c "from app.core.logging_config import get_logger, setup_logging"
python3 -c "from app.core.error_handlers import register_exception_handlers"
python3 -c "from app.repositories.user_repository import UserRepository"
python3 -c "from app.use_cases.auth_use_cases import LoginUseCase, RegisterUseCase"
python3 -c "from app.api.auth_v2 import router"
echo -e "${GREEN}✅ All imports working${NC}"
echo ""

cd ..

# 3. Check Docker Compose file
echo "3️⃣  Checking Docker Compose configuration..."
docker-compose config > /dev/null
echo -e "${GREEN}✅ Docker Compose config valid${NC}"
echo ""

# 4. Check environment file
echo "4️⃣  Checking environment configuration..."
if [ -f "backend/.env" ]; then
    echo -e "${GREEN}✅ .env file exists${NC}"
else
    echo -e "${YELLOW}⚠️  .env file not found, using .env.example${NC}"
    cp backend/.env.example backend/.env
fi
echo ""

echo "=========================================="
echo -e "${GREEN}✅ Basic verification passed!${NC}"
echo ""
echo "Next steps:"
echo "1. Start the application: docker-compose up -d"
echo "2. Check logs: docker-compose logs -f backend"
echo "3. Test health: curl http://localhost:8000/health"
echo "4. Test auth: curl -X POST http://localhost:8000/api/v2/auth/login ..."
echo ""
echo "See PRODUCTION_READINESS.md for full checklist"

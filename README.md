# 🏗️ Archify - AI-Powered Code Analysis Platform

Archify is a comprehensive code analysis platform that leverages AI and static analysis tools to provide deep insights into your codebase's architecture, maintainability, reliability, scalability, and security.

## ✨ Features

- 🔐 **User Authentication** - Secure JWT-based authentication system
- 🏢 **Multi-Tenancy** - Schema-based isolation for organizations (optional)
- 📁 **Repository Management** - Support for GitHub and GitLab repositories
- 🤖 **AI-Powered Analysis** - Multi-LLM support (Claude, OpenAI, Azure OpenAI)
- 📊 **Comprehensive Metrics** - Code quality, complexity, and architecture analysis
- 💡 **Smart Suggestions** - AI-generated recommendations for improvements
- 🎯 **Quality Scores** - Maintainability, Reliability, Scalability, and Security ratings
- ⚙️ **Admin Settings** - Configure LLM providers and Git tokens
- 📈 **Dashboard** - Intuitive Material-UI based interface

## 🏗️ Architecture

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│   React     │────▶│   FastAPI    │────▶│ PostgreSQL  │
│  Frontend   │     │   Backend    │     │  Database   │
└─────────────┘     └──────────────┘     └─────────────┘
                           │
                           ├────▶ Redis Cache
                           │
                           ├────▶ GitHub/GitLab API
                           │
                           └────▶ LLM Services
                                  (Claude, OpenAI, Azure)
```

## 🛠️ Tech Stack

### Backend
- **FastAPI** - Modern Python web framework
- **SQLAlchemy** - SQL toolkit and ORM
- **Alembic** - Database migrations
- **PostgreSQL** - Primary database
- **Redis** - Caching layer
- **LangChain** - LLM orchestration
- **Radon & Lizard** - Code analysis tools

### Frontend
- **React.js** - UI library
- **Material-UI (MUI)** - Component library
- **Redux Toolkit** - State management
- **React Router** - Navigation
- **Axios** - HTTP client
- **Recharts** - Data visualization

### Infrastructure
- **Docker & Docker Compose** - Containerization
- **Nginx** (production) - Reverse proxy

## 🚀 Quick Start

Choose your preferred deployment method:

### Option A: Docker Compose (Easiest - Recommended)

**Prerequisites:** Docker and Docker Compose

```bash
# 1. Clone repository
git clone https://github.com/yourusername/archify.git
cd archify

# 2. Start with Docker Compose
docker compose up -d

# OR if you have older docker-compose
docker-compose up -d

# OR using Makefile shortcuts
make up
```

### Option B: Podman Compose

**Prerequisites:** Podman and Podman Compose

```bash
# 1. Clone repository
git clone https://github.com/yourusername/archify.git
cd archify

# 2. Start with Podman Compose
podman-compose up -d
```

### Option C: Local Development (No Docker)

**Prerequisites:** Python 3.11+, Node.js 18+, PostgreSQL 15+

```bash
# 1. Clone repository
git clone https://github.com/yourusername/archify.git
cd archify

# 2. Setup backend
chmod +x setup-backend.sh
./setup-backend.sh

# 3. Setup frontend
chmod +x setup-frontend.sh
./setup-frontend.sh

# 4. See LOCAL_SETUP.md for detailed instructions
```

### Access the Application
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

### First Time Setup

1. **Register an account**
   - Go to http://localhost:3000/register
   - Create your first user account

2. **Configure LLM Provider** (Admin)
   - Navigate to Settings
   - Choose your LLM provider (Claude, OpenAI, or Azure)
   - Enter your API key

3. **Configure Git Integration** (Optional)
   - Go to Settings → Git Integration
   - Add your GitHub or GitLab access token
   - This is required for private repositories

4. **Add a Repository**
   - Go to Repositories
   - Click "Add Repository"
   - Enter the repository URL
   - Start analysis!

## 📋 Available Commands

```bash
make build          # Build all containers
make up             # Start all services
make down           # Stop all services
make restart        # Restart all services
make logs           # View logs from all services
make backend-logs   # View backend logs
make frontend-logs  # View frontend logs
make db-migrate     # Create new database migration
make db-upgrade     # Apply database migrations
make clean          # Remove all containers and volumes
make shell-backend  # Open shell in backend container
make shell-frontend # Open shell in frontend container
```

## 🔧 Configuration

### LLM Providers

#### Claude (Anthropic)
1. Get API key from https://console.anthropic.com
2. Navigate to Settings → LLM Provider
3. Select "Claude" and enter your API key

#### OpenAI
1. Get API key from https://platform.openai.com
2. Navigate to Settings → LLM Provider
3. Select "OpenAI" and enter your API key

#### Azure OpenAI
1. Set up Azure OpenAI resource in Azure Portal
2. Get endpoint URL and deployment name
3. Navigate to Settings → LLM Provider
4. Select "Azure" and enter required details

### Git Integration

#### GitHub
1. Go to Settings → Developer settings → Personal access tokens
2. Generate new token with `repo` scope
3. Add token in Archify Settings → Git Integration

#### GitLab
1. Go to Preferences → Access Tokens
2. Create token with `read_repository` scope
3. Add token in Archify Settings → Git Integration

## 📊 Analysis Metrics

Archify provides comprehensive analysis across four key dimensions:

### 1. Maintainability Score
- Code complexity analysis
- Function length and nesting
- Comment coverage
- Code duplication

### 2. Reliability Score
- Error handling patterns
- Test coverage indicators
- Documentation quality
- Code consistency

### 3. Scalability Score
- Architecture patterns
- Design principles
- Modularity assessment
- Dependency management

### 4. Security Score
- Security vulnerability detection
- Code injection risks
- Dependency vulnerabilities
- Best practices compliance

## 🏃‍♂️ Development

### Backend Development

```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Run migrations
alembic upgrade head

# Create new migration
alembic revision --autogenerate -m "description"

# Run development server
uvicorn app.main:app --reload
```

### Frontend Development

```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev

# Build for production
npm run build
```

## 🗄️ Database Migrations

```bash
# Create a new migration
make db-migrate message="add new table"

# Apply migrations
make db-upgrade

# Rollback migration
docker-compose exec backend alembic downgrade -1
```

## 🔐 Security Considerations

1. **Change default secrets** in production
   - Update `SECRET_KEY` and `JWT_SECRET_KEY` in `.env`

2. **Use environment variables** for sensitive data
   - Never commit API keys to version control

3. **HTTPS in production**
   - Configure SSL/TLS certificates
   - Use reverse proxy (Nginx/Traefik)

4. **Database security**
   - Use strong passwords
   - Restrict network access
   - Regular backups

## 📁 Project Structure

```
archify/
├── backend/
│   ├── app/
│   │   ├── api/           # API endpoints
│   │   ├── core/          # Core functionality
│   │   ├── models/        # Database models
│   │   ├── schemas/       # Pydantic schemas
│   │   ├── services/      # Business logic
│   │   └── main.py        # FastAPI application
│   ├── alembic/           # Database migrations
│   ├── tests/             # Backend tests
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/    # React components
│   │   ├── pages/         # Page components
│   │   ├── services/      # API services
│   │   ├── store/         # Redux store
│   │   ├── theme/         # MUI theme
│   │   └── App.jsx        # Main app component
│   ├── Dockerfile
│   └── package.json
├── docker-compose.yml
├── Makefile
├── .env.example
└── README.md
```

## 🧪 Testing

### Backend Tests
```bash
cd backend
pytest tests/
```

### Frontend Tests
```bash
cd frontend
npm test
```

## 🚢 Production Deployment

1. **Update environment variables**
   - Set `DEBUG=False`
   - Use secure passwords
   - Configure proper SECRET_KEY

2. **Build production images**
```bash
docker-compose -f docker-compose.prod.yml build
```

3. **Deploy with orchestration**
   - Use Kubernetes/Docker Swarm for scaling
   - Configure load balancer
   - Set up monitoring and logging

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License.

## 🙏 Acknowledgments

- **FastAPI** for the excellent Python web framework
- **Material-UI** for beautiful React components
- **Anthropic Claude** for powerful AI capabilities
- **LangChain** for LLM orchestration
- All open-source contributors

## 📧 Support

For issues and questions:
- Create an issue on GitHub
- Email: support@archify.io

## 🏢 Multi-Tenancy

Archify supports **schema-based multi-tenancy** for SaaS deployments:

- ✅ Complete data isolation per organization
- ✅ Automatic schema creation and migration
- ✅ Tenant-aware routing and middleware
- ✅ Independent credentials and settings per tenant
- ✅ Easy tenant provisioning via API or UI

**Enable multi-tenancy:**
```bash
ENABLE_MULTI_TENANCY=true
```

**See [MULTI_TENANCY.md](MULTI_TENANCY.md) for complete guide.**

## 🗺️ Roadmap

- [x] Multi-tenancy support (schema-based)
- [ ] Multi-repository comparison
- [ ] Historical trend analysis
- [ ] CI/CD integration
- [ ] Custom analysis rules
- [ ] Team collaboration features
- [ ] API rate limiting
- [ ] WebSocket for real-time updates
- [ ] Export reports (PDF, JSON)
- [ ] Code smell detection
- [ ] Performance benchmarking

---

Built with ❤️ for better code quality

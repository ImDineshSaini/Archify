# Archify

AI-powered code analysis platform that scans your repositories and provides actionable insights on maintainability, reliability, scalability, and security.

## What It Does

- Connects to GitHub/GitLab repositories
- Runs static analysis (complexity, duplication, code smells)
- Uses AI (Claude, OpenAI, or Azure OpenAI) for deep architectural analysis
- Generates quality scores and improvement recommendations

## Tech Stack

- **Backend:** FastAPI, PostgreSQL, Redis, LangChain
- **Frontend:** React, Material-UI, Redux Toolkit
- **Analysis:** Radon, Lizard, AI-powered insights
- **Deployment:** Docker Compose

## Quick Start

```bash
git clone https://github.com/ImDineshSaini/Archify.git
cd Archify
docker compose up -d
```

Open http://localhost:3000, register an account, configure your LLM provider in Settings, and add a repository to analyze.

## Local Development

See [LOCAL_SETUP.md](LOCAL_SETUP.md) for running without Docker.

## License

MIT

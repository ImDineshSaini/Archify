# Archify

AI-powered code analysis platform that helps engineering teams review architecture quality, identify technical debt, and get actionable improvement recommendations across their repositories.

## Why Archify?

Manual code reviews catch bugs but often miss architectural problems — poor modularity, scalability bottlenecks, security gaps, and mounting technical debt. Archify automates this by combining static analysis with AI to evaluate your codebase across 40+ quality attributes and give you a clear picture of where you stand.

## What It Analyzes

- **Maintainability** — complexity, function length, nesting depth, code duplication, comment coverage
- **Reliability** — error handling patterns, test coverage indicators, code consistency
- **Scalability** — architecture patterns, modularity, dependency management, design principles
- **Security** — vulnerability detection, injection risks, dependency issues, best practices
- **NFR Assessment** — 40+ non-functional requirements including performance, resilience, observability, portability, and more
- **Deep Analysis** — multi-layer AI examination that breaks down findings by architecture layer with concrete recommendations

## How It Works

1. Connect your GitHub or GitLab repository
2. Archify clones the repo and runs static analysis (Radon, Lizard)
3. AI (Claude, OpenAI, or Azure OpenAI) performs deep architectural review
4. Get quality scores, visualizations, and prioritized recommendations

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

Open http://localhost:3000 to get started.

## Setup

1. **Register** — Go to `/register` and create an account. The first user is automatically promoted to **admin**.
2. **Configure LLM** — Go to Settings and add your API key for Claude, OpenAI, or Azure OpenAI.
3. **Connect Git** (optional) — Add a GitHub/GitLab access token in Settings for private repo access.
4. **Analyze** — Add a repository URL and start your first analysis.

## Local Development

See [LOCAL_SETUP.md](LOCAL_SETUP.md) for running without Docker.

## License

MIT

# FastAPI Template

A production-oriented FastAPI starter template: async SQLAlchemy + PostgreSQL, Redis, Alembic migrations, JWT auth, structured logging, and a clean layered layout ready to clone for any new project.

## Stack

- **FastAPI** — async web framework, auto-generated OpenAPI docs
- **SQLAlchemy 2.0 (async)** + **asyncpg** — PostgreSQL access
- **Alembic** — database migrations
- **Redis** — caching / ephemeral state
- **Pydantic v2** + **pydantic-settings** — validation and typed configuration
- **PyJWT** + **bcrypt** — authentication and password hashing
- **uv** — dependency management
- **Ruff** + **pre-commit** — linting and formatting
- **pytest** (async) — test suite
- **Docker Compose** — local Postgres + Redis + backend

## Project layout

```
.
├── backend/                # FastAPI application (see backend/README.md)
│   ├── app/
│   │   ├── main.py         # App factory + module entrypoint
│   │   ├── core/           # config, db, redis, security, auth, exceptions, logging
│   │   ├── api/            # router, dependencies, route handlers & schemas
│   │   ├── models/         # SQLAlchemy models
│   │   ├── schemas/        # shared Pydantic schemas (base, pagination)
│   │   ├── services/       # business logic (base CRUD + user)
│   │   └── middlewares/    # CORS, request id, request logging
│   ├── alembic/            # async migrations
│   ├── scripts/            # maintenance helpers (e.g. seed_db.py)
│   └── tests/              # backend test suite
├── docker-compose.yml      # backend + postgres + redis
├── Makefile                # thin command wrappers
└── package.json            # npm-script equivalents of the Make targets
```

## Requirements

- Python 3.12+
- [uv](https://docs.astral.sh/uv/)
- Docker with Compose (for local PostgreSQL and Redis)

## Quick start

From the repository root:

```bash
cp backend/.env.example backend/.env
docker compose up -d          # start postgres + redis (+ backend)
cd backend
uv sync --all-groups
uv run alembic upgrade head    # apply migrations
uv run python -m backend.app.main --host 0.0.0.0 --port 8000 --reload
```

Interactive API docs are then available at http://localhost:8000/docs (enabled while `DEBUG=true`).

## Common commands

Run from the `backend/` directory. `make <target>` and `npm run <target>` are equivalent wrappers.

| Task | Make | Direct |
|------|------|--------|
| Run (reload) | `make dev` | `uv run python -m backend.app.main --reload` |
| Run | `make run` | `uv run python -m backend.app.main` |
| Tests | `make test` | `uv run pytest tests/ -v` |
| Lint | `make lint` | `uv run ruff check . && uv run ruff format --check .` |
| Format | `make format` | `uv run ruff check --fix . && uv run ruff format .` |
| Migrate | `make migrate` | `uv run alembic upgrade head` |
| New migration | `make migration name="..."` | `uv run alembic revision --autogenerate -m "..."` |
| Start services | `make docker-up` | `docker compose up -d` |
| Stop services | `make docker-down` | `docker compose down` |

## API endpoints

All routes are mounted under the `/api/v1` prefix:

- `GET  /api/v1/health` — service health check
- `GET  /api/v1/info` — application info
- `/api/v1/users` — user resource (CRUD)

## Configuration

Settings are loaded from `backend/.env` via `pydantic-settings` (see [backend/app/core/config.py](backend/app/core/config.py)). Key variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `PROJECT_NAME` | `FastAPI Template` | App title |
| `DEBUG` | `true` | Enables `/docs`, `/redoc` and dev-only options |
| `DATABASE_URL` | `postgresql+asyncpg://user:password@localhost:5432/dbname` | Async Postgres DSN |
| `REDIS_URL` | `redis://localhost:6379/0` | Redis connection |
| `ALLOWED_ORIGINS` | `["http://localhost:8000"]` | CORS allow-list |
| `SECRET_KEY` | *(change in production)* | JWT signing key |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `30` | JWT lifetime |
| `BYPASS_AUTH` | `true` | Skips JWT verification — **only allowed when `DEBUG=true`** |

> ⚠️ Before deploying outside local dev, set a real `SECRET_KEY`, `DEBUG=false`, and `BYPASS_AUTH=false`. The config refuses to start if `BYPASS_AUTH=true` while `DEBUG=false`.

## Docker

`docker-compose.yml` starts three services:

- `backend` on `localhost:8000`
- `postgres` on `localhost:5432`
- `redis` on `localhost:6379`

The backend container receives `DATABASE_URL` and `REDIS_URL` pointing at the Compose service names, so it works inside the container network with no extra setup.

See [backend/README.md](backend/README.md) for backend-specific details.

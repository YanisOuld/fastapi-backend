# Backend

This folder contains the FastAPI backend only: app code, Alembic migrations, tests, and its own `pyproject.toml`/`uv.lock`.

## Requirements

- Python 3.12+
- [uv](https://docs.astral.sh/uv/)
- Docker with Compose for local PostgreSQL and Redis

## Quick start

Run these commands from the repository root:

```bash
cp backend/.env.example backend/.env
docker compose up -d
cd backend
uv sync --all-groups
uv run alembic upgrade head
uv run python -m backend.app.main --host 0.0.0.0 --port 8000 --reload
```

If you use the repo-level helpers instead, the equivalent commands are `make docker-up`, `make migrate`, `make dev`, `npm run docker:up`, `npm run migrate`, and `npm run dev`.

Interactive API docs are available at http://localhost:8000/docs when `DEBUG=true`.

## Running the app

The app entrypoint lives in [backend/app/main.py](app/main.py) and can be launched as a module:

```bash
uv run python -m backend.app.main --host 0.0.0.0 --port 8000
```

Add `--reload` for development.

## Docker

The backend image is built from [backend/Dockerfile](Dockerfile), and [docker-compose.yml](../docker-compose.yml) starts three services:

- `backend` on `localhost:8000`
- `postgres` on `localhost:5432`
- `redis` on `localhost:6379`

The backend service gets `DATABASE_URL` and `REDIS_URL` pointing at the Compose service names, so it works inside the container network without extra setup.

## Structure

```
app/
  main.py            FastAPI app factory + module entrypoint
  core/              config, db, redis, security, auth, exceptions, logging
  api/               router, dependencies, route schemas, route handlers
  middlewares/       CORS, request id, request logging
alembic/             async migrations
scripts/             maintenance helpers
tests/               backend test suite
```

## Notes

- `BYPASS_AUTH=true` is allowed only while `DEBUG=true`.
- The repo-level `Makefile` and `package.json` are thin wrappers around backend commands for convenience.

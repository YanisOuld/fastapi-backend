# FastAPI Template

Base template for a FastAPI backend: JWT auth, PostgreSQL (async SQLAlchemy), Redis, Alembic migrations, tests, CI.

## Requirements

- Python 3.12+ (see [.python-version](.python-version))
- [uv](https://docs.astral.sh/uv/) — dependency management
- Docker (with the Compose plugin) — runs PostgreSQL and Redis locally
- `make` (optional — every command has an npm equivalent for native Windows)

## Quick start

```bash
cp .env.example .env          # set a real SECRET_KEY for production
make docker-up                 # starts postgres + redis (docker-compose.yml)
uv sync --all-groups           # install dependencies
make migrate                   # apply database migrations
make dev                       # start the server with auto-reload
```

If `make` is not available (native Windows), use the npm equivalents: `npm run docker:up`, `npm run migrate`, `npm run dev`.

Interactive API docs: http://localhost:8000/docs (only exposed when `DEBUG=true`).

## Running the server

The app runs locally with uvicorn; Docker is only used for the infrastructure (see next section).

| Mode | Command | Notes |
|---|---|---|
| Development | `make dev` / `npm run dev` | auto-reload on file changes |
| Production-like | `make run` / `npm run start` | no reload |

Both serve on `0.0.0.0:8000`. Under the hood they run:

```bash
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 [--reload]
```

Before the first run, make sure:

1. `.env` exists (`cp .env.example .env`) — settings are loaded from it at startup.
2. Postgres and Redis are up (`make docker-up`).
3. Migrations are applied (`make migrate`).

## Docker

[docker-compose.yml](docker-compose.yml) provides the two services the app depends on — it does **not** containerize the app itself:

- **postgres** (`postgres:16-alpine`) on `localhost:5432` — user `user`, password `password`, database `dbname` (matches the default `DATABASE_URL` in `.env.example`)
- **redis** (`redis:7-alpine`) on `localhost:6379`

```bash
make docker-up      # docker compose up -d   (npm run docker:up)
make docker-down    # docker compose down    (npm run docker:down)
```

Postgres data persists in the `postgres_data` volume across restarts. Both services have healthchecks; give them a few seconds after `docker-up` before running migrations.

## Project structure

```
app/
  main.py              single entry point — creates the FastAPI app, wires middlewares/exceptions/routers
  core/
    config.py          Settings (pydantic-settings), loaded from .env
    db.py               async SQLAlchemy engine + session
    redis.py            async Redis client
    security.py          password hashing (bcrypt) + JWT encode/decode
    auth.py              get_current_user_id dependency (verifies the JWT, or bypasses it if BYPASS_AUTH=true)
    exceptions.py         AppException and subclasses + global handlers
    logging.py            setup_logging() / get_logger()
    constant.py            global constants (pagination, etc.)
  models/
    base.py               SQLAlchemy Base + AppModel (UUID id + created_at/updated_at)
  schemas/
    base.py                AppSchema — mandatory Pydantic base for every schema in the project
    pagination.py           generic Page[T] for paginated responses
  services/
    base.py                 BaseService[Model] — generic CRUD (get_by_id, get_all, create, delete)
  api/
    router.py                central api_router, aggregates all sub-routers
    dependancies.py           DbSession, CurrentUserId, RedisClient — typed Annotated dependencies
    routes/                   one file per feature (health.py, info.py, ...)
    schemas/                  request/response schemas per route, inherit from AppSchema
  middlewares/
    cors.py                   CORS (open origins in DEBUG, ALLOWED_ORIGINS otherwise)
    request_id.py              X-Request-ID header on every request
    logging.py                  logs method/path/status/duration per request
alembic/                       migrations (async, reads DATABASE_URL from Settings)
scripts/                       standalone scripts (seed, maintenance) — pattern in seed_db.py
tests/                         conftest.py provides an HTTP client with mocked DB/Redis
```

## Conventions

- **Schemas**: always inherit from `AppSchema` ([app/schemas/base.py](app/schemas/base.py)), never from `pydantic.BaseModel` directly.
- **Route schemas** live in `app/api/schemas/`, co-located with their route. Reusable generic schemas (e.g. `Page`) live in `app/schemas/`.
- **Business logic** goes in services inheriting from `BaseService[Model]`, not in routes.
- **Business exceptions**: raise a subclass of `AppException` (`NotFoundException`, `ConflictException`, etc.) rather than `HTTPException` directly.
- **Route dependencies**: use the typed aliases from `app/api/dependancies.py` (`DbSession`, `CurrentUserId`, `RedisClient`) instead of raw `Depends(...)`.

## Auth — bypass mode

`BYPASS_AUTH=true` (the default in dev) disables JWT verification entirely — every request is treated as authenticated with a fixed user id. **The app deliberately refuses to start if `BYPASS_AUTH=true` while `DEBUG=false`** ([app/core/config.py](app/core/config.py)), to prevent this from slipping into production.

## Useful commands

| Make | npm | Description |
|---|---|---|
| `make dev` | `npm run dev` | server with auto-reload |
| `make run` | `npm run start` | server without reload |
| `make test` | `npm run test` | test suite |
| `make lint` | `npm run lint` | ruff check + format check |
| `make format` | `npm run format` | auto-fix lint and formatting |
| `make migration name="..."` | `npm run migration -- "..."` | generate an Alembic migration |
| `make migrate` | `npm run migrate` | apply migrations |
| `make docker-up` / `docker-down` | `npm run docker:up` / `docker:down` | local postgres + redis |

## CI

[.github/workflows/ci.yml](.github/workflows/ci.yml): lint (ruff) then tests (with ephemeral postgres/redis), on every push/PR to `main`.

FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/app/backend/.venv/bin:$PATH"

WORKDIR /app

COPY pyproject.toml uv.lock ./backend/

RUN uv sync --project /app/backend --frozen --no-dev --no-install-project

COPY . ./backend

EXPOSE 8000

CMD ["python", "-m", "backend.app.main", "--host", "0.0.0.0", "--port", "8000"]

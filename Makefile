dev:
	uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

run:
	uv run uvicorn app.main:app --host 0.0.0.0 --port 8000

test:
	uv run pytest tests/ -v

lint:
	uv run ruff check .
	uv run ruff format --check .

format:
	uv run ruff check --fix .
	uv run ruff format .

migrate:
	uv run alembic upgrade head

migration:
	uv run alembic revision --autogenerate -m "$(name)"

docker-up:
	docker compose up -d

docker-down:
	docker compose down

.PHONY: dev run test lint format migrate migration docker-up docker-down

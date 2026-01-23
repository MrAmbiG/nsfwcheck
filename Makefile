.PHONY: install venv run dev build du dudb dd test clean

# Install dependencies
install:
	uv sync

# Print activation command
venv:
	@echo "source .venv/bin/activate"

# Run locally with uv
run:
	uv run uvicorn app.main:app --host 0.0.0.0 --port 8000

# Run in dev mode (reload)
dev:
	uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Build the project
build:
	docker compose build

# Run with Docker Compose (Attached)
du:
	docker compose down && docker compose up --remove-orphans

# Run with Docker Compose (Detached + Build)
dudb:
	docker compose down && docker compose up -d --build --remove-orphans

# Stop all services
dd:
	docker compose down

# Run tests
test:
	bash scripts/test-stack.sh

# Cleanup
clean:
	rm -rf .venv .pytest_cache
	find . -type d -name "__pycache__" -exec rm -rf {} +

.PHONY: install run lint format test docker-build docker-up docker-down clean

# Variables
PYTHON = python
PIP = pip
UVICORN = uvicorn
APP_MODULE = app.main:app
PORT = 8000
HOST = 0.0.0.0

install:
	$(PIP) install -r requirements.txt

run:
	$(PYTHON) -m uvicorn $(APP_MODULE) --reload --host $(HOST) --port $(PORT)

lint:
	$(PYTHON) -m ruff check app
	$(PYTHON) -m mypy app

format:
	$(PYTHON) -m black app
	$(PYTHON) -m ruff check --fix app

test:
	$(PYTHON) -m pytest

docker-build:
	docker build -t streamline-backend:latest .

docker-up:
	docker-compose up --build -d

docker-down:
	docker-compose down

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".ruff_cache" -exec rm -rf {} +

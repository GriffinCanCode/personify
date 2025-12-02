.PHONY: help install build dev test clean db-init db-migrate

PYTHON := python3
VENV := venv
VENV_BIN := $(VENV)/bin
PIP := $(VENV_BIN)/pip
PYTHON_VENV := $(VENV_BIN)/python

help:
	@echo "Backend Makefile Commands:"
	@echo "  make install     - Create venv and install all dependencies"
	@echo "  make build       - Build/prepare backend (install + db-init)"
	@echo "  make dev         - Run development server"
	@echo "  make test        - Run tests"
	@echo "  make db-init     - Initialize database tables"
	@echo "  make clean       - Remove venv and cache files"
	@echo "  make lint        - Run linters"

install:
	@echo "📦 Installing backend dependencies..."
	@test -d $(VENV) || $(PYTHON) -m venv $(VENV)
	@$(PIP) install --upgrade pip
	@$(PIP) install -r requirements.txt
	@echo "✓ Backend dependencies installed!"

build: install db-init
	@echo "✓ Backend built successfully!"

dev:
	@echo "🚀 Starting backend development server..."
	@CHROMA_TELEMETRY_IMPL="chromadb.telemetry.noop.Noop" $(VENV_BIN)/uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000

test:
	@echo "🧪 Running backend tests..."
	@$(VENV_BIN)/pytest

db-init:
	@echo "🗄️  Initializing database..."
	@$(PYTHON_VENV) -m backend.database.init_db

db-migrate:
	@echo "🔄 Running database migrations..."
	@$(VENV_BIN)/alembic upgrade head

lint:
	@echo "🔍 Running linters..."
	@$(VENV_BIN)/ruff check . || true
	@$(VENV_BIN)/mypy . || true

clean:
	@echo "🧹 Cleaning backend..."
	@rm -rf $(VENV)
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	@echo "✓ Backend cleaned!"


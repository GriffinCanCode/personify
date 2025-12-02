.PHONY: help install build dev test clean docker-up docker-down db-init status

help:
	@echo "═══════════════════════════════════════════════════════════"
	@echo "  Personify - Virtual Griffin"
	@echo "═══════════════════════════════════════════════════════════"
	@echo ""
	@echo "🚀 Quick Start:"
	@echo "  make install     - Install all dependencies (backend + frontend)"
	@echo "  make build       - Build entire project"
	@echo "  make dev         - Start full development environment"
	@echo "  make docker-up   - Start services with Docker Compose"
	@echo ""
	@echo "📦 Installation:"
	@echo "  make install-backend   - Install backend dependencies only"
	@echo "  make install-frontend  - Install frontend dependencies only"
	@echo ""
	@echo "🏗️  Build:"
	@echo "  make build-backend     - Build backend only"
	@echo "  make build-frontend    - Build frontend only"
	@echo ""
	@echo "🔧 Development:"
	@echo "  make dev-backend       - Run backend dev server"
	@echo "  make dev-frontend      - Run frontend dev server"
	@echo "  make dev-all          - Run both servers concurrently"
	@echo ""
	@echo "🐳 Docker:"
	@echo "  make docker-up         - Start all Docker services"
	@echo "  make docker-down       - Stop all Docker services"
	@echo "  make docker-logs       - View Docker logs"
	@echo "  make docker-rebuild    - Rebuild and restart services"
	@echo ""
	@echo "🗄️  Database:"
	@echo "  make db-init           - Initialize database tables"
	@echo "  make db-connect        - Connect to PostgreSQL"
	@echo ""
	@echo "🧪 Testing:"
	@echo "  make test              - Run all tests"
	@echo "  make test-backend      - Run backend tests"
	@echo "  make test-frontend     - Run frontend tests"
	@echo "  make test-system       - Run system integration test"
	@echo ""
	@echo "🧹 Cleanup:"
	@echo "  make clean             - Clean all build artifacts"
	@echo "  make clean-backend     - Clean backend only"
	@echo "  make clean-frontend    - Clean frontend only"
	@echo "  make clean-data        - Clean data directory (WARNING: deletes uploads!)"
	@echo ""
	@echo "📊 Status:"
	@echo "  make status            - Show status of all services"
	@echo ""

# ═══════════════════════════════════════════════════════════
# Installation
# ═══════════════════════════════════════════════════════════

install: install-backend install-frontend
	@echo ""
	@echo "✅ All dependencies installed!"
	@echo ""
	@echo "Next steps:"
	@echo "  1. Configure .env file with your API keys"
	@echo "  2. make docker-up      (start PostgreSQL)"
	@echo "  3. make dev           (start development servers)"
	@echo ""

install-backend:
	@echo "📦 Installing backend..."
	@cd backend && $(MAKE) install

install-frontend:
	@echo "📦 Installing frontend..."
	@cd frontend && $(MAKE) install

# ═══════════════════════════════════════════════════════════
# Build
# ═══════════════════════════════════════════════════════════

build: build-backend build-frontend
	@echo "✅ Full build complete!"

build-backend:
	@cd backend && $(MAKE) build

build-frontend:
	@cd frontend && $(MAKE) build

# ═══════════════════════════════════════════════════════════
# Development
# ═══════════════════════════════════════════════════════════

dev:
	@echo "🚀 Starting development environment..."
	@echo "   Backend:  http://localhost:8000"
	@echo "   Frontend: http://localhost:3000"
	@echo "   API Docs: http://localhost:8000/docs"
	@echo ""
	@./start-dev.sh

dev-backend:
	@cd backend && $(MAKE) dev

dev-frontend:
	@cd frontend && $(MAKE) dev

dev-all:
	@echo "🚀 Starting both backend and frontend..."
	@trap 'kill 0' INT; \
	(cd backend && $(MAKE) dev) & \
	(cd frontend && $(MAKE) dev) & \
	wait

# ═══════════════════════════════════════════════════════════
# Docker
# ═══════════════════════════════════════════════════════════

docker-up:
	@echo "🐳 Starting Docker services..."
	@docker-compose up -d
	@echo "✓ Services started!"
	@$(MAKE) status

docker-down:
	@echo "🐳 Stopping Docker services..."
	@docker-compose down

docker-logs:
	@docker-compose logs -f

docker-rebuild:
	@echo "🔨 Rebuilding Docker services..."
	@docker-compose down
	@docker-compose build --no-cache
	@docker-compose up -d

# ═══════════════════════════════════════════════════════════
# Database
# ═══════════════════════════════════════════════════════════

db-init:
	@cd backend && $(MAKE) db-init

db-connect:
	@echo "🗄️  Connecting to PostgreSQL..."
	@docker exec -it personify-postgres-1 psql -U postgres personify

# ═══════════════════════════════════════════════════════════
# Testing
# ═══════════════════════════════════════════════════════════

test: test-backend test-frontend
	@echo "✅ All tests passed!"

test-backend:
	@cd backend && $(MAKE) test

test-frontend:
	@cd frontend && $(MAKE) test

test-system:
	@echo "🧪 Running system integration test..."
	@python3 test_system.py

# ═══════════════════════════════════════════════════════════
# Cleanup
# ═══════════════════════════════════════════════════════════

clean: clean-backend clean-frontend
	@echo "✓ All cleaned!"

clean-backend:
	@cd backend && $(MAKE) clean

clean-frontend:
	@cd frontend && $(MAKE) clean

clean-data:
	@echo "⚠️  WARNING: This will delete all uploaded data!"
	@read -p "Are you sure? [y/N] " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		rm -rf data/uploads/*; \
		rm -rf data/processed/*; \
		rm -rf data/chromadb/*; \
		echo "✓ Data cleaned!"; \
	else \
		echo "Cancelled."; \
	fi

# ═══════════════════════════════════════════════════════════
# Status & Info
# ═══════════════════════════════════════════════════════════

status:
	@echo "📊 Service Status:"
	@echo ""
	@echo "🐳 Docker Services:"
	@docker ps --filter "name=personify" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" 2>/dev/null || echo "  No Docker services running"
	@echo ""
	@echo "📂 Data Directory:"
	@echo "  Uploads:   $(shell find data/uploads -type f 2>/dev/null | wc -l | tr -d ' ') files"
	@echo "  Processed: $(shell find data/processed -type f 2>/dev/null | wc -l | tr -d ' ') files"
	@echo ""
	@echo "🔧 Dependencies:"
	@if [ -d "backend/venv" ]; then echo "  ✓ Backend venv exists"; else echo "  ✗ Backend venv missing (run: make install-backend)"; fi
	@if [ -d "frontend/node_modules" ]; then echo "  ✓ Frontend node_modules exists"; else echo "  ✗ Frontend node_modules missing (run: make install-frontend)"; fi
	@echo ""

setup:
	@echo "🔧 Running setup script..."
	@./setup.sh

.DEFAULT_GOAL := help


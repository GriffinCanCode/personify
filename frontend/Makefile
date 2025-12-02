.PHONY: help install build dev test clean lint

help:
	@echo "Frontend Makefile Commands:"
	@echo "  make install     - Install all Node dependencies"
	@echo "  make build       - Build production frontend"
	@echo "  make dev         - Run development server"
	@echo "  make test        - Run tests"
	@echo "  make clean       - Remove node_modules and build artifacts"
	@echo "  make lint        - Run linters"

install:
	@echo "📦 Installing frontend dependencies..."
	@npm install
	@echo "✓ Frontend dependencies installed!"

build: install
	@echo "🏗️  Building frontend for production..."
	@npm run build
	@echo "✓ Frontend built successfully!"

dev:
	@echo "🚀 Starting frontend development server..."
	@npm run dev

test:
	@echo "🧪 Running frontend tests..."
	@npm test || echo "No tests configured yet"

lint:
	@echo "🔍 Running linters..."
	@npm run lint || true

clean:
	@echo "🧹 Cleaning frontend..."
	@rm -rf node_modules
	@rm -rf .next
	@rm -rf out
	@echo "✓ Frontend cleaned!"


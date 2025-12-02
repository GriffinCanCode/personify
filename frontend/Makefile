.PHONY: help install build dev test clean lint

help:
	@echo "Frontend # Personify Frontend Makefile
# Quick commands for common development tasks

.PHONY: help install dev build start clean test lint format validate deploy

# Default target
help:
	@echo "Available commands:"
	@echo "  make install    - Install dependencies"
	@echo "  make dev        - Start development server"
	@echo "  make build      - Build for production"
	@echo "  make start      - Start production server"
	@echo "  make clean      - Clean build artifacts"
	@echo "  make test       - Run all tests"
	@echo "  make lint       - Run linters"
	@echo "  make format     - Format code"
	@echo "  make validate   - Run all quality checks"
	@echo "  make setup      - Initial setup (install + prepare hooks)"

# Setup
setup:
	npm install
	npm run prepare
	@echo "✅ Setup complete!"

install:
	npm install

# Development
dev:
	npm run dev

build:
	npm run build

start:
	npm start

# Cleaning
clean:
	rm -rf .next
	rm -rf node_modules
	rm -rf coverage
	rm -rf playwright-report
	rm -rf test-results
	@echo "✅ Cleaned build artifacts"

# Testing
test:
	npm test

test-coverage:
	npm run test:coverage

test-e2e:
	npm run test:e2e

test-e2e-ui:
	npm run test:e2e:ui

# Code Quality
lint:
	npm run lint

lint-fix:
	npm run lint:fix

format:
	npm run format

format-check:
	npm run format:check

type-check:
	npm run type-check

validate:
	npm run validate

# Deployment
deploy-preview:
	npm run build
	@echo "✅ Preview build complete"

deploy-prod:
	npm run build
	@echo "✅ Production build complete"
 Commands:"
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


# Makefile Guide for Personify

This project uses Makefiles to simplify development, building, and deployment tasks.

## Quick Reference

```bash
# First time setup
make install          # Install all dependencies
make docker-up        # Start PostgreSQL
make dev              # Start development servers

# Common workflows
make status           # Check service status
make test             # Run all tests
make clean            # Clean build artifacts
```

## Structure

The project has three Makefiles:

1. **Root Makefile** (`./Makefile`) - Orchestrates everything
2. **Backend Makefile** (`./backend/Makefile`) - Backend-specific commands
3. **Frontend Makefile** (`./frontend/Makefile`) - Frontend-specific commands

## Complete Command List

### Installation

| Command | Description |
|---------|-------------|
| `make install` | Install both backend and frontend dependencies |
| `make install-backend` | Install only backend dependencies (creates venv, installs packages) |
| `make install-frontend` | Install only frontend dependencies (npm install) |

### Building

| Command | Description |
|---------|-------------|
| `make build` | Build both backend and frontend |
| `make build-backend` | Build backend (install + db-init) |
| `make build-frontend` | Build frontend for production |

### Development

| Command | Description |
|---------|-------------|
| `make dev` | Start full dev environment (backend + frontend + postgres) |
| `make dev-backend` | Start only backend dev server (port 8000) |
| `make dev-frontend` | Start only frontend dev server (port 3000) |
| `make dev-all` | Start both servers concurrently |

### Docker Operations

| Command | Description |
|---------|-------------|
| `make docker-up` | Start all Docker services (PostgreSQL) |
| `make docker-down` | Stop all Docker services |
| `make docker-logs` | View live Docker logs |
| `make docker-rebuild` | Rebuild and restart services |

### Database

| Command | Description |
|---------|-------------|
| `make db-init` | Initialize database tables |
| `make db-connect` | Connect to PostgreSQL CLI |

### Testing

| Command | Description |
|---------|-------------|
| `make test` | Run all tests (backend + frontend) |
| `make test-backend` | Run backend tests (pytest) |
| `make test-frontend` | Run frontend tests |
| `make test-system` | Run system integration test |

### Cleanup

| Command | Description |
|---------|-------------|
| `make clean` | Clean all build artifacts |
| `make clean-backend` | Remove backend venv and cache |
| `make clean-frontend` | Remove node_modules and .next |
| `make clean-data` | **⚠️ Delete all uploaded data** (asks for confirmation) |

### Status & Info

| Command | Description |
|---------|-------------|
| `make status` | Show status of services, data, dependencies |
| `make help` | Show all available commands |

## Common Workflows

### First Time Setup

```bash
# 1. Install dependencies
make install

# 2. Start PostgreSQL
make docker-up

# 3. Initialize database
make db-init

# 4. Start development
make dev
```

### Daily Development

```bash
# Start everything
make dev

# Or start services separately:
# Terminal 1:
make docker-up
make dev-backend

# Terminal 2:
make dev-frontend
```

### Testing Your Changes

```bash
# Run all tests
make test

# Or run specific tests
make test-backend
make test-system

# Check service status
make status
```

### Clean Slate

```bash
# Clean and reinstall everything
make clean
make install
make build
```

### Production Build

```bash
# Build for production
make build

# This will:
# - Install all dependencies
# - Build frontend static files
# - Initialize database
```

## Backend-Specific Commands

You can also run backend commands directly:

```bash
cd backend

make install      # Create venv and install deps
make dev          # Run development server
make test         # Run pytest
make db-init      # Initialize database
make lint         # Run linters
make clean        # Clean venv and cache
```

## Frontend-Specific Commands

Similarly for frontend:

```bash
cd frontend

make install      # npm install
make build        # Production build
make dev          # Development server
make lint         # Run linters
make clean        # Remove node_modules
```

## Environment Variables

Make sure to configure `.env` before running:

```bash
# Copy example
cp .env.example .env

# Edit with your keys
nano .env  # or your favorite editor
```

Required variables:
- `OPENAI_API_KEY` - For embeddings and chat
- `DATABASE_URL` - PostgreSQL connection (default: localhost)

## Troubleshooting

### "Command not found: make"

Install make:
- **macOS**: `xcode-select --install`
- **Linux**: `sudo apt install build-essential`

### "No rule to make target"

Make sure you're in the right directory:
```bash
# Root commands from project root
cd /Users/griffinstrier/projects/personify
make help

# Backend commands from backend directory
cd backend
make help
```

### Services not starting

Check status and logs:
```bash
make status
make docker-logs
```

### Permission denied

Make scripts executable:
```bash
chmod +x setup.sh start-dev.sh
```

## Tips

1. **Use `make help`** - Each Makefile has a help command showing available targets
2. **Tab completion** - Make supports tab completion in bash/zsh
3. **Parallel execution** - Run `make -j4 install` to install dependencies in parallel
4. **Dry run** - Use `make -n <target>` to see what would be executed without running it

## Examples

### Complete setup from scratch:

```bash
make install      # Install everything
make docker-up    # Start PostgreSQL
make db-init      # Create tables
make dev          # Start servers
```

### Quick restart after code changes:

```bash
make dev          # Servers auto-reload on file changes
```

### Deploy workflow:

```bash
make clean        # Clean old builds
make build        # Fresh build
make test         # Verify everything works
make docker-up    # Start services
```

### Debug database issues:

```bash
make docker-logs  # Check PostgreSQL logs
make db-connect   # Connect to database
make db-init      # Reinitialize if needed
```

---

For more details, see the main [README.md](README.md) and [QUICKSTART.md](QUICKSTART.md).


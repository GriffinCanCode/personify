#!/bin/bash

# Setup backend .env file
echo "Setting up backend .env file..."

cat > .env << 'EOF'
# Database Configuration
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/personify

# OpenAI API
OPENAI_API_KEY=your_openai_api_key_here

# Anthropic API (optional)
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Application Settings
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=INFO

# Security
SECRET_KEY=dev-secret-key-please-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS Settings
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:3001

# ChromaDB Settings
CHROMA_HOST=localhost
CHROMA_PORT=8001
CHROMA_PERSIST_DIRECTORY=../data/chromadb
CHROMA_TELEMETRY_IMPL=chromadb.telemetry.noop.Noop

# Upload Settings
UPLOAD_DIR=../data/uploads
PROCESSED_DIR=../data/processed
MAX_UPLOAD_SIZE=10485760
EOF

echo "✅ Backend .env file created!"
echo ""
echo "⚠️  IMPORTANT: Edit backend/.env and add your actual API keys:"
echo "   - OPENAI_API_KEY"
echo "   - ANTHROPIC_API_KEY (optional)"
echo ""


#!/bin/bash

echo "Setting up Personify - Virtual Griffin"
echo "======================================="

# Create environment file
if [ ! -f .env ]; then
    echo "Creating .env file..."
    cp .env.example .env
    echo "⚠️  Please edit .env and add your API keys!"
else
    echo "✓ .env file already exists"
fi

# Create data directories
echo "Creating data directories..."
mkdir -p data/uploads data/processed data/chromadb

# Set up Python backend
echo ""
echo "Setting up Python backend..."
cd backend || exit

if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
fi

echo "Activating virtual environment..."
source venv/bin/activate

echo "Installing Python dependencies..."
pip install -r ../requirements.txt

echo "Initializing database..."
python3 -m backend.database.init_db

cd ..

# Set up Node frontend
echo ""
echo "Setting up Node frontend..."
cd frontend || exit

echo "Installing Node dependencies..."
npm install

cd ..

echo ""
echo "======================================="
echo "✓ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env and add your API keys"
echo "2. Start PostgreSQL (or use Docker Compose)"
echo "3. Run backend: cd backend && source venv/bin/activate && uvicorn backend.main:app --reload"
echo "4. Run frontend: cd frontend && npm run dev"
echo ""
echo "Or use Docker Compose: docker-compose up"


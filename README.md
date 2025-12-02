# Personify - Virtual Griffin

Build your identical digital twin using RAG (Retrieval-Augmented Generation).

## Overview

Personify creates Virtual Griffin, an AI-powered digital twin that can converse exactly like you by learning from your firsthand documents, communications, and personality data.

## Tech Stack

- **Backend**: Python, FastAPI
- **Frontend**: Next.js 14, React, TypeScript, Tailwind CSS
- **Vector Database**: ChromaDB
- **LLM**: OpenAI GPT-4o / Anthropic Claude
- **Database**: PostgreSQL

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 20+
- PostgreSQL
- Docker & Docker Compose (optional)

### Setup

1. **Clone and navigate to project:**
```bash
cd /Users/griffinstrier/projects/personify
```

2. **Set up environment variables:**
```bash
cp .env.example .env
# Edit .env and add your API keys
```

3. **Option A: Docker (Recommended)**
```bash
docker-compose up -d
```

4. **Option B: Local Development**

Backend:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn backend.main:app --reload
```

Frontend:
```bash
cd frontend
npm install
npm run dev
```

### Access

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## Project Structure

```
personify/
├── backend/
│   ├── api/              # API endpoints
│   ├── conversation/     # RAG conversation engine
│   ├── database/         # Database models & migrations
│   ├── feedback/         # Feedback collection
│   ├── ingestion/        # Document parsers
│   ├── personality/      # Personality analysis
│   ├── vectorstore/      # Vector DB operations
│   ├── config.py         # Configuration
│   └── main.py           # FastAPI app
├── frontend/
│   ├── app/              # Next.js pages
│   ├── components/       # React components
│   └── lib/              # Utilities & API client
├── data/
│   ├── uploads/          # Raw uploaded files
│   ├── processed/        # Processed documents
│   └── chromadb/         # Vector database
└── docker-compose.yml
```

## Usage

1. **Upload Your Data**: Navigate to /upload and upload documents, emails, journals, etc.
2. **Let It Process**: System will analyze your writing style and personality
3. **Chat with Virtual Griffin**: Go to /chat and start a conversation
4. **View Personality**: Check /personality to see your digital twin's profile

## Development

See [virtual-griffin.plan.md](virtual-griffin.plan.md) for detailed implementation plan.

## License

Private - Griffin Strier


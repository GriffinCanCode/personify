# Personify - Virtual Griffin Quickstart Guide

## Overview

Personify creates Virtual Griffin, your identical digital twin that can converse exactly like you by learning from your personal data.

## Prerequisites

- Python 3.11+
- Node.js 20+
- PostgreSQL (or Docker)
- OpenAI API key

## Installation

### Option 1: Automated Setup

```bash
chmod +x setup.sh
./setup.sh
```

### Option 2: Manual Setup

1. **Create environment file:**
```bash
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
```

2. **Backend setup:**
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r ../requirements.txt
python3 -m backend.database.init_db
```

3. **Frontend setup:**
```bash
cd frontend
npm install
```

## Running the Application

### Option 1: Docker Compose (Recommended)

```bash
docker-compose up
```

### Option 2: Development Mode

```bash
chmod +x start-dev.sh
./start-dev.sh
```

### Option 3: Manual

**Terminal 1 - PostgreSQL:**
```bash
docker run -d -p 5432:5432 \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=personify \
  postgres:16-alpine
```

**Terminal 2 - Backend:**
```bash
cd backend
source venv/bin/activate
uvicorn backend.main:app --reload
```

**Terminal 3 - Frontend:**
```bash
cd frontend
npm run dev
```

## Access

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## Usage Workflow

### 1. Upload Your Data

Navigate to `/upload` and upload your personal documents:
- Journals, notes, emails
- Documents (.txt, .pdf, .docx, .md)
- Voice recordings (will be transcribed)
- Social media exports (JSON)

**Tip**: Upload diverse content for best results (at least 500+ documents or equivalent text).

### 2. Build Personality Profile

Once documents are uploaded:
1. Click "Build Profile" on the upload page
2. Wait for analysis to complete (may take 1-5 minutes)
3. Profile is automatically saved

### 3. Chat with Virtual Griffin

Navigate to `/chat` and start a conversation:
- Ask questions you'd ask yourself
- Virtual Griffin responds exactly as you would
- Rate responses to improve accuracy

### 4. View Personality Profile

Navigate to `/personality` to see:
- Communication style metrics
- Personality traits
- Values hierarchy
- Knowledge domains
- Common phrases

## Tips for Best Results

### Data Quality

- **More is better**: 1,000+ text examples ideal
- **Diversity matters**: Mix of contexts (work, personal, creative)
- **Authentic content**: Unfiltered, genuine writing works best
- **Rich metadata**: Date-stamped content helps with evolution tracking

### Optimal Data Types

1. **Journals/Diaries**: Most valuable - authentic, unfiltered
2. **Sent Emails**: Shows professional voice
3. **Personal Notes**: Captures thinking patterns
4. **Creative Writing**: Reveals deeper personality
5. **Voice Transcripts**: Natural speech patterns

### Improving Accuracy

- Rate responses after each message
- Upload more data regularly
- Rebuild personality profile after adding significant new data
- Review personality dashboard and adjust if needed

## Troubleshooting

### "No personality profile found"
- Go to `/upload` and click "Build Profile"
- Ensure you've uploaded and processed documents first

### Uploads failing
- Check file formats are supported
- Ensure files aren't corrupted
- Check backend logs for specific errors

### Poor response quality
- Upload more diverse data (need 500+ examples minimum)
- Ensure data is authentic and representative
- Rebuild personality profile
- Check confidence scores - low scores indicate insufficient data

### Backend errors
- Verify `.env` has correct `OPENAI_API_KEY`
- Check PostgreSQL is running
- Check backend logs: `docker-compose logs backend`

## Architecture

```
User → Frontend (Next.js) → Backend API (FastAPI)
                                ↓
                    ┌──────────┴──────────┐
                    ↓                     ↓
            PostgreSQL            ChromaDB (Vectors)
            (Metadata)            (Embeddings)
                    ↓                     ↓
                    └──────────┬──────────┘
                               ↓
                        Personality Profile
                               ↓
                        RAG Engine
                               ↓
                        OpenAI GPT-4o
                               ↓
                        Virtual Griffin Response
```

## Development

### Run tests:
```bash
cd backend
pytest
```

### Database migrations:
```bash
cd backend
alembic revision --autogenerate -m "description"
alembic upgrade head
```

### Add new document parser:
Edit `backend/ingestion/parsers.py` and add to `ParserFactory.PARSERS`

## Privacy & Security

- **All data stays local** (except OpenAI API calls for embeddings/generation)
- **No data is shared** with third parties
- Vector database is local (ChromaDB)
- Implement authentication before deploying publicly

## Next Steps

1. **Fine-tuning**: Once you have 10k+ examples with feedback, consider fine-tuning a custom model
2. **Voice synthesis**: Add voice cloning for audio responses
3. **Mobile app**: Build mobile interface
4. **API access**: Use Virtual Griffin in other applications
5. **Shared access**: Let trusted people interact with your digital twin

## Support

- Check `README.md` for detailed documentation
- Review `virtual-griffin.plan.md` for architecture details
- Open issues on GitHub (if applicable)

## License

Private - Griffin Strier


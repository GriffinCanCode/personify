from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.config import settings
from backend.api import chat, upload, personality, feedback

app = FastAPI(
    title="Virtual Griffin API",
    description="RAG-based digital twin conversation system",
    version="0.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(chat.router, prefix=settings.API_V1_STR)
app.include_router(upload.router, prefix=settings.API_V1_STR)
app.include_router(personality.router, prefix=settings.API_V1_STR)
app.include_router(feedback.router, prefix=settings.API_V1_STR)

@app.get("/")
async def root():
    return {"message": "Virtual Griffin API", "version": "0.1.0"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

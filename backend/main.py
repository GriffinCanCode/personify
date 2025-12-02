from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import time
import uuid
from contextvars import ContextVar

from backend.config import settings
from backend.api import chat, upload, personality, feedback
from backend.logging_config import setup_logging, get_logger, LogContext

# Initialize logging
setup_logging(
    log_level=settings.LOG_LEVEL,
    json_logs=settings.LOG_JSON,
    log_file=settings.LOG_FILE if settings.LOG_FILE else None
)

logger = get_logger(__name__)
request_id_var: ContextVar[str] = ContextVar('request_id', default='')

app = FastAPI(
    title="Virtual Griffin API",
    description="RAG-based digital twin conversation system",
    version="0.1.0"
)

# Logging middleware for request/response tracking
@app.middleware("http")
async def logging_middleware(request: Request, call_next):
    """Log all requests with timing and context"""
    request_id = str(uuid.uuid4())
    request_id_var.set(request_id)
    
    start_time = time.perf_counter()
    
    with LogContext(
        request_id=request_id,
        method=request.method,
        path=request.url.path,
        client_ip=request.client.host if request.client else None
    ):
        logger.info(
            "request_started",
            method=request.method,
            path=request.url.path,
            query_params=dict(request.query_params)
        )
        
        try:
            response = await call_next(request)
            duration_ms = (time.perf_counter() - start_time) * 1000
            
            logger.info(
                "request_completed",
                status_code=response.status_code,
                duration_ms=duration_ms
            )
            
            response.headers["X-Request-ID"] = request_id
            return response
            
        except Exception as e:
            duration_ms = (time.perf_counter() - start_time) * 1000
            logger.error(
                "request_failed",
                error=str(e),
                duration_ms=duration_ms,
                exc_info=True
            )
            return JSONResponse(
                status_code=500,
                content={"detail": "Internal server error", "request_id": request_id},
                headers={"X-Request-ID": request_id}
            )

# CORS middleware
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

@app.on_event("startup")
async def startup_event():
    """Log application startup"""
    logger.info(
        "application_startup",
        project=settings.PROJECT_NAME,
        environment=settings.ENVIRONMENT,
        log_level=settings.LOG_LEVEL
    )

@app.on_event("shutdown")
async def shutdown_event():
    """Log application shutdown"""
    logger.info("application_shutdown", project=settings.PROJECT_NAME)

@app.get("/")
async def root():
    logger.debug("root_endpoint_called")
    return {"message": "Virtual Griffin API", "version": "0.1.0"}

@app.get("/health")
async def health():
    logger.debug("health_check")
    return {"status": "healthy"}

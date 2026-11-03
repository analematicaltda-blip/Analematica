import os
import time
import uuid
import logging
from fastapi import FastAPI, Request, Response, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette.staticfiles import StaticFiles
from app.api.v1.api import api_router
from app.core.config import settings
from app.core.logging_config import setup_logging

# Initialize Structured Logging
logger = setup_logging()

app = FastAPI(title=settings.PROJECT_NAME)

# Correlation ID and Request Latency Middleware
@app.middleware("http")
async def correlation_id_and_logging_middleware(request: Request, call_next):
    correlation_id = request.headers.get("X-Correlation-ID") or str(uuid.uuid4())
    request.state.correlation_id = correlation_id

    start_time = time.time()
    response: Response = await call_next(request)
    duration_ms = round((time.time() - start_time) * 1000, 2)

    response.headers["X-Correlation-ID"] = correlation_id

    # Log request details with structured context
    log_extra = {
        "correlation_id": correlation_id,
        "method": request.method,
        "path": request.url.path,
        "status_code": response.status_code,
        "duration_ms": duration_ms,
        "client_ip": request.client.host if request.client else "127.0.0.1"
    }

    if duration_ms > 1000:
        logging.warning(
            f"[OPERATIONAL ALERT / SLOW REQUEST] Path={request.url.path} Duration={duration_ms}ms",
            extra=log_extra
        )
    else:
        logging.info(
            f"HTTP Request Processed: {request.method} {request.url.path} -> {response.status_code}",
            extra=log_extra
        )

    return response

# Global Unhandled Exception Handler (500)
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    correlation_id = getattr(request.state, "correlation_id", str(uuid.uuid4()))
    logging.error(
        f"[UNHANDLED EXCEPTION 500] Path={request.url.path} Message={str(exc)}",
        exc_info=exc,
        extra={"correlation_id": correlation_id, "path": request.url.path}
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "Error interno del servidor. Por favor, contacte a soporte e indique el ID de correlación.",
            "correlation_id": correlation_id
        },
        headers={"X-Correlation-ID": correlation_id}
    )

# Service Unavailable Handler (503)
@app.exception_handler(503)
async def service_unavailable_handler(request: Request, exc: Exception):
    correlation_id = getattr(request.state, "correlation_id", str(uuid.uuid4()))
    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content={
            "detail": "El servicio se encuentra temporalmente en mantenimiento o no disponible.",
            "correlation_id": correlation_id
        },
        headers={"X-Correlation-ID": correlation_id, "Retry-After": "60"}
    )

# CORS Configuration
origins = getattr(settings, "BACKEND_CORS_ORIGINS", ["*"])
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Security Headers Middleware
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response: Response = await call_next(request)
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains; preload"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "geolocation=(self), microphone=()"
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
        "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
        "font-src 'self' https://fonts.gstatic.com; "
        "img-src 'self' data: https:; "
        "connect-src 'self' https:; "
        "frame-ancestors 'none';"
    )
    return response

# Custom StaticFiles class to serve assets with Immutable Cache-Control headers
class CachedStaticFiles(StaticFiles):
    def file_response(self, *args, **kwargs) -> Response:
        response = super().file_response(*args, **kwargs)
        response.headers["Cache-Control"] = "public, max-age=31536000, immutable"
        return response

# Create static directory if it doesn't exist
static_dir = "app/static"
if not os.path.exists(static_dir):
    os.makedirs(static_dir)

app.mount("/static", CachedStaticFiles(directory=static_dir), name="static")

app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/")
def read_root():
    return {"message": f"Welcome to {settings.PROJECT_NAME}"}

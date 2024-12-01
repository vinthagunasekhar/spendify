from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.core.config import settings
from app.api.v1.api import router as api_v1_router
import logging

#logging.basicConfig(level=logging.DEBUG)
#logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    description="Spendify API",
    debug=True
)

'''
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Enhanced logging middleware that properly handles request body"""
    try:
        # Log basic request info
        logger.debug(f"Incoming request: {request.method} {request.url}")
        logger.debug(f"Request headers: {request.headers}")

        # Create a copy of the request body
        body_bytes = await request.body()
        # Log the body content and length
        logger.debug(f"Request body length: {len(body_bytes)}")
        logger.debug(f"Request body content: {body_bytes.decode() if body_bytes else 'EMPTY'}")

        # We need to create a new request with the body since we've consumed it
        async def receive():
            return {"type": "http.request", "body": body_bytes}

        request._receive = receive
        response = await call_next(request)
        return response

    except Exception as e:
        logger.exception("Error processing request")
        return JSONResponse(
            status_code=400,
            content={
                "status": "error",
                "message": "Request processing error",
                "details": str(e)
            }
        )
''' #CORS Debugging logic

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_v1_router, prefix=settings.API_V1_STR)


@app.get("/")
async def root():
    return {
        "message": "Welcome to Spendify API",
        "version": "1.0.0",
        "database_url": settings.DATABASE_URL[:10] + "..."
    }
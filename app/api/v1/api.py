# app/api/v1/api.py
from fastapi import APIRouter
from app.api.v1.endpoints import health, auth  # We'll create these next

# Create main v1 router
router = APIRouter()

# Include different endpoint routers
router.include_router(
    health.router,
    prefix="/health",
    tags=["Health"]
)

router.include_router(
    auth.router,
    prefix="/auth",
    tags=["Authentication"]
)

# Add more routers as needed for your specific endpoints
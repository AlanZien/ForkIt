"""ForkIt API - Family meal planning backend."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routes.auth import router as auth_router

app = FastAPI(
    title="ForkIt API",
    description="Family meal planning and recipe management API",
    version="0.1.0",
)

# CORS middleware for mobile app
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router)


@app.get("/")
async def root() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "ok", "message": "ForkIt API is running"}


@app.get("/health")
async def health() -> dict[str, str]:
    """Health check for deployment platforms."""
    return {"status": "healthy"}

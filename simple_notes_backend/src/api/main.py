from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.db import engine
from src.api.models import Base
from src.api.routes_auth import router as auth_router
from src.api.routes_notes import router as notes_router
from src.api.schemas import HealthResponse

openapi_tags = [
    {"name": "health", "description": "Service health endpoints."},
    {"name": "auth", "description": "User registration/login endpoints (JWT bearer auth)."},
    {"name": "notes", "description": "CRUD endpoints for notes (authenticated)."},
]


def _init_db() -> None:
    """Create tables if they don't exist (lightweight for this simple app)."""
    Base.metadata.create_all(bind=engine)


_init_db()

app = FastAPI(
    title="Simple Notes API",
    description=(
        "Backend API for the Simple Notes app.\n\n"
        "Auth: use `Authorization: Bearer <token>` returned by `/auth/login`.\n"
        "All `/notes` endpoints require authentication."
    ),
    version="1.0.0",
    openapi_tags=openapi_tags,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For demo; restrict in production.
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get(
    "/",
    response_model=HealthResponse,
    tags=["health"],
    summary="Health check",
    description="Simple health check endpoint.",
    operation_id="health_check",
)
def health_check() -> HealthResponse:
    """Health check for load balancers/preview."""
    return HealthResponse(message="Healthy")


app.include_router(auth_router)
app.include_router(notes_router)

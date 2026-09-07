from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.auth import router as auth_router
from app.api.dashboard import router as dashboard_router
from app.api.discover import router as discover_router
from app.api.requests import router as requests_router
from app.api.workspace import router as workspace_router
from app.core.config import settings

app = FastAPI(
    title=settings.APP_NAME,
    description="SkillBridge — a peer-to-peer skill exchange platform. "
    "Teach what you know, learn what you love.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/api")
app.include_router(dashboard_router, prefix="/api")
app.include_router(discover_router, prefix="/api")
app.include_router(requests_router, prefix="/api")
app.include_router(workspace_router, prefix="/api")


@app.get("/", tags=["health"])
def root():
    return {"service": "SkillBridge API", "status": "ok"}


@app.get("/api/health", tags=["health"])
def health_check():
    return {"status": "ok", "environment": settings.ENVIRONMENT}


# Routers for users, skills, matching, requests, chat, sessions,
# reviews, credits, and notifications are wired up in later phases as
# each domain's models/schemas/services are built out.

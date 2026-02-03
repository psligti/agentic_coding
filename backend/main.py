import sys
from pathlib import Path

# Add opencode_python to Python path for SDK imports (absolute path for reliable imports)
sys.path.insert(0, "/Users/parkersligting/develop/pt/agentic_coding/.worktrees/webapp/opencode_python/src")

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from typing import AsyncGenerator


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    # Startup
    yield
    # Shutdown
    print("🛑 WebApp backend shutting down...")


app = FastAPI(
    title="WebApp API",
    description="Backend API for WebApp",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["root"])
async def root() -> dict[str, str]:
    return {
        "message": "Welcome to WebApp API",
        "version": "0.1.0",
        "docs": "/docs",
    }


@app.get("/health", tags=["health"])
async def health_check() -> dict[str, str | bool]:
    return {"status": "healthy", "database": True}


# Include API routes
from api import accounts, agents, health, messages, models, sessions, sessions_streaming, skills, streaming, tools

app.include_router(health.router, prefix="/api/v1")
app.include_router(messages.router)
app.include_router(sessions.router)
app.include_router(agents.router)
app.include_router(streaming.router)
app.include_router(sessions_streaming.router)
app.include_router(tools.router)
app.include_router(skills.router)
app.include_router(models.router)
app.include_router(accounts.router)


@app.get("/api/v1/info", tags=["api"])
async def api_info() -> dict[str, str]:
    return {
        "name": "WebApp API",
        "version": "0.1.0",
        "status": "operational",
    }


# Routes will be added here as the application grows
# from api import routes
# app.include_router(routes.router, prefix="/api/v1", tags=["api"])


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )

import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import RedirectResponse
from src.core.logging_config import setup_logging
from src.websocket.camera_control_stream import router as camera_control_stream_router
from src.service.camera.route import router as camera_router
from src.core.db import Base, engine  # <-- import Base and engine
import asyncio

# -----------------------------
# Logging
# -----------------------------
setup_logging()
logger = logging.getLogger(__name__)

# -----------------------------
# FastAPI app
# -----------------------------
app = FastAPI(
    debug=True,
    title="Camera Control API",
    description="Translates complex camera commands into a simple, unified API, enabling seamless control of diverse cameras directly from your web dashboard",
)

# -----------------------------
# CORS middleware
# -----------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------
# Root redirect
# -----------------------------
@app.get("/", include_in_schema=False)
def root_redirect():
    return RedirectResponse(url="/docs/")

# -----------------------------
# Include routers
# -----------------------------
app.include_router(camera_router, prefix="/camera", tags=["Camera Management"])
app.include_router(camera_control_stream_router, tags=["Camera Control and Streaming"])

# -----------------------------
# Database initialization on startup
# -----------------------------
@app.on_event("startup")
async def startup_event():
    logger.info("🚀 Initializing database...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("✅ Database initialized")

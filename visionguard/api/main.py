"""
VisionGuard FastAPI Application Server.
Provides OpenAPI documentation, REST endpoints, and WebSocket video/event streaming.
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from visionguard.api.routes import cameras, events, metrics, system
from visionguard.logging.logger import logger

app = FastAPI(
    title="VisionGuard Intelligent Video Analytics API",
    description="Production-grade REST and WebSocket API for real-time video analytics, object tracking, and event management.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Router Modules
app.include_router(system.router)
app.include_router(cameras.router)
app.include_router(events.router)
app.include_router(metrics.router)


@app.websocket("/api/v1/ws/stream")
async def websocket_stream_endpoint(websocket: WebSocket):
    await websocket.accept()
    logger.info("API: Client connected to WebSocket video stream")
    try:
        while True:
            # Receive ping/commands or push frame telemetry
            msg = await websocket.receive_text()
            await websocket.send_json({"status": "active", "message": "Stream alive"})
    except WebSocketDisconnect:
        logger.info("API: Client disconnected from WebSocket stream")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")

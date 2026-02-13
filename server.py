"""
Heisenberg Settings Server - FastAPI backend for configuration management
Provides HTTP API for settings management with live preview and auto-revert
"""

import asyncio
import socket
import threading
import time
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sse_starlette.sse import EventSourceResponse
import uvicorn

from settings_manager import load_settings, save_settings, update_setting

# Global state
preview_settings: Optional[dict] = None
original_settings: Optional[dict] = None
preview_timer: Optional[threading.Timer] = None
clients = []  # List of connected SSE clients
current_settings = {}

class SettingsRequest(BaseModel):
    sensitivity: Optional[float] = None
    mode: Optional[str] = None
    speech_speed: Optional[float] = None

class PreviewResponse(BaseModel):
    message: str
    time_remaining: int
    settings: dict


def find_available_port(start_port: int = 2026, max_port: int = 2100) -> int:
    """Find an available port starting from start_port"""
    for port in range(start_port, max_port + 1):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.bind(('127.0.0.1', port))
            sock.close()
            return port
        except OSError:
            continue
    raise RuntimeError("No available ports found")


def broadcast_update():
    """Broadcast settings update to all connected SSE clients"""
    for client_queue in clients:
        try:
            client_queue.put_nowait(current_settings)
        except:
            pass


def auto_revert():
    """Auto-revert to original settings after 120s"""
    global preview_settings, original_settings, current_settings
    if original_settings is not None:
        current_settings = original_settings.copy()
        preview_settings = None
        original_settings = None
        broadcast_update()
        print("[SERVER] Auto-revert triggered after 120s timeout")


def start_preview_timer():
    """Start the 120s preview timer"""
    global preview_timer
    if preview_timer is not None:
        preview_timer.cancel()
    preview_timer = threading.Timer(120.0, auto_revert)
    preview_timer.start()


def stop_preview_timer():
    """Stop the preview timer"""
    global preview_timer
    if preview_timer is not None:
        preview_timer.cancel()
        preview_timer = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup/shutdown"""
    global current_settings
    # Startup
    current_settings = load_settings()
    print(f"[SERVER] Loaded settings: {current_settings}")
    yield
    # Shutdown
    stop_preview_timer()
    print("[SERVER] Shutting down")


app = FastAPI(title="Heisenberg Settings Server", lifespan=lifespan)

# Enable CORS for web UI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/settings")
async def get_settings():
    """Get current settings"""
    return current_settings


@app.post("/settings/preview")
async def preview_settings_endpoint(request: SettingsRequest):
    """
    Apply settings temporarily for preview (120s timeout)
    Does NOT save to JSON file
    """
    global preview_settings, original_settings, current_settings
    
    # Store original if not already stored
    if original_settings is None:
        original_settings = current_settings.copy()
    
    # Update preview settings
    preview_settings = current_settings.copy()
    if request.sensitivity is not None:
        preview_settings['sensitivity'] = max(0.5, min(2.0, request.sensitivity))
    if request.mode is not None:
        preview_settings['mode'] = request.mode
    if request.speech_speed is not None:
        preview_settings['speech_speed'] = max(0.5, min(2.0, request.speech_speed))
    
    # Apply preview
    current_settings = preview_settings.copy()
    
    # Start/restart timer
    start_preview_timer()
    
    broadcast_update()
    
    return PreviewResponse(
        message="Preview mode active. Changes will auto-revert in 120 seconds unless committed.",
        time_remaining=120,
        settings=current_settings
    )


@app.post("/settings/commit")
async def commit_settings():
    """
    Commit preview settings to JSON file
    Stops the auto-revert timer
    """
    global preview_settings, original_settings
    
    if preview_settings is None:
        raise HTTPException(status_code=400, detail="No preview settings to commit")
    
    # Save to JSON
    success = save_settings(current_settings)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to save settings")
    
    # Stop timer
    stop_preview_timer()
    
    # Clear preview state
    preview_settings = None
    original_settings = None
    
    broadcast_update()
    
    return {
        "message": "Settings committed successfully",
        "settings": current_settings
    }


@app.post("/settings/revert")
async def revert_settings():
    """
    Revert to original settings (before preview)
    Stops the auto-revert timer
    """
    global preview_settings, original_settings, current_settings
    
    if original_settings is None:
        raise HTTPException(status_code=400, detail="No preview to revert")
    
    # Restore original
    current_settings = original_settings.copy()
    
    # Stop timer
    stop_preview_timer()
    
    # Clear preview state
    preview_settings = None
    original_settings = None
    
    broadcast_update()
    
    return {
        "message": "Settings reverted to original values",
        "settings": current_settings
    }


@app.get("/settings/time-remaining")
async def get_time_remaining():
    """Get remaining time for preview (if active)"""
    if preview_timer is None or original_settings is None:
        return {"active": False, "time_remaining": 0}
    
    # This is a simplified check - in production you'd track start time
    return {"active": True, "time_remaining": 120}


@app.get("/settings/stream")
async def settings_stream():
    """
    Server-Sent Events endpoint for live settings updates
    Clients connect here to receive real-time updates
    """
    queue = asyncio.Queue()
    clients.append(queue)
    
    try:
        # Send current settings immediately
        yield {
            "event": "message",
            "data": current_settings
        }
        
        # Wait for updates
        while True:
            settings = await queue.get()
            yield {
                "event": "message",
                "data": settings
            }
    finally:
        clients.remove(queue)


def run_server():
    """
    Start the FastAPI server with port fallback
    Updates settings.json with actual port used
    """
    # Load settings to get preferred port
    settings = load_settings()
    preferred_port = settings.get('port', 2026)
    
    # Try preferred port, fallback if taken
    try:
        port = find_available_port(preferred_port)
        if port != preferred_port:
            print(f"[SERVER] Port {preferred_port} unavailable, using port {port}")
            # Update settings with new port
            update_setting('port', port)
        else:
            print(f"[SERVER] Using port {port}")
    except RuntimeError as e:
        print(f"[SERVER] Error: {e}")
        raise
    
    # Run uvicorn
    uvicorn.run(app, host="127.0.0.1", port=port, log_level="info")


if __name__ == "__main__":
    run_server()

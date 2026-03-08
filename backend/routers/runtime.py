import asyncio
import os
import httpx
from fastapi import APIRouter, Depends, WebSocket
from services.security import get_current_user
from services import icecast_controller

router = APIRouter()
ICECAST_STATS_URL = os.getenv("ICECAST_STATS_URL", "http://icecast:8000/status-json.xsl")


@router.post("/start")
def start(_=Depends(get_current_user)):
    return icecast_controller.start_icecast()


@router.post("/stop")
def stop(_=Depends(get_current_user)):
    return icecast_controller.stop_icecast()


@router.post("/restart")
def restart(_=Depends(get_current_user)):
    return icecast_controller.restart_icecast()


@router.websocket("/ws/stats")
async def stats_ws(websocket: WebSocket):
    await websocket.accept()
    while True:
        async with httpx.AsyncClient(timeout=5) as client:
            try:
                response = await client.get(ICECAST_STATS_URL)
                payload = response.json()
            except Exception:
                payload = {"icestats": {"listeners": 0, "sources": 0}}
        await websocket.send_json(payload)
        await asyncio.sleep(2)

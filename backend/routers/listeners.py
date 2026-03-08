from typing import Optional
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from services.security import get_current_user
from services.admin_manager import list_listeners, kick_listener, move_listener

router = APIRouter()


class ListenersQuery(BaseModel):
    mount: str


class KickRequest(BaseModel):
    mount: str


class MoveRequest(BaseModel):
    mount: str
    destination: str
    listener_id: Optional[str] = None


@router.get('')
async def get_listeners(mount: str, _=Depends(get_current_user)):
    return await list_listeners(mount)


@router.post('/{listener_id}/kick')
async def kick(listener_id: str, payload: KickRequest, _=Depends(get_current_user)):
    return await kick_listener(payload.mount, listener_id)


@router.post('/{listener_id}/move')
async def move(listener_id: str, payload: MoveRequest, _=Depends(get_current_user)):
    return await move_listener(payload.mount, payload.destination, listener_id)

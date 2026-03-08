from fastapi import APIRouter, Depends
from pydantic import BaseModel
from services.security import get_current_user
from services.mount_manager import list_mounts, kill_source

router = APIRouter()


class KillSourceRequest(BaseModel):
    mount: str


@router.get("")
async def mounts(_=Depends(get_current_user)):
    return await list_mounts()


@router.post("/kill-source")
async def kill(payload: KillSourceRequest, _=Depends(get_current_user)):
    return await kill_source(payload.mount)

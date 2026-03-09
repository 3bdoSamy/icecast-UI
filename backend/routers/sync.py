from fastapi import APIRouter, Depends
from pydantic import BaseModel
from services.security import get_current_user
from services.sync_manager import sync_services, runtime_endpoints

router = APIRouter()


class SyncRequest(BaseModel):
    domain: str
    icecast_port: int = 8000
    https_enabled: bool = False
    ssl_mode: str = 'none'
    cloudflare_enabled: bool = False


@router.post('/services')
def sync(payload: SyncRequest, _=Depends(get_current_user)):
    return sync_services(
        payload.domain,
        payload.icecast_port,
        payload.https_enabled,
        payload.ssl_mode,
        payload.cloudflare_enabled,
    )


@router.get('/endpoints')
def endpoints(_=Depends(get_current_user)):
    return runtime_endpoints()

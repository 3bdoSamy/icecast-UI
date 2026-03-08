from fastapi import APIRouter, Depends
from pydantic import BaseModel
from services.security import get_current_user
from services import nginx_manager

router = APIRouter()


class NginxSettingsRequest(BaseModel):
    domain: str
    https_enabled: bool = False
    ssl_mode: str = 'none'
    cloudflare_enabled: bool = False
    icecast_port: int = 8000


class CertUploadRequest(BaseModel):
    cert_pem: str
    key_pem: str


@router.get('/settings')
def get_settings(_=Depends(get_current_user)):
    return nginx_manager.get_settings()


@router.post('/settings')
def save_settings(payload: NginxSettingsRequest, _=Depends(get_current_user)):
    settings = nginx_manager.save_settings(payload.model_dump())
    return nginx_manager.apply_nginx_config(settings)


@router.post('/ssl/cloudflare')
def upload_cloudflare(payload: CertUploadRequest, _=Depends(get_current_user)):
    nginx_manager.save_cloudflare_cert(payload.cert_pem, payload.key_pem)
    return {'status': 'uploaded'}


@router.post('/ssl/custom')
def upload_custom(payload: CertUploadRequest, _=Depends(get_current_user)):
    nginx_manager.save_custom_cert(payload.cert_pem, payload.key_pem)
    return {'status': 'uploaded'}


@router.post('/ssl/letsencrypt')
def setup_letsencrypt(payload: NginxSettingsRequest, _=Depends(get_current_user)):
    return nginx_manager.run_certbot(payload.domain)


@router.post('/restart')
def restart(_=Depends(get_current_user)):
    return nginx_manager.nginx_restart()


@router.post('/reload')
def reload(_=Depends(get_current_user)):
    return nginx_manager.nginx_reload()


@router.get('/test')
def test(_=Depends(get_current_user)):
    return nginx_manager.nginx_test()

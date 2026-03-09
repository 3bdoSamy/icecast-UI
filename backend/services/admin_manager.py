import os
import httpx

ICECAST_ADMIN_URL = os.getenv('ICECAST_ADMIN_URL', 'http://127.0.0.1:8000')
ICECAST_ADMIN_USER = os.getenv('ICECAST_ADMIN_USER', 'admin')
ICECAST_ADMIN_PASSWORD = os.getenv('ICECAST_ADMIN_PASSWORD', 'hackme')


async def _get(path: str, params: dict):
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(
            f'{ICECAST_ADMIN_URL}{path}',
            auth=(ICECAST_ADMIN_USER, ICECAST_ADMIN_PASSWORD),
            params=params,
        )
        return {'status': resp.status_code, 'body': resp.text}


async def list_listeners(mount: str):
    return await _get('/admin/listclients', {'mount': mount})


async def kick_listener(mount: str, listener_id: str):
    return await _get('/admin/killclient', {'mount': mount, 'id': listener_id})


async def move_listener(mount: str, destination: str, listener_id: str | None = None):
    params = {'mount': mount, 'destination': destination}
    if listener_id:
        params['id'] = listener_id
    return await _get('/admin/moveclients', params)


async def update_metadata(mount: str, song: str):
    return await _get('/admin/metadata', {'mount': mount, 'mode': 'updinfo', 'song': song})

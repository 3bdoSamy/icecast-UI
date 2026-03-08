from typing import Dict, List
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from services.security import get_current_user
from services.xml_editor import IcecastXmlEditor

router = APIRouter()
editor = IcecastXmlEditor()


SECTION_SCHEMA: Dict[str, List[str]] = {
    'limits': [
        'limits/clients', 'limits/sources', 'limits/queue-size', 'limits/client-timeout',
        'limits/header-timeout', 'limits/source-timeout', 'limits/burst-size', 'limits/burst-on-connect'
    ],
    'authentication': [
        'authentication/source-password', 'authentication/relay-user', 'authentication/relay-password',
        'authentication/admin-user', 'authentication/admin-password'
    ],
    'directory': ['directory/yp-url-timeout', 'directory/yp-url', 'directory/touch-freq'],
    'server_settings': ['hostname', 'location', 'admin', 'fileserve', 'charset', 'mount-default'],
    'listen_sockets': ['listen-socket/port', 'listen-socket/ssl', 'listen-socket/bind-address', 'listen-socket/shoutcast-mount'],
    'http_headers': ['http-headers/access-control-allow-origin', 'http-headers/cache-control'],
    'relays': [
        'master-server', 'master-server-port', 'master-update-interval', 'master-password',
        'relays/relay/server', 'relays/relay/port', 'relays/relay/mount', 'relays/relay/local-mount',
        'relays/relay/on-demand', 'relays/relay/relay-shoutcast-metadata', 'relays/relay/relays-on-demand'
    ],
    'mount_defaults': [
        'mount/default-type', 'mount/dump-file', 'mount/intro', 'mount/hidden',
        'mount/mp3-metadata-interval', 'mount/charset'
    ],
    'paths': [
        'paths/basedir', 'paths/logdir', 'paths/pidfile', 'paths/webroot', 'paths/adminroot',
        'paths/alias/source', 'paths/alias/destination', 'paths/ssl-certificate', 'paths/ssl-allowed-ciphers', 'paths/allow-ip', 'paths/deny-ip'
        'paths/alias/source', 'paths/alias/destination', 'paths/ssl-certificate'
    ],
    'logging': ['logging/accesslog', 'logging/errorlog', 'logging/playlistlog', 'logging/loglevel', 'logging/logsize', 'logging/logarchive'],
    'security': ['security/chroot', 'security/changeowner/user', 'security/changeowner/group'],
    'listener_auth': [
        'authentication/listener_auth/type', 'authentication/listener_auth/mount_add',
        'authentication/listener_auth/mount_remove', 'authentication/listener_auth/listener_add',
        'authentication/listener_auth/listener_remove', 'authentication/listener_auth/stream_auth'
    ]
}


class XmlUpdateRequest(BaseModel):
    xpath: str
    value: str


class BulkUpdateRequest(BaseModel):
    updates: List[XmlUpdateRequest]


@router.get('/raw')
def get_raw_config(_=Depends(get_current_user)):
    return {'xml': editor.read_xml()}


@router.get('/schema')
def get_schema(_=Depends(get_current_user)):
    return SECTION_SCHEMA


@router.post('/update')
def update_xml(payload: XmlUpdateRequest, _=Depends(get_current_user)):
    try:
        backup = editor.backup()
        editor.set_value(payload.xpath, payload.value)
        valid = editor.validate()
        if not valid['valid']:
            raise HTTPException(status_code=400, detail={'message': 'XML validation failed', 'validation': valid, 'backup': backup})
        return {'status': 'updated', 'backup': backup, 'validation': valid}
@router.get("/raw")
def get_raw_config(_=Depends(get_current_user)):
    return {"xml": editor.read_xml()}


@router.post("/update")
def update_xml(payload: XmlUpdateRequest, _=Depends(get_current_user)):
    try:
        editor.update_value(payload.xpath, payload.value)
        return {"status": "updated"}
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post('/bulk-update')
def bulk_update(payload: BulkUpdateRequest, _=Depends(get_current_user)):
    backup = editor.backup()
    for upd in payload.updates:
        editor.set_value(upd.xpath, upd.value)
    valid = editor.validate()
    if not valid['valid']:
        raise HTTPException(status_code=400, detail={'message': 'XML validation failed', 'validation': valid, 'backup': backup})
    return {'status': 'updated', 'backup': backup, 'validation': valid, 'updated_count': len(payload.updates)}


@router.post('/validate')
def validate_xml(_=Depends(get_current_user)):
    return editor.backup_and_validate()


@router.get('/limits')
def get_limits(_=Depends(get_current_user)):
    keys = ['clients','sources','queue-size','client-timeout','header-timeout','source-timeout','burst-size','burst-on-connect']
    xml = editor.load_tree()
    out = {}
    for k in keys:
        node = xml.xpath(f'/icecast/limits/{k}')
        out[k] = node[0].text if node else ''
    return out


class LimitsRequest(BaseModel):
    clients: int
    sources: int
    queue_size: int
    client_timeout: int
    header_timeout: int
    source_timeout: int
    burst_size: int
    burst_on_connect: int


@router.put('/limits')
def update_limits(payload: LimitsRequest, _=Depends(get_current_user)):
    backup = editor.backup()
    updates = [
        ('limits/clients', str(payload.clients)),
        ('limits/sources', str(payload.sources)),
        ('limits/queue-size', str(payload.queue_size)),
        ('limits/client-timeout', str(payload.client_timeout)),
        ('limits/header-timeout', str(payload.header_timeout)),
        ('limits/source-timeout', str(payload.source_timeout)),
        ('limits/burst-size', str(payload.burst_size)),
        ('limits/burst-on-connect', str(payload.burst_on_connect)),
    ]
    for xpath, value in updates:
        editor.set_value(xpath, value)
    valid = editor.validate()
    if not valid['valid']:
        raise HTTPException(status_code=400, detail={'message': 'XML validation failed', 'validation': valid, 'backup': backup})
    return {'status': 'updated', 'backup': backup, 'validation': valid}
@router.post("/validate")
def validate_xml(_=Depends(get_current_user)):
    return editor.validate()

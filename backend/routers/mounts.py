from typing import Optional
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from services.security import get_current_user
from services.mount_manager import list_mounts, kill_source
from services.xml_editor import IcecastXmlEditor
from services.admin_manager import update_metadata

router = APIRouter()
editor = IcecastXmlEditor()


class KillSourceRequest(BaseModel):
    mount: str


class MountConfigRequest(BaseModel):
    mount_name: str
    username: Optional[str] = None
    password: Optional[str] = None
    max_listeners: Optional[int] = None
    max_listener_duration: Optional[int] = None
    fallback_mount: Optional[str] = None
    fallback_override: Optional[int] = None
    fallback_when_full: Optional[int] = None
    public: Optional[int] = None
    stream_name: Optional[str] = None
    stream_description: Optional[str] = None
    stream_url: Optional[str] = None
    genre: Optional[str] = None
    bitrate: Optional[str] = None
    type: Optional[str] = None
    subtype: Optional[str] = None
    hidden: Optional[int] = None
    burst_size: Optional[int] = None
    mp3_metadata_interval: Optional[int] = None
    intro: Optional[str] = None
    dump_file: Optional[str] = None
    charset: Optional[str] = None


@router.get('')
async def mounts(_=Depends(get_current_user)):
    return await list_mounts()


@router.post('/kill-source')
async def kill(payload: KillSourceRequest, _=Depends(get_current_user)):
    return await kill_source(payload.mount)


@router.post('/upsert')
def upsert_mount(payload: MountConfigRequest, _=Depends(get_current_user)):
    backup = editor.backup()
    values = {
        'username': payload.username,
        'password': payload.password,
        'max-listeners': payload.max_listeners,
        'max-listener-duration': payload.max_listener_duration,
        'fallback-mount': payload.fallback_mount,
        'fallback-override': payload.fallback_override,
        'fallback-when-full': payload.fallback_when_full,
        'public': payload.public,
        'stream-name': payload.stream_name,
        'stream-description': payload.stream_description,
        'stream-url': payload.stream_url,
        'genre': payload.genre,
        'bitrate': payload.bitrate,
        'type': payload.type,
        'subtype': payload.subtype,
        'hidden': payload.hidden,
        'burst-size': payload.burst_size,
        'mp3-metadata-interval': payload.mp3_metadata_interval,
        'intro': payload.intro,
        'dump-file': payload.dump_file,
        'charset': payload.charset,
    }
    editor.upsert_mount(payload.mount_name, values)
    valid = editor.validate()
    return {'status': 'ok', 'backup': backup, 'validation': valid}


@router.delete('/{mount_name}')
def delete_mount(mount_name: str, _=Depends(get_current_user)):
    backup = editor.backup()
    editor.delete_mount(mount_name)
    valid = editor.validate()
    return {'status': 'deleted', 'backup': backup, 'validation': valid}


class MetadataRequest(BaseModel):
    song: str


@router.post('/{mount:path}/metadata')
async def metadata(mount: str, payload: MetadataRequest, _=Depends(get_current_user)):
    if not mount.startswith('/'):
        mount = '/' + mount
    return await update_metadata(mount, payload.song)

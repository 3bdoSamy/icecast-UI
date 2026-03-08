from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from services.security import get_current_user
from services.xml_editor import IcecastXmlEditor

router = APIRouter()
editor = IcecastXmlEditor()


class MasterRelayRequest(BaseModel):
    master_server: str
    master_server_port: int
    master_update_interval: int
    master_password: str
    relays_on_demand: int = 0


class SpecificRelayRequest(BaseModel):
    server: str
    port: int
    mount: str
    local_mount: str
    username: Optional[str] = None
    password: Optional[str] = None
    relay_shoutcast_metadata: int = 0
    on_demand: int = 0


def _validate_or_raise(backup: str):
    valid = editor.validate()
    if not valid['valid']:
        raise HTTPException(status_code=400, detail={'message': 'XML validation failed', 'backup': backup, 'validation': valid})
    return valid


@router.get('')
def get_relays(_=Depends(get_current_user)):
    return editor.get_relays()


@router.put('/master')
def set_master(payload: MasterRelayRequest, _=Depends(get_current_user)):
    backup = editor.backup()
    editor.set_master_relay({
        'master-server': payload.master_server,
        'master-server-port': payload.master_server_port,
        'master-update-interval': payload.master_update_interval,
        'master-password': payload.master_password,
        'relays-on-demand': payload.relays_on_demand,
    })
    return {'status': 'updated', 'backup': backup, 'validation': _validate_or_raise(backup)}


@router.post('')
def add_specific(payload: SpecificRelayRequest, _=Depends(get_current_user)):
    backup = editor.backup()
    editor.add_specific_relay({
        'server': payload.server,
        'port': payload.port,
        'mount': payload.mount,
        'local-mount': payload.local_mount,
        'username': payload.username,
        'password': payload.password,
        'relay-shoutcast-metadata': payload.relay_shoutcast_metadata,
        'on-demand': payload.on_demand,
    })
    return {'status': 'created', 'backup': backup, 'validation': _validate_or_raise(backup)}


@router.put('/{relay_id}')
def update_specific(relay_id: int, payload: SpecificRelayRequest, _=Depends(get_current_user)):
    backup = editor.backup()
    editor.update_specific_relay(relay_id, {
        'server': payload.server,
        'port': payload.port,
        'mount': payload.mount,
        'local-mount': payload.local_mount,
        'username': payload.username,
        'password': payload.password,
        'relay-shoutcast-metadata': payload.relay_shoutcast_metadata,
        'on-demand': payload.on_demand,
    })
    return {'status': 'updated', 'backup': backup, 'validation': _validate_or_raise(backup)}


@router.delete('/{relay_id}')
def delete_specific(relay_id: int, _=Depends(get_current_user)):
    backup = editor.backup()
    editor.delete_specific_relay(relay_id)
    return {'status': 'deleted', 'backup': backup, 'validation': _validate_or_raise(backup)}

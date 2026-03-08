from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from services.security import get_current_user
from services.xml_editor import IcecastXmlEditor

router = APIRouter()
editor = IcecastXmlEditor()


class SocketRequest(BaseModel):
    port: int
    bind_address: Optional[str] = None
    ssl: int = 0
    shoutcast_mount: Optional[str] = None


def _validate_or_raise(backup: str):
    valid = editor.validate()
    if not valid['valid']:
        raise HTTPException(status_code=400, detail={'message': 'XML validation failed', 'backup': backup, 'validation': valid})
    return valid


@router.get('')
def get_sockets(_=Depends(get_current_user)):
    return {'sockets': editor.list_sockets()}


@router.post('')
def create_socket(payload: SocketRequest, _=Depends(get_current_user)):
    backup = editor.backup()
    editor.add_socket({'port': payload.port, 'bind-address': payload.bind_address, 'ssl': payload.ssl, 'shoutcast-mount': payload.shoutcast_mount})
    return {'status': 'created', 'backup': backup, 'validation': _validate_or_raise(backup)}


@router.put('/{socket_id}')
def update_socket(socket_id: int, payload: SocketRequest, _=Depends(get_current_user)):
    backup = editor.backup()
    editor.update_socket(socket_id, {'port': payload.port, 'bind-address': payload.bind_address, 'ssl': payload.ssl, 'shoutcast-mount': payload.shoutcast_mount})
    return {'status': 'updated', 'backup': backup, 'validation': _validate_or_raise(backup)}


@router.delete('/{socket_id}')
def delete_socket(socket_id: int, _=Depends(get_current_user)):
    backup = editor.backup()
    editor.delete_socket(socket_id)
    return {'status': 'deleted', 'backup': backup, 'validation': _validate_or_raise(backup)}

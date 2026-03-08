from fastapi import APIRouter, Depends
from pydantic import BaseModel
from services.security import get_current_user
from services.listener_auth import add_or_update_user, delete_user, list_users, issue_stream_token, verify_stream_token

router = APIRouter()


class UserRequest(BaseModel):
    username: str
    password: str


class TokenRequest(BaseModel):
    mount: str
    username: str


@router.get('/htpasswd')
def users(_=Depends(get_current_user)):
    return {'users': list_users()}


@router.post('/htpasswd')
def upsert(payload: UserRequest, _=Depends(get_current_user)):
    add_or_update_user(payload.username, payload.password)
    return {'status': 'ok'}


@router.delete('/htpasswd/{username}')
def remove(username: str, _=Depends(get_current_user)):
    delete_user(username)
    return {'status': 'deleted'}


@router.post('/stream-token')
def stream_token(payload: TokenRequest, _=Depends(get_current_user)):
    return {'token': issue_stream_token(payload.mount, payload.username)}


@router.get('/validate-token')
def validate_token(token: str, mount: str):
    return {'valid': verify_stream_token(token, mount)}


@router.get('/stream-auth')
def stream_auth(token: str, mount: str):
    return {'authorized': verify_stream_token(token, mount)}

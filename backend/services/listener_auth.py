from pathlib import Path
from passlib.apache import HtpasswdFile
from jose import jwt
import os

HTPASSWD_PATH = Path('/data/control/listeners.htpasswd')
SECRET = os.getenv('JWT_SECRET', 'change-me')


def _file() -> HtpasswdFile:
    HTPASSWD_PATH.parent.mkdir(parents=True, exist_ok=True)
    if not HTPASSWD_PATH.exists():
        HTPASSWD_PATH.write_text('', encoding='utf-8')
    return HtpasswdFile(str(HTPASSWD_PATH), default_scheme='bcrypt')


def add_or_update_user(username: str, password: str):
    f = _file()
    f.set_password(username, password)
    f.save()


def delete_user(username: str):
    f = _file()
    f.delete(username)
    f.save()


def list_users():
    f = _file()
    return sorted(f.users())


def issue_stream_token(mount: str, username: str):
    return jwt.encode({'mount': mount, 'sub': username}, SECRET, algorithm='HS256')



def verify_stream_token(token: str, mount: str):
    try:
        payload = jwt.decode(token, SECRET, algorithms=['HS256'])
        return payload.get('mount') == mount
    except Exception:
        return False

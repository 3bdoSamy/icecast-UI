from fastapi import APIRouter, Depends
from services.security import get_current_user
from services.logs_manager import tail_log

router = APIRouter()


@router.get("/{log_name}")
def read_log(log_name: str, _=Depends(get_current_user)):
    return {"lines": tail_log(log_name)}

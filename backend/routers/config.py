from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from services.security import get_current_user
from services.xml_editor import IcecastXmlEditor

router = APIRouter()
editor = IcecastXmlEditor()


class XmlUpdateRequest(BaseModel):
    xpath: str
    value: str


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


@router.post("/validate")
def validate_xml(_=Depends(get_current_user)):
    return editor.validate()

from fastapi import APIRouter, Depends, HTTPException
from app.api.requests.handlers import list_requests, get_request
from app.api.requests.schema import RequestMode
from app.infra.db.dependencies import get_db

router = APIRouter(prefix="/requests", tags=["requests"])

@router.get("")
async def list_api(mode: RequestMode, db = Depends(get_db)):
    return await list_requests(db, mode)

@router.get("/{request_id}")
async def get_api(request_id: str, db = Depends(get_db)):
    record = await get_request(db, request_id)
    if not record:
        raise HTTPException(404)
    return record

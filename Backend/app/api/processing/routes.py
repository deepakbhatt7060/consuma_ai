from fastapi import APIRouter, Depends,Request
from app.api.processing.schemas import WorkPayload, AsyncPayload
from app.api.processing.handlers import handle_sync, handle_async
from app.infra.db.dependencies import get_db
from app.infra.workers.callback_scheduler import retry_failed_callbacks
from sqlalchemy.ext.asyncio import  AsyncSession

router = APIRouter(tags=["processing"])

#sync processing endpoint
@router.post("/sync")
async def sync_api(payload: WorkPayload,request: Request, db = Depends(get_db)):
    return await handle_sync(payload.model_dump(), db,  app=request.app)

#async processing endpoint
@router.post("/async")
async def async_api(payload: AsyncPayload,request: Request, db = Depends(get_db)):
    request_id = await handle_async(
        payload=payload.model_dump(),
        db=db,
        app=request.app
    )
    return {"id": request_id, "status": "Accepted"}

# @router.post("/retry-callbacks")
# async def retry_callbacks(db: AsyncSession = Depends(get_db)):
#     await retry_failed_callbacks(db)
#     return {"status": "ok"}
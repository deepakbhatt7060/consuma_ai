from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.infra.db.models import RequestDB

from app.utils.utils import epoch_time

# Repository for RequestDB model
class RequestRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, **kwargs):
        record = RequestDB(**kwargs)
        self.db.add(record)
        await self.db.commit()
        await self.db.refresh(record)
        return record

    async def get(self, request_id: str):
        result = await self.db.execute(select(RequestDB).where(RequestDB.id == request_id))
        return result.scalars().first()

    async def list(self, mode: str | None):
        stmt = select(RequestDB)
        if mode:
            stmt = stmt.where(RequestDB.mode == mode)
        stmt = stmt.order_by(RequestDB.started_at_ms.desc())
        result = await self.db.execute(stmt)
        return result.scalars().all()
    
    async def get_failed_callbacks(self, limit: int = 100):
        stmt = (
            select(RequestDB)
            .where(
                RequestDB.mode == "async",
                RequestDB.status == "callback_failed",
            )
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        return result.scalars().all()
    
    async def mark_callback_success(self, request_id: str, duration_ms: float):
        record = await self.db.get(RequestDB, request_id)
        record.status = "callback_completed"
        record.callback_completed_at_ms = epoch_time()
        record.callback_time_ms = duration_ms
        await self.db.commit()

    async def mark_callback_failure(self, request_id: str, error: str):
        record = await self.db.get(RequestDB, request_id)
        record.callback_attempts += 1
        record.last_error = error
        await self.db.commit()
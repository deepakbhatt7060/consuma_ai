import uuid
from sqlalchemy.orm import Session

from app.domain.work_service import perform_work
from app.repositories.request_repository import RequestRepository
import asyncio
from app.infra.workers.background_worker import background_worker
from app.utils.utils import epoch_time

async def handle_sync(payload: dict, db: Session, app):
    loop = asyncio.get_running_loop()
    started_at = epoch_time()

    result = await loop.run_in_executor(
        app.state.process_pool,
        perform_work,
        payload
    )

    completed_at = epoch_time()
    execution_time = completed_at - started_at

    repo = RequestRepository(db)
    await repo.create(
        id=str(uuid.uuid4()),
        mode="sync",
        status="completed",
        payload=payload,
        result=result,
        started_at_ms = started_at,
        completed_at_ms = completed_at,
        execution_time_ms=execution_time
    )

    return result

async def handle_async(payload: dict, db: Session, app):
    request_id = str(uuid.uuid4())

    repo = RequestRepository(db)
    await repo.create(
        id=request_id,
        mode="async",
        status="pending",
        payload=payload,
        started_at_ms=epoch_time()
    )

    # Schedule background processing and callback delivery
    asyncio.create_task(background_worker(app, request_id, payload))
    return request_id

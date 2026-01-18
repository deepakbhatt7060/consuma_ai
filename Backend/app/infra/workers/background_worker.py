from app.domain.work_service import perform_work
from app.infra.workers.callback import deliver_callback
from app.utils.utils import epoch_time
import asyncio

# Background worker for async processing and callback delivery
async def background_worker(app, request_id, payload):
    
    loop = asyncio.get_running_loop()
    process_pool = app.state.process_pool
    
    # Offloading CPU-bound work to process pool
    work_result = await loop.run_in_executor(process_pool, perform_work, payload)

    # Update DB and deliver callback
    async with app.state.session() as db:
        from sqlalchemy.future import select
        result = await db.execute(select(app.state.db).where(app.state.db.id == request_id))
        record = result.scalars().first()
        if record:
            record.result = work_result
            record.status = "work_done(callback_scheduled)"
            record.completed_at_ms = epoch_time()
            record.execution_time_ms = epoch_time() - record.started_at_ms
            await db.commit()
            await db.refresh(record)
            await deliver_callback(record,db,app.state.settings)


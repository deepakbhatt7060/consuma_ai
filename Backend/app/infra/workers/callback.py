import asyncio
import httpx
from app.config.settings import Settings
from app.utils.utils import epoch_time

# Deliver callback to the specified URL, with retries and update DB record accordingly
async def deliver_callback(record, db,settings):
    
    async with httpx.AsyncClient(timeout=settings.callback_timeout) as client:
        for attempt in range(settings.max_callback_retries):
            try:
                record.callback_attempts += 1

                start = epoch_time()

                resp = await client.post(
                    record.payload.get("callback_url"),
                    json={"id": record.id, "result": record.result}
                )

                resp.raise_for_status()

                duration_ms = epoch_time() - start

                record.callback_time_ms = duration_ms
                record.callback_completed_at_ms = epoch_time()
                record.status = "callback_completed"

                await db.commit()
                await db.refresh(record)
                return

            except Exception as e:
                record.last_error = str(e)
                await db.commit()
                await asyncio.sleep(2 ** attempt)

        record.status = "callback_failed"
        await db.commit()

import time
import httpx
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.request_repository import RequestRepository

CALLBACK_TIMEOUT = 5  # seconds
MAX_CALLBACK_ATTEMPTS = 5


async def retry_failed_callbacks(db: AsyncSession):
    repo = RequestRepository(db)

    failed_requests = await repo.get_failed_callbacks(limit=50)

    async with httpx.AsyncClient(timeout=CALLBACK_TIMEOUT) as client:
        for req in failed_requests:
            if req.callback_attempts >= MAX_CALLBACK_ATTEMPTS:
                continue  

            callback_url = req.payload.get("callback_url")
            if not callback_url:
                await repo.mark_callback_failure(
                    req.id, "Missing callback_url in payload"
                )
                continue

            start = time.time()

            try:
                response = await client.post(
                    callback_url,
                    json={
                        "request_id": req.id,
                        "result": req.result,
                        "status": req.status,
                    },
                )

                duration_ms = (time.time() - start) * 1000

                if response.status_code == 200:
                    await repo.mark_callback_success(req.id, duration_ms)
                else:
                    raise Exception(f"HTTP {response.status_code}")

            except Exception as exc:
                await repo.mark_callback_failure(req.id, str(exc))
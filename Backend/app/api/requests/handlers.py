from app.repositories.request_repository import RequestRepository

async def list_requests(db, mode: str):
    repo = RequestRepository(db)
    return await repo.list(mode)

async def get_request(db, request_id: str):
    repo = RequestRepository(db)
    return await repo.get(request_id)
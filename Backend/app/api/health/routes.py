from fastapi import APIRouter

router = APIRouter()

#liveliness probe
@router.get("/healthz", tags=["health"])
def healthz():
    return {"status": "ok"}
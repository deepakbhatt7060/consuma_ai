
from contextlib import asynccontextmanager
from fastapi import FastAPI
from concurrent.futures import ProcessPoolExecutor

from app.config.settings import Settings
from app.infra.db.session import create_async_engine_and_session
from app.infra.db.base import Base
from app.infra.db.models import RequestDB
from app.infra.workers.scheduler import should_run_scheduler, start_scheduler


# Lifespan context manager for FastAPI app
@asynccontextmanager
async def lifespan(app: FastAPI):
    settings=Settings()
    
    engine, asyncSession = create_async_engine_and_session()

    app.state.engine = engine
    app.state.session = asyncSession
    app.state.db = RequestDB
    app.state.settings=settings

    # Create a process pool for CPU-bound tasks with specified max workers
    process_pool = ProcessPoolExecutor(max_workers=settings.max_workers)
    app.state.process_pool = process_pool
    
    #create a scheduler for retrying failed callbacks
    if should_run_scheduler():
        start_scheduler(asyncSession)

    yield

    process_pool.shutdown(wait=True)
    await engine.dispose()

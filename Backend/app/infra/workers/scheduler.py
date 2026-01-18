from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy.ext.asyncio import async_sessionmaker
from app.infra.workers.callback_scheduler import retry_failed_callbacks

import os

scheduler = AsyncIOScheduler()

def should_run_scheduler() -> bool:
    return os.getenv("RUN_SCHEDULER", "false").lower() == "true"

def start_scheduler(session_factory: async_sessionmaker):
    scheduler.add_job(
        retry_failed_callbacks,
        CronTrigger(minute="*/10"),  # every 10 minutes
        args=[session_factory()],
        max_instances=1, 
        coalesce=True,
    )
    scheduler.start()
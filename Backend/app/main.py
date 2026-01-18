from fastapi import FastAPI
from app.lifecycle.lifespan import lifespan
from app.middlewares.cors_middleware import add_cors_middleware

from app.api.processing.routes import router as processing_router
from app.api.requests.routes import router as requests_router
from app.api.health.routes import router as health_router


app = FastAPI(lifespan=lifespan)
add_cors_middleware(app)

app.include_router(processing_router)
app.include_router(requests_router)
app.include_router(health_router)
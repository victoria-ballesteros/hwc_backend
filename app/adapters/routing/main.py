import logging
from typing import Any
from fastapi import FastAPI  # type: ignore

from app.adapters.routing.fastapi.config import init_app
from app.adapters.database.postgres.connection import SessionLocal
from app.adapters.routing.utils.context import db_context
from app.domain.core.feature_flags import FeatureFlags
from app.adapters.database.postgres.seeders.test_seeder import TestSeeder
from app.adapters.database.postgres.seeders.initialize_models import initialize_tables

app = FastAPI(title="HWC SERVER", version="1.0.0")
init_app(app)

@app.middleware("http")
async def db_connection_middleware(request, call_next) -> Any:
    request.state.db = SessionLocal()
    token = db_context.set(request.state.db)
    try:
        response = await call_next(request)
        return response
    except Exception:
        request.state.db.rollback()
        raise
    finally:
        db_context.reset(token)
        request.state.db.close()

@app.on_event("startup")
async def startup_events() -> None:
    logging.getLogger("uvicorn").info("Starting web server...")

    try:
        initialize_tables()

        if FeatureFlags().is_development:
            logging.getLogger("uvicorn").info("Running in development mode")
            TestSeeder(SessionLocal()).run()
        
        logging.getLogger("uvicorn").info("Initialization complete")
    finally:
        pass

@app.on_event("shutdown")
async def shutdown_event() -> None:
    logging.getLogger("uvicorn").info("Shutting down server")
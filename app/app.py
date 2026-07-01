from contextlib import asynccontextmanager
from fastapi import FastAPI

from app.api import router as incident_router
from app.database import create_tables
from cognee.modules.engine.operations.setup import setup


@asynccontextmanager
async def lifespan(app: FastAPI):
    await setup()
    await create_tables()
    yield


app = FastAPI(lifespan=lifespan)

app.include_router(incident_router)

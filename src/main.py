from fastapi import FastAPI
from fastapi_pagination import add_pagination
from contextlib import asynccontextmanager
from src.core.config import settings
from src.api.routes import router
from src.db import engine
from src.models import Base


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(
    title="Banking API",
    description="API assíncrona para gerenciamento de contas bancárias e operações financeiras",
    version="1.0.0",
    lifespan=lifespan
)
app.include_router(router)
add_pagination(app)

from fastapi import FastAPI
from fastapi_pagination import add_pagination
from src.core.config import settings
from src.api.routes import router

app = FastAPI(title=settings.APP_NAME)
app.include_router(router)
add_pagination(app)

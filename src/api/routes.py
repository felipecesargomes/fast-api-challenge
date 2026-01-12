from fastapi import APIRouter
from src.api.endpoints import auth, items

router = APIRouter()
router.include_router(auth.router, prefix="/auth", tags=["auth"])
router.include_router(items.router, prefix="/items", tags=["items"])

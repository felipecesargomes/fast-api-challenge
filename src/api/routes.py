from fastapi import APIRouter
from src.api.endpoints import auth, items, accounts, operations

router = APIRouter()
router.include_router(auth.router, prefix="/auth", tags=["auth"])
router.include_router(items.router, prefix="/items", tags=["items"])
router.include_router(accounts.router, prefix="/accounts", tags=["bank-accounts"])
router.include_router(operations.router, prefix="/operations", tags=["bank-operations"])

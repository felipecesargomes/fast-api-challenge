from pydantic import BaseModel
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi_pagination import Page, paginate
from src.db import get_db
from src.models import Item
from src.api.deps import validate_token

router = APIRouter()

class ItemCreate(BaseModel):
    name: str

class ItemOut(BaseModel):
    id: int
    name: str

@router.post("/", response_model=ItemOut, status_code=201, dependencies=[Depends(validate_token)])
async def create_item(data: ItemCreate, db: AsyncSession = Depends(get_db)):
    item = Item(name=data.name)
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return ItemOut(id=item.id, name=item.name)

@router.get("/", response_model=Page[ItemOut], dependencies=[Depends(validate_token)])
async def list_items(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Item).order_by(Item.id))
    items = [ItemOut(id=i.id, name=i.name) for i in result.scalars().all()]
    return paginate(items)

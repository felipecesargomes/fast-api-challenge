from pydantic import BaseModel
from fastapi import APIRouter
from src.core.security import create_access_token

router = APIRouter()

class LoginIn(BaseModel):
    username: str

class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"

@router.post("/login", response_model=TokenOut)
async def login(data: LoginIn):
    token = create_access_token(subject=data.username)
    return TokenOut(access_token=token)

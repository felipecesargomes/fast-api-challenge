from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.db import get_db
from src.models import BankAccount
from src.api.schemas import BankAccountCreate, BankAccountOut
from src.api.deps import validate_token

router = APIRouter()


@router.post("/", response_model=BankAccountOut, status_code=status.HTTP_201_CREATED, dependencies=[Depends(validate_token)])
async def create_bank_account(
    account_data: BankAccountCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Cria uma nova conta bancária.
    
    - **user_id**: ID do usuário (obrigatório)
    - **account_type**: Tipo da conta (checking ou savings)
    - **initial_balance**: Saldo inicial (padrão: 0.0)
    - **daily_limit**: Limite diário de saque (padrão: 1000.0)
    """
    result = await db.execute(
        select(BankAccount).where(
            BankAccount.user_id == account_data.user_id,
            BankAccount.account_type == account_data.account_type.value,
            BankAccount.is_active == True
        )
    )
    existing_account = result.scalar_one_or_none()
    
    if existing_account:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Usuário já possui uma conta {account_data.account_type.value} ativa"
        )
    
    new_account = BankAccount(
        user_id=account_data.user_id,
        balance=account_data.initial_balance,
        account_type=account_data.account_type.value,
        daily_limit=account_data.daily_limit,
        is_active=True
    )
    
    db.add(new_account)
    await db.commit()
    await db.refresh(new_account)
    
    return new_account


@router.get("/", response_model=list[BankAccountOut], dependencies=[Depends(validate_token)])
async def list_bank_accounts(
    user_id: int | None = None,
    skip: int = 0,
    limit: int = 50,
    db: AsyncSession = Depends(get_db)
):
    """
    Lista contas bancárias com filtros opcionais.
    
    - **user_id**: Filtrar por ID do usuário (opcional)
    - **skip**: Offset para paginação
    - **limit**: Número máximo de resultados
    """
    query = select(BankAccount).where(BankAccount.is_active == True)
    
    if user_id:
        query = query.where(BankAccount.user_id == user_id)
    
    query = query.offset(skip).limit(limit).order_by(BankAccount.created_at.desc())
    
    result = await db.execute(query)
    accounts = result.scalars().all()
    
    return accounts


@router.get("/{account_id}", response_model=BankAccountOut, dependencies=[Depends(validate_token)])
async def get_bank_account(
    account_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Busca uma conta bancária específica por ID.
    """
    result = await db.execute(
        select(BankAccount).where(BankAccount.id == account_id)
    )
    account = result.scalar_one_or_none()
    
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conta bancária não encontrada"
        )
    
    return account


@router.patch("/{account_id}/deactivate", dependencies=[Depends(validate_token)])
async def deactivate_account(
    account_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Desativa uma conta bancária (soft delete).
    """
    result = await db.execute(
        select(BankAccount).where(BankAccount.id == account_id)
    )
    account = result.scalar_one_or_none()
    
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conta bancária não encontrada"
        )
    
    if not account.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Conta já está desativada"
        )
    
    account.is_active = False
    await db.commit()
    
    return {"message": "Conta desativada com sucesso"}

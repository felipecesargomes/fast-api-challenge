from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from datetime import datetime, timedelta
from src.db import get_db
from src.models import BankAccount, Operation, OperationType
from src.api.schemas import OperationCreate, OperationOut, StatementOut
from src.api.deps import validate_token

router = APIRouter()


async def validate_and_get_account(account_id: int, db: AsyncSession) -> BankAccount:
    """Valida e retorna uma conta bancária ativa"""
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
            detail="Conta bancária está desativada"
        )
    
    return account


async def check_daily_withdrawal_limit(account: BankAccount, amount: float, db: AsyncSession):
    """Verifica se o saque está dentro do limite diário"""
    today = datetime.utcnow().date()
    today_start = datetime.combine(today, datetime.min.time())
    
    result = await db.execute(
        select(func.sum(Operation.amount)).where(
            Operation.account_id == account.id,
            Operation.operation_type == OperationType.WITHDRAWAL.value,
            Operation.timestamp >= today_start
        )
    )
    total_withdrawn_today = result.scalar() or 0.0
    
    if float(total_withdrawn_today) + amount > float(account.daily_limit):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Operação excede o limite diário de saque (R$ {account.daily_limit}). Já sacado hoje: R$ {total_withdrawn_today}"
        )


@router.post("/deposit", response_model=OperationOut, status_code=status.HTTP_201_CREATED, dependencies=[Depends(validate_token)])
async def deposit(
    operation: OperationCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Realiza um depósito na conta bancária.
    
    - **account_id**: ID da conta
    - **amount**: Valor do depósito (deve ser positivo)
    - **description**: Descrição opcional da operação
    """
    if operation.operation_type != OperationType.DEPOSIT:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tipo de operação deve ser 'deposit'"
        )
    
    account = await validate_and_get_account(operation.account_id, db)
    
    new_balance = float(account.balance) + operation.amount
    account.balance = new_balance
    
    # Cria o registro da operação
    new_operation = Operation(
        account_id=account.id,
        operation_type=OperationType.DEPOSIT.value,
        amount=operation.amount,
        balance_after=new_balance,
        description=operation.description or "Depósito"
    )
    
    db.add(new_operation)
    await db.commit()
    await db.refresh(new_operation)
    
    return new_operation


@router.post("/withdraw", response_model=OperationOut, status_code=status.HTTP_201_CREATED, dependencies=[Depends(validate_token)])
async def withdraw(
    operation: OperationCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Realiza um saque da conta bancária.
    
    Validações:
    - Saldo suficiente
    - Dentro do limite diário
    - Valor positivo
    
    - **account_id**: ID da conta
    - **amount**: Valor do saque
    - **description**: Descrição opcional da operação
    """
    if operation.operation_type != OperationType.WITHDRAWAL:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tipo de operação deve ser 'withdrawal'"
        )
    
    account = await validate_and_get_account(operation.account_id, db)
    
    if float(account.balance) < operation.amount:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Saldo insuficiente. Saldo atual: R$ {account.balance}"
        )
    
    await check_daily_withdrawal_limit(account, operation.amount, db)
    
    new_balance = float(account.balance) - operation.amount
    account.balance = new_balance
    
    new_operation = Operation(
        account_id=account.id,
        operation_type=OperationType.WITHDRAWAL.value,
        amount=operation.amount,
        balance_after=new_balance,
        description=operation.description or "Saque"
    )
    
    db.add(new_operation)
    await db.commit()
    await db.refresh(new_operation)
    
    return new_operation


@router.get("/{account_id}/statement", response_model=StatementOut, dependencies=[Depends(validate_token)])
async def get_statement(
    account_id: int,
    limit: int = 50,
    offset: int = 0,
    db: AsyncSession = Depends(get_db)
):
    """
    Retorna o extrato da conta bancária com paginação.
    
    - **account_id**: ID da conta
    - **limit**: Número de operações por página
    - **offset**: Offset para paginação
    """
    account = await validate_and_get_account(account_id, db)
    
    result = await db.execute(
        select(Operation)
        .where(Operation.account_id == account_id)
        .order_by(Operation.timestamp.desc())
        .offset(offset)
        .limit(limit)
    )
    operations = result.scalars().all()
    
    count_result = await db.execute(
        select(func.count(Operation.id)).where(Operation.account_id == account_id)
    )
    total_operations = count_result.scalar()
    
    return StatementOut(
        account=account,
        operations=operations,
        total_operations=total_operations
    )


@router.get("/", response_model=list[OperationOut], dependencies=[Depends(validate_token)])
async def list_operations(
    account_id: int | None = None,
    operation_type: OperationType | None = None,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """
    Lista operações com filtros opcionais.
    
    - **account_id**: Filtrar por conta específica
    - **operation_type**: Filtrar por tipo de operação (deposit/withdrawal)
    - **skip**: Offset para paginação
    - **limit**: Número máximo de resultados
    """
    query = select(Operation)
    
    if account_id:
        query = query.where(Operation.account_id == account_id)
    
    if operation_type:
        query = query.where(Operation.operation_type == operation_type.value)
    
    query = query.order_by(Operation.timestamp.desc()).offset(skip).limit(limit)
    
    result = await db.execute(query)
    operations = result.scalars().all()
    
    return operations

from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from enum import Enum


class AccountType(str, Enum):
    """Tipos de conta bancária"""
    CHECKING = "checking"
    SAVINGS = "savings"


class OperationType(str, Enum):
    """Tipos de operação bancária"""
    DEPOSIT = "deposit"
    WITHDRAWAL = "withdrawal"


class BankAccountCreate(BaseModel):
    """Schema para criação de conta bancária"""
    user_id: int = Field(..., gt=0, description="ID do usuário")
    account_type: AccountType = Field(default=AccountType.CHECKING, description="Tipo da conta")
    initial_balance: float = Field(default=0.0, ge=0, description="Saldo inicial")
    daily_limit: float = Field(default=1000.0, gt=0, le=10000, description="Limite diário de saque")

    @field_validator('initial_balance', 'daily_limit')
    @classmethod
    def validate_amount(cls, v):
        if v < 0:
            raise ValueError('Valor não pode ser negativo')
        return round(v, 2)


class BankAccountOut(BaseModel):
    """Schema de saída para conta bancária"""
    id: int
    user_id: int
    balance: float
    account_type: str
    daily_limit: float
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class OperationCreate(BaseModel):
    """Schema para criar uma operação bancária"""
    account_id: int = Field(..., gt=0, description="ID da conta")
    operation_type: OperationType = Field(..., description="Tipo de operação")
    amount: float = Field(..., gt=0, description="Valor da operação")
    description: str | None = Field(None, max_length=255, description="Descrição opcional")

    @field_validator('amount')
    @classmethod
    def validate_amount(cls, v):
        if v <= 0:
            raise ValueError('Valor deve ser maior que zero')
        if v > 1000000:
            raise ValueError('Valor excede o limite máximo permitido')
        return round(v, 2)


class OperationOut(BaseModel):
    """Schema de saída para operação"""
    id: int
    account_id: int
    operation_type: str
    amount: float
    balance_after: float
    description: str | None
    timestamp: datetime

    model_config = {"from_attributes": True}


class StatementQuery(BaseModel):
    """Parâmetros para consulta de extrato"""
    limit: int = Field(default=50, gt=0, le=500, description="Número de registros")
    offset: int = Field(default=0, ge=0, description="Offset para paginação")


class StatementOut(BaseModel):
    """Schema de saída do extrato"""
    account: BankAccountOut
    operations: list[OperationOut]
    total_operations: int

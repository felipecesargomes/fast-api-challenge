from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, Numeric, DateTime, ForeignKey, Enum as SQLEnum
from datetime import datetime
from enum import Enum
from typing import List

class Base(DeclarativeBase):
    pass

class Item(Base):
    __tablename__ = "items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)


class AccountType(str, Enum):
    """Tipos de conta bancária"""
    CHECKING = "checking"
    SAVINGS = "savings"


class OperationType(str, Enum):
    """Tipos de operação bancária"""
    DEPOSIT = "deposit"
    WITHDRAWAL = "withdrawal"
    TRANSFER = "transfer"


class BankAccount(Base):
    """Modelo de Conta Bancária"""
    __tablename__ = "bank_accounts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    balance: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False, default=0.0)
    account_type: Mapped[str] = mapped_column(
        SQLEnum(AccountType, name="account_type_enum", create_type=True),
        nullable=False,
        default=AccountType.CHECKING.value
    )
    daily_limit: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False, default=1000.0)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    
    operations: Mapped[List["Operation"]] = relationship("Operation", back_populates="account", lazy="selectin")


class Operation(Base):
    """Modelo de Operação Bancária"""
    __tablename__ = "operations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    account_id: Mapped[int] = mapped_column(Integer, ForeignKey("bank_accounts.id"), nullable=False, index=True)
    operation_type: Mapped[str] = mapped_column(
        SQLEnum(OperationType, name="operation_type_enum", create_type=True),
        nullable=False
    )
    amount: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    balance_after: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    description: Mapped[str] = mapped_column(String(255), nullable=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    account: Mapped["BankAccount"] = relationship("BankAccount", back_populates="operations")

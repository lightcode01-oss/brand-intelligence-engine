import uuid
from datetime import datetime, timezone, timedelta
from typing import Optional, Sequence
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User, CreditTransaction
from app.exceptions.errors import DomainException

class CreditService:
    """Manages user token credit balances, debit checkpoints, and atomic refunds."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        
    async def get_balance(self, user_id: uuid.UUID) -> float:
        """Calculates active credit balance summing credits/refunds and subtracting debits."""
        now = datetime.now(timezone.utc)
        
        # 1. Sum credits/refunds that are not expired
        credit_stmt = select(func.sum(CreditTransaction.amount)).where(
            CreditTransaction.user_id == user_id,
            CreditTransaction.type.in_(["CREDIT", "REFUND"]),
            (CreditTransaction.expires_at == None) | (CreditTransaction.expires_at > now),
            CreditTransaction.deleted_at == None
        )
        total_credit = (await self.db.execute(credit_stmt)).scalar() or 0.0
        
        # 2. Sum debits
        debit_stmt = select(func.sum(CreditTransaction.amount)).where(
            CreditTransaction.user_id == user_id,
            CreditTransaction.type == "DEBIT",
            CreditTransaction.deleted_at == None
        )
        total_debit = (await self.db.execute(debit_stmt)).scalar() or 0.0
        
        return max(0.0, total_credit - total_debit)
        
    async def credit_user(self, user_id: uuid.UUID, amount: float, expiration_days: Optional[int] = None) -> CreditTransaction:
        """Grants credits to a user account, with optional expiration rules."""
        if amount <= 0:
            raise DomainException("Credit amount must be greater than zero.")
            
        expires_at = None
        if expiration_days:
            expires_at = datetime.now(timezone.utc) + timedelta(days=expiration_days)
            
        txn = CreditTransaction(
            user_id=user_id,
            amount=amount,
            type="CREDIT",
            expires_at=expires_at
        )
        self.db.add(txn)
        await self.db.flush()
        return txn
        
    async def debit_credits(self, user_id: uuid.UUID, amount: float) -> bool:
        """Atomically debits credits from a user's account, preventing race conditions."""
        if amount <= 0:
            raise DomainException("Debit amount must be greater than zero.")
            
        # Lock user record inside database transaction (pessimistic locking)
        stmt = select(User).where(User.id == user_id, User.deleted_at == None).with_for_update()
        user = (await self.db.execute(stmt)).scalar()
        if not user:
            raise DomainException("User account not found.")
            
        # Check current balance
        balance = await self.get_balance(user_id)
        if balance < amount:
            raise DomainException("Insufficient credit balance to perform this operation.")
            
        # Write debit transaction log
        txn = CreditTransaction(
            user_id=user_id,
            amount=amount,
            type="DEBIT"
        )
        self.db.add(txn)
        await self.db.flush()
        return True
        
    async def refund_transaction(self, user_id: uuid.UUID, debit_txn_id: uuid.UUID) -> CreditTransaction:
        """Refunds a previously executed debit transaction back to the user."""
        stmt = select(CreditTransaction).where(
            CreditTransaction.id == debit_txn_id,
            CreditTransaction.user_id == user_id,
            CreditTransaction.type == "DEBIT",
            CreditTransaction.deleted_at == None
        )
        debit_txn = (await self.db.execute(stmt)).scalar()
        if not debit_txn:
            raise DomainException("Target debit transaction not found.")
            
        # Write refund log
        refund_txn = CreditTransaction(
            user_id=user_id,
            amount=debit_txn.amount,
            type="REFUND"
        )
        self.db.add(refund_txn)
        await self.db.flush()
        return refund_txn

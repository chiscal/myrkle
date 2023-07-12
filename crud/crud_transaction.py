from typing import List

from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from .base import CRUDBase
from models.transaction import Transaction
from schemas.transaction import Transaction as TransactionCreate


class CRUDTransaction(CRUDBase[Transaction, TransactionCreate, TransactionCreate]):
    def create_with_owner(
        self, db: Session, *, obj_in: TransactionCreate, owner_id: int
    ) -> Transaction:
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = self.model(**obj_in_data, owner_id=owner_id)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_multi_by_user(
        self, db: Session, *, user_id: int, skip: int = 0, limit: int = 100
    ) -> List[Transaction]:
        return (
            db.query(self.model)
            .filter(Transaction.user_id == user_id)
            .offset(skip)
            .limit(limit)
            .all()
        )


transaction = CRUDTransaction(Transaction)

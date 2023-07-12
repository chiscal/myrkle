from typing import Optional

from pydantic import BaseModel


class Transaction(BaseModel):
    id: Optional[int] = None
    transaction_id: str
    network: str
    currency: str
    amount: float
    transaction_type: str
    receipient: Optional[str] = None

    class Config:
        orm_mode = True

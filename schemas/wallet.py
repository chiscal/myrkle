from typing import Optional

from pydantic import BaseModel


class Wallet(BaseModel):
    id: Optional[int] = None
    address: str
    balance: str
    user_id: int

    class Config:
        orm_mode = True

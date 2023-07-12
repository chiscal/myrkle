from typing import Optional
from pydantic import BaseModel

from .user import UserInDBBase


class PairToken(BaseModel):
    key: str
    status: str
    expiry: int

    class Config:
        orm_mode = True


class Pair(BaseModel):
    first_person: UserInDBBase
    second_person: UserInDBBase
    token: Optional[PairToken]

    class Config:
        orm_mode = True

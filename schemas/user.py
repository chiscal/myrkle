from typing import Optional

from pydantic import BaseModel

from .wallet import Wallet


# Shared properties
class UserBase(BaseModel):
    browser_id: str = None
    is_active: Optional[bool] = True
    is_superuser: bool = False
    wallets: list[Wallet] = []


# Properties to receive via API on creation
class UserCreate(UserBase):
    browser_id: str
    password: str


# Properties to receive via API on update
class UserUpdate(UserBase):
    password: Optional[str] = None


class UserInDBBase(UserBase):
    id: Optional[int] = None

    class Config:
        orm_mode = True


# Additional properties to return via API
class User(UserInDBBase):
    pass


# Additional properties stored in DB
class UserInDB(UserInDBBase):
    hashed_password: str

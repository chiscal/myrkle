from typing import Optional

from pydantic import BaseModel


class CancelOffer(BaseModel):
    sender_addr: str
    offer_seq: int
    fee: str



class CreateOrderBookLiquidity(BaseModel):
    sender_addr: str
    buy: str
    sell: str
    expiry_date: int = None
    fee: str = None
    buy_type: str = None
    sell_type: str = None
    buy_issuer: str = None
    sell_issuer: str = None


class GetAccountOrderBookLiquidity(BaseModel):
    wallet_addr: str
    limit: int = None


class OrderBookSwap(BaseModel):
    sender_addr: str
    buy: str
    sell: str
    swap_all: bool = False
    fee: str = None
    buy_type: str = None
    sell_type: str = None
    buy_issuer: str = None
    sell_issuer: str = None


class SortBestOffer(BaseModel):
    buy: str
    sell: str
    best_buy: bool = False
    best_sell: bool = False
    limit: int = None
    buy_issuer: str = None
    sell_issuer: str = None
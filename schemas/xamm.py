# from typing import Optional, Str

from pydantic import BaseModel


class CancelOffer(BaseModel):
    sender_addr: str
    offer_seq: int
    fee: str


class CreateOrderBookLiquidity(BaseModel):
    sender_addr: str
    buy: float
    sell: float
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
    buy: float
    sell: float
    tf_sell: bool = False
    tf_fill_or_kill: bool = False
    tf_immediate_or_cancel: bool = False
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


class XAMMWallet(BaseModel):
    wallet_addr: str
    tf_sell: bool = False
    tf_fill_or_kill: bool = False
    tf_immediate_or_cancel: bool = False

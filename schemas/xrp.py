from typing import Union
from decimal import Decimal
from pydantic import BaseModel


class SendXRP(BaseModel):
    sender_address: str
    receiver_address: str
    amount: Union[float, int, Decimal]
    destination_tag: int = None
    source_tag: int = None
    fee: int = None


class SendToken(BaseModel):
    sender_address: str
    receiver_address: str
    receiver_addr: str
    token: str
    amount: Union[float, int, Decimal]
    issuer: str
    is_lp_token: bool = False
    destination_tag: int = None
    source_tag: int = None
    fee: int = None


class SendNFT(BaseModel):
    sender_addr: str
    nftoken_id: str
    receiver: str
    fee: Union[float, int, Decimal] = None

class CreateToken(BaseModel):
    issuer_addr: str
    manager_addr: str
    token_name: str
    total_supply: str
    fee: Union[float, int, Decimal] = None

class BurnToken(BaseModel):
    sender_addr: str
    token: str
    issuer: str
    amount: float
    fee: Union[float, int, Decimal] = None

class MintNFT(BaseModel):
    issuer_addr: str
    taxon: int
    is_transferable: bool
    only_xrp: bool
    issuer_burn: bool
    transfer_fee: float = None
    uri: str = None
    fee: Union[float, int, Decimal] = None

class BurnNFT(BaseModel):
    sender_addr: str
    nftoken_id: str
    holder: str = None
    fee: Union[float, int, Decimal] = None


class CreateXRPCheck(BaseModel):
    sender_addr: str
    receiver_addr: str
    amount: Union[int, float, Decimal]
    expiry_date: int = None
    fee: Union[float, int, Decimal] = None


class AccountChecks(BaseModel):
    wallet_addr: str
    limit: int = None


class CashXRPCheck(BaseModel):
    sender_addr: str
    check_id: str
    amount: Union[float, int, Decimal]
    fee: Union[float, int, Decimal] = None


class CancelCheck(BaseModel):
    sender_addr: str
    check_id: str
    fee: Union[float, int, Decimal] = None


class CreateTokenCheck(BaseModel):
    sender_addr: str
    check_id: str
    fee: Union[float, int, Decimal] = None


class CashTokenCheck(BaseModel):
    sender_addr: str
    check_id: str
    token: str
    amount: str
    issuer: str
    fee: Union[float, int, Decimal] = None


class CreateXRPEscrow(BaseModel):
    sender_addr: str
    amount: Union[float, int, Decimal]
    receiver_addr: str
    condition: str
    claim_date: str
    expiry_date: str
    fee: Union[float, int, Decimal] = None


class ScheduleXRP(BaseModel):
    sender_addr: str
    amount: int| Decimal| float
    receiver_addr: str
    claim_date: int
    expiry_date: int
    fee: Union[float, int, Decimal] = None


class AccountXRPEscrows(BaseModel):
    wallet_addr: str
    limit: int


class r_seq_dict(BaseModel):
    prev_txn_id: str


class r_sequence(BaseModel):
    prev_txn_id: str


class CancelXRPEscrow(BaseModel):
    sender_addr: str
    escrow_creator: str
    prev_txn_id: str
    fee: Union[float, int, Decimal] = None


class finish_xrp_escrow(BaseModel):
    sender_addr: str
    escrow_creator: str
    prev_txn_id: str
    condition: str
    fulfillment: str
    fee: Union[float, int, Decimal] = None


class CreateOffer(BaseModel):
    sender_addr: str
    pay: float
    receive: float
    pay_type: str
    receive_type: str
    receive_issuer: str = None
    pay_issuer: str = None
    expiry_date: int
    fee: Union[float, int, Decimal] = None


class AccountOffers(BaseModel):
    wallet_addr: str
    limit: int


class CancelOffer(BaseModel):
    sender_addr: str
    offer_seq: int
    fee: Union[float, int, Decimal] = None


class AllOffers(BaseModel):
    pay: float
    receive: float
    limit: int

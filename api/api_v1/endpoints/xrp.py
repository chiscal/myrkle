from typing import Any, Dict

from fastapi import APIRouter, Depends

from api import deps

from sqlalchemy.orm import Session

from blockchain.xrp_client import (
    XRPWalletClient, XRPAssetClient,
    XRPObjectClient
)

from schemas import xrp, transaction as transaction_schema

import crud
import models


router = APIRouter()


@router.get("/get_balance/{wallet_address}", response_model=Any)
def get_balance(
    wallet_address: str,
    current_user: models.User = Depends(deps.get_current_user), 
    ) -> Dict:
    client = XRPWalletClient()
    balance = client.get_balance(wallet_address)
    return balance

@router.get("/get_tokens/{wallet_address}", response_model=Dict)
def get_wallet_tokens(
    wallet_address: str,
    current_user: models.User = Depends(deps.get_current_user),
    ) -> Dict:
    client = XRPWalletClient()
    tokens = client.get_tokens(wallet_address)
    return tokens

@router.get("/get_nfts/{wallet_address}", response_model=Dict)
def get_wallet_nfts(
    wallet_address: str,
    current_user: models.User = Depends(deps.get_current_user),
    ) -> Dict:
    client = XRPWalletClient()
    nfts = client.get_tokens(wallet_address)
    return nfts

@router.get("/get_transactions/{wallet_address}", response_model=Dict)
def get_wallet_transactions(
    wallet_address: str,
    current_user: models.User = Depends(deps.get_current_user), 
    ) -> Dict:
    client = XRPWalletClient()
    transactions = client.get_transactions(wallet_address)
    return transactions

@router.get("/get_token_transactions/{wallet_address}", response_model=Dict)
def get_token_transactions(
    wallet_address: str,
    current_user: models.User = Depends(deps.get_current_user),
    ) -> Dict:
    client = XRPWalletClient()
    token_transactions = client.get_token_transactions(wallet_address)
    return token_transactions   

@router.post("/send_xrp/", response_model=transaction_schema.Transaction)
def send_xrp(
    *,
    db: Session = Depends(deps.get_db),
    transaction: xrp.SendXRP,
    current_user: models.User = Depends(deps.get_current_user),
    ) -> Any:

    client = XRPWalletClient()
    send = client.send_xrp(
        sender_address=transaction.sender_address,
        receiver_address=transaction.receiver_address,
        amount=transaction.amount,
        destination_tag=transaction.destination_tag,
        source_tag=transaction.source_tag,
        fee=transaction.fee
    )
    record = transaction_schema.Transaction(
        user_id=current_user.id,
        transaction_id=send[""],
        network="xrp",
        currency=transaction.token,
        amount=transaction.amount,
        transaction_type="send_token",
        receipient=transaction.receiver_addr
    )

    entry = crud.transaction.create(db=db, obj_in=record)

    return entry

@router.post("/send_token/", response_model=transaction_schema.Transaction)
def send_token(
    *,
    db: Session = Depends(deps.get_db),
    transaction: xrp.SendToken,
    current_user: models.User = Depends(deps.get_current_user),
    ) -> Any:

    client = XRPWalletClient()
    send = client.send_token(
        sender_addr=transaction.sender_address,
        receiver_addr=transaction.receiver_addr,
        token=transaction.token,
        amount=transaction.amount,
        issuer=transaction.issuer,
        is_lp_token=transaction.is_lp_token,
        destination_tag=transaction.destination_tag,
        source_tag=transaction.source_tag,
        fee=transaction.fee
    )
    record = transaction_schema.Transaction(
        user_id=current_user.id,
        transaction_id=send[""],
        network="xrp",
        currency=transaction.token,
        amount=transaction.amount,
        transaction_type="send_token",
        receipient=transaction.receiver_addr
    )

    entry = crud.transaction.create(db=db, obj_in=record)

    return entry

@router.post("/create_token/", response_model=Dict)
def create_token(
    create_token: xrp.CreateToken,
    current_user: models.User = Depends(deps.get_current_user),
    ) -> Dict:
    client = XRPAssetClient()
    token = client.create_token(
        issuer_addr=create_token.issuer_addr,
        manager_addr=create_token.manager_addr,
        token_name=create_token.token_name,
        total_supply=create_token.total_supply,
        fee=create_token.fee
    )
    return token

@router.post("/burn_token/", response_model=Dict)
def burn_token(
    burn: xrp.BurnToken,
    current_user: models.User = Depends(deps.get_current_user),
    ) -> Dict:
    client = XRPAssetClient()
    burn = client.burn_token(
        sender_addr=burn.sender_addr,
        token=burn.token,
        issuer=burn.issuer,
        amount=burn.amount,
        fee=burn.fee
    )
    return burn

@router.post("/mint_nft/", response_model=Dict)
def mint_nft(
    nft: xrp.MintNFT,
    current_user: models.User = Depends(deps.get_current_user), 
    ) -> Dict:
    client = XRPAssetClient()
    mint = client.mint_nft(
        issuer_addr=nft.issuer_addr,
        taxon=nft.taxon,
        is_transferable=nft.is_transferable,
        only_xrp=nft.only_xrp,
        issuer_burn=nft.issuer_burn,
        transfer_fee=nft.transfer_fee,
        uri=nft.uri,
        fee=nft.fee
    )
    return mint

@router.post("/burn_nft/", response_model=Dict)
def burn_nft(
    nft: xrp.BurnNFT,
    current_user: models.User = Depends(deps.get_current_user),
    ) -> Dict:
    client = XRPAssetClient()
    burn = client.burn_nft(
        sender_addr=nft.sender_addr,
        nftoken_id=nft.nftoken_id,
        holder=nft.holder,
        fee=nft.fee
    )
    return burn

@router.post("/create_xrp_check/", response_model=Dict)
def create_xrp_check(
    check: xrp.CreateXRPCheck,
    current_user: models.User = Depends(deps.get_current_user), 
    ) -> Dict:
    client = XRPObjectClient()
    xrp_check = client.create_xrp_check(
        sender_addr=check.sender_addr,
        receiver_addr=check.receiver_addr,
        amount=check.amount,
        expiry_date=check.expiry_date,
        fee=check.fee
    )
    return xrp_check

@router.get("/account_checks/", response_model=Dict)
def get_account_checks(
    wallet_address: str,
    limit: int = None,
    current_user: models.User = Depends(deps.get_current_user),
    ) -> Dict:
    client = XRPObjectClient()
    account_checks = client.account_checks(
        wallet_addr=wallet_address,
        limit=limit
    )
    return account_checks

@router.get("/account_escrow/", response_model=Dict)
def get_account_escrows(
    wallet_address: str,
    limit: int = None,
    current_user: models.User = Depends(deps.get_current_user),
    ) -> Dict:
    client = XRPObjectClient()
    account_escrows = client.account_xrp_escrows(
        wallet_addr=wallet_address,
        limit=limit
    )
    return account_escrows

@router.post("/create_offer/", response_model=Dict)
def create_offer(
    offer: xrp.CreateOffer,
    current_user: models.User = Depends(deps.get_current_user),
    ) -> Dict:
    client = XRPObjectClient()
    offer = client.create_offer(
        sender_addr=offer.sender_addr,
        pay=offer.pay,
        receive=offer.receive,
        expiry_date=offer.expiry_date,
        fee=offer.fee
    )
    return offer

@router.get("/account_offers/", response_model=Dict)
def account_offers(
    wallet_addr: str,
    limit: int,
    current_user: models.User = Depends(deps.get_current_user), 
    ) -> Dict:
    client = XRPObjectClient()
    offers = client.account_offers(
        wallet_addr=wallet_addr,
        limit=limit
    )
    return offers

@router.post("/cancel_offer/", response_model=Dict)
def cancel_offer(
    cancel_offer: xrp.CancelOffer,
    current_user: models.User = Depends(deps.get_current_user),
    ) -> Dict:
    client = XRPObjectClient()
    cancel = client.cancel_offer(
        sender_addr=cancel_offer.sender_addr,
        offer_seq=cancel_offer.offer_seq,
        fee=cancel_offer.fee
    )
    return cancel

@router.get("/all_offers/", response_model=Dict)
def all_offers(
    pay: float,
    receive: float,
    limit: int,
    current_user: models.User = Depends(deps.get_current_user),
    ) -> list:
    client = XRPObjectClient()
    offers = client.all_offers(
        pay=pay,
        receive=receive,
        limit=limit
    )
    return offers

from typing import Any, Dict, List

from fastapi import APIRouter, Depends, HTTPException

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
    
    ) -> Dict:
    client = XRPWalletClient()
    balance = client.get_balance(wallet_address)
    return balance

@router.get("/get_tokens/{wallet_address}", response_model=List)
def get_wallet_tokens(
    wallet_address: str,
    ) -> List:
    client = XRPWalletClient()
    try:
        tokens = client.get_tokens(wallet_address)
    except Exception as exception:
        raise HTTPException(status_code=400, detail=str(exception))
    return tokens

@router.get("/get_nfts/{wallet_address}", response_model=List)
def get_wallet_nfts(
    wallet_address: str,
    
    ) -> List:
    client = XRPWalletClient()
    try:
        nfts = client.get_tokens(wallet_address)
    except Exception as exception:
        raise HTTPException(status_code=400, detail=str(exception))
    return nfts

@router.get("/get-transactions/{wallet_address}", response_model=Dict)
def get_wallet_transactions(
    wallet_address: str,
    
    ) -> Dict:
    client = XRPWalletClient()
    try:
        transactions = client.get_transactions(wallet_address)
    except Exception as exception:
        raise HTTPException(status_code=400, detail=str(exception))
    return transactions

@router.get("/get-token-transactions/{wallet_address}", response_model=Dict)
def get_token_transactions(
    wallet_address: str,
    
    ) -> Dict:
    client = XRPWalletClient()
    try:
        token_transactions = client.get_token_transactions(wallet_address)
    except Exception as exception:
        raise HTTPException(status_code=400, detail=str(exception))
    return token_transactions  

@router.get("/get-token-transactions/{wallet_address}", response_model=Dict)
def get_token_transactions(
    wallet_address: str,
    
    ) -> Dict:
    client = XRPWalletClient()
    try:
        token_transactions = client.get_token_transactions(wallet_address)
    except Exception as exception:
        raise HTTPException(status_code=400, detail=str(exception))
    return token_transactions 

@router.post("/send-xrp/", response_model=transaction_schema.Transaction)
def send_xrp(
    *,
    db: Session = Depends(deps.get_db),
    transaction: xrp.SendXRP,
    
    ) -> Any:

    client = XRPWalletClient()
    try:
        send = client.send_xrp(
        sender_addr=transaction.sender_address,
        receiver_addr=transaction.receiver_address,
        amount=transaction.amount,
        destination_tag=transaction.destination_tag,
        source_tag=transaction.source_tag,
        fee=transaction.fee
    )
    except Exception as exception:
        raise HTTPException(status_code=400, detail=str(exception))
    # record = transaction_schema.Transaction(
    #     user_id=
    #     transaction_id=send[""],
    #     network="xrp",
    #     currency=transaction.token,
    #     amount=transaction.amount,
    #     transaction_type="send_token",
    #     receipient=transaction.receiver_addr
    # )

    # entry = crud.transaction.create(db=db, obj_in=record)

    return send

@router.post("/send-token/", response_model=transaction_schema.Transaction)
def send_token(
    *,
    db: Session = Depends(deps.get_db),
    transaction: xrp.SendToken,
    
    ) -> Any:

    client = XRPWalletClient()
    try:
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
    except Exception as exception:
        raise HTTPException(status_code=400, detail=str(exception))
    # record = transaction_schema.Transaction(
    #     user_id=
    #     transaction_id=send[""],
    #     network="xrp",
    #     currency=transaction.token,
    #     amount=transaction.amount,
    #     transaction_type="send_token",
    #     receipient=transaction.receiver_addr
    # )

    # entry = crud.transaction.create(db=db, obj_in=record)

    return send

@router.post("/create-token/", response_model=Dict)
def create_token(
    create_token: xrp.CreateToken,
    
    ) -> Dict:
    client = XRPAssetClient()
    try:
        token = client.create_token(
        issuer_addr=create_token.issuer_addr,
        manager_addr=create_token.manager_addr,
        token_name=create_token.token_name,
        total_supply=create_token.total_supply,
        fee=create_token.fee
    )
    
    
    except Exception as exception:
        raise HTTPException(status_code=400, detail=str(exception))
    return token

@router.post("/burn-token/", response_model=Dict)
def burn_token(
    burn: xrp.BurnToken,
    
    ) -> Dict:
    client = XRPAssetClient()
    try:
        burn = client.burn_token(
        sender_addr=burn.sender_addr,
        token=burn.token,
        issuer=burn.issuer,
        amount=burn.amount,
        fee=burn.fee
    )
    
    
    except Exception as exception:
        raise HTTPException(status_code=400, detail=str(exception))
    return burn

@router.post("/mint-nft/", response_model=Dict)
def mint_nft(
    nft: xrp.MintNFT,
    
    ) -> Dict:
    client = XRPAssetClient()
    try:
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
    
    
    except Exception as exception:
        raise HTTPException(status_code=400, detail=str(exception))
    return mint

@router.post("/burn-nft/", response_model=Dict)
def burn_nft(
    nft: xrp.BurnNFT,
    
    ) -> Dict:
    client = XRPAssetClient()
    try:
        burn = client.burn_nft(
        sender_addr=nft.sender_addr,
        nftoken_id=nft.nftoken_id,
        holder=nft.holder,
        fee=nft.fee
    )
    
    
    except Exception as exception:
        raise HTTPException(status_code=400, detail=str(exception))
    return burn

@router.post("/create-xrp-check/", response_model=Dict)
def create_xrp_check(
    check: xrp.CreateXRPCheck,
    
    ) -> Dict:
    client = XRPObjectClient()
    try:
        xrp_check = client.create_xrp_check(
        sender_addr=check.sender_addr,
        receiver_addr=check.receiver_addr,
        amount=check.amount,
        expiry_date=check.expiry_date,
        fee=check.fee
    )
    
    
    except Exception as exception:
        raise HTTPException(status_code=400, detail=str(exception))
    return xrp_check

@router.get("/account-checks/", response_model=Dict)
def get_account_checks(
    wallet_address: str,
    limit: int = None,
    
    ) -> Dict:
    client = XRPObjectClient()
    try:
        account_checks = client.account_checks(
        wallet_addr=wallet_address,
        limit=limit
    )
    
    
    except Exception as exception:
        raise HTTPException(status_code=400, detail=str(exception))
    return account_checks

@router.get("/account-escrow/", response_model=Dict)
def get_account_escrows(
    wallet_address: str,
    limit: int = None,
    
    ) -> Dict:
    client = XRPObjectClient()
    try:
        account_escrows = client.account_xrp_escrows(
        wallet_addr=wallet_address,
        limit=limit
    )
    
    except Exception as exception:
        raise HTTPException(status_code=400, detail=str(exception))
    return account_escrows

@router.post("/create-offer/", response_model=Dict)
def create_offer(
    offer: xrp.CreateOffer,
    
    ) -> Dict:
    client = XRPObjectClient()
    try:
        offer = client.create_offer(
            sender_addr=offer.sender_addr,
            pay=offer.pay,
            receive=offer.receive,
            expiry_date=offer.expiry_date,
            fee=offer.fee,
            pay_type=offer.pay_type,
            receive_type=offer.receive_type,
            receive_issuer=offer.receive_issuer,
            pay_issuer=offer.pay_issuer
        )
        return offer
    
    except Exception as exception:
        raise HTTPException(status_code=400, detail=str(exception))

@router.get("/account-offers/", response_model=Dict)
def account_offers(
    wallet_addr: str,
    limit: int,
    
    ) -> Dict:
    client = XRPObjectClient()
    try:
        offers = client.account_offers(
        wallet_addr=wallet_addr,
        limit=limit
    )
    except Exception as exception:
        raise HTTPException(status_code=400, detail=str(exception))
    return offers

@router.post("/cancel-offer/", response_model=Dict)
def cancel_offer(
    cancel_offer: xrp.CancelOffer,
    
    ) -> Dict:
    client = XRPObjectClient()
    try:
        cancel = client.cancel_offer(
        sender_addr=cancel_offer.sender_addr,
        offer_seq=cancel_offer.offer_seq,
        fee=cancel_offer.fee
    )
    except Exception as exception:
        raise HTTPException(status_code=400, detail=str(exception))
    return cancel

@router.get("/all-offers/", response_model=Dict)
def all_offers(
    pay: float,
    receive: float,
    limit: int,
    
    ) -> list:
    client = XRPObjectClient()
    try:
        offers = client.all_offers(
        pay=pay,
        receive=receive,
        limit=limit
    )
    except Exception as exception:
        raise HTTPException(status_code=400, detail=str(exception))
    return offers

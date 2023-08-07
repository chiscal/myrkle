from typing import Any, Dict, Union, List
from fastapi import APIRouter, HTTPException, Depends
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
import crud
from api import deps

# from api import deps


from schemas import xamm

from blockchain.xrp_client import XammFinance

from blockchain.xrp.x_constants import XURLS_

test_url = XURLS_["TESTNET_URL"]
test_txns = XURLS_["TESTNET_TXNS"]
test_account =  XURLS_["TESTNET_ACCOUNT"]
main_url = XURLS_["MAINNET_URL"]
main_txns = XURLS_["MAINNET_TXNS"]
main_account = XURLS_["MAINNET_ACCOUNT"]

router = APIRouter()


@router.post("/cancel-offer/", response_model=Any)
def cancel_offer(
    *,
    transaction: xamm.CancelOffer
    ):
    if transaction.network == "testnet":
        client = XammFinance(test_url, test_account, test_txns)
    else:
        client = XammFinance(main_url, main_account, main_txns)
    try:
        return client.cancel_offer(
            transaction.sender_addr,
            transaction.offer_seq,
            transaction.fee
        )
    except Exception as exception:
        raise HTTPException(status_code=400, detail=str(exception))

@router.post("/create-order-book-liquidity/", response_model=Any)
def create_order_book_liquidity(
    *,
    transaction: xamm.CreateOrderBookLiquidity
    ):

    if transaction.network == "testnet":
        client = XammFinance(test_url, test_account, test_txns)
    else:
        client = XammFinance(main_url, main_account, main_txns)
    try:
        return client.create_order_book_liquidity(
            transaction.sender_addr,
            transaction.buy,
            transaction.sell,
            transaction.expiry_date,
            transaction.fee,
            transaction.buy_type,
            transaction.sell_type,
            transaction.buy_issuer,
            transaction.sell_issuer
        )
    except Exception as exception:
        raise HTTPException(status_code=400, detail=str(exception))

@router.get("/get-account-order-book-liquidity/{network}/{wallet_addr}/{limit}", response_model=Any)   
def get_account_order_book_liquidity(
    *,
    network: str,
    wallet_addr: str,
    limit : int = 30
    ):

    if network == "testnet":
        client = XammFinance(test_url, test_account, test_txns)
    else:
        client = XammFinance(main_url, main_account, main_txns)
    try:
        return client.get_account_order_book_liquidity(
            wallet_addr,
            limit,
        )
    except Exception as exception:
        raise HTTPException(status_code=400, detail=str(exception))


@router.post("/order-book-swap/", response_model=Any)
def order_book_swap(
    *,
    transaction: xamm.OrderBookSwap
    ):
    try:
        if transaction.network == "testnet":
            client = XammFinance(test_url, test_account, test_txns)
        else:
            client = XammFinance(main_url, main_account, main_txns)
        
        return client.order_book_swap(
            transaction.sender_addr,
            transaction.buy,
            transaction.sell,
            transaction.tf_sell,
            transaction.tf_fill_or_kill,
            transaction.tf_immediate_or_cancel,
            transaction.fee,
            transaction.buy_issuer,
            transaction.sell_issuer,
            transaction.buy_type,
            transaction.sell_type
        )
    except Exception as exception:
        raise HTTPException(status_code=400, detail=str(exception))


@router.get(
    '/token-balance/{wallet_address}/{name}/{issuer_address}',
    response_model=Any
)
def token_balance(wallet_address: str, name: str, issuer_address: str):
    client = XammFinance(main_url, main_account, main_txns)
    try:
        return client.token_balance(wallet_address, name, issuer_address)
    except Exception as exception:
        raise HTTPException(400, detail=exception)
    
@router.get('/status/{txid}/', response_model=Any)
def status(txid: str):
    client = XammFinance(main_url, main_account, main_txns)
    reponse = client.status(txid)
    if reponse:
        if reponse.get("status_code") == 400:
            return HTTPException(status_code=400, detail="Transaction not found")
        return reponse
    return HTTPException(status_code=400, detail="Transaction not found")

@router.get('/token-exists/{token}/{issuer}/{network}', response_model=Any)
def token_exists(token: str, issuer: str, network: str = "mainnet"):
    if network == "mainnet":
        client = XammFinance(main_url, main_account, main_txns)
    else:
        client = XammFinance(test_url, test_account, test_txns)
    return client.token_exists(token, issuer)

@router.get('/pending-offers/{wallet_addr}/{network}', response_model=Any)
def token_exists(wallet_addr: str, network: str = "mainnet"):
    if network == "mainnet":
        client = XammFinance(main_url, main_account, main_txns)
    else:
        client = XammFinance(test_url, test_account, test_txns)
    return client.pending_offers(wallet_addr)

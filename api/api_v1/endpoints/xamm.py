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
    limit : int = 0
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

@router.get("/order-book-swap/{wallet_address}", response_model=Union[xamm.XAMMWallet, Dict])
def get_pre_order_book(wallet_address: str, db: Session = Depends(deps.get_db)):
    wallet_info = crud.xamm_wallet.get_by_address(db, wallet_addr=wallet_address)
    if wallet_info:
        return wallet_info
    return {
        "wallet_addr": wallet_address,
        "tf_sell": False,
        "tf_fill_or_kill": False,
        "tf_immediate_or_cancel": False,
    }

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

@router.post("/sort-best-offer/", response_model=Any)
def sort_best_offer(*,
    transaction: xamm.SortBestOffer
    ):
    if transaction.network == "testnet":
        client = XammFinance(test_url, test_account, test_txns)
    else:
        client = XammFinance(main_url, main_account, main_txns)
    try:
        offer =  client.sort_best_offer(
            transaction.buy,
            transaction.sell,
            transaction.best_buy,
            transaction.best_sell,
            transaction.limit,
            transaction.buy_issuer,
            transaction.sell_issuer,
        )
        return offer
    except Exception as exception:
        raise HTTPException(status_code=400, detail=str(exception))


@router.get(
    '/token-balance/{wallet_address}/{name}/{issuer_address}',
    response_model=List
)
def token_balance(wallet_address: str,name: str, issuer_address: str):
    client = XammFinance(main_url, main_account, main_txns)
    try:
        return client.token_balance(wallet_address, name, issuer_address)
    except Exception as exception:
        raise HTTPException(400, detail=exception)
    
@router.get('/status/{txid}/{network}/', response_model=List)
def status(txid: str, network: str):
    mainnet = True
    client = XammFinance(main_url, main_account, main_txns)
    if network != "mainnet":
        mainnet = False
    return client.status(txid, mainnet)

@router.get('/token-exists/{token}/{issuer}/{network}', response_model=Dict)
def token_exists(token: str, issuer: str, network: str):
    if network == "mainnet":
        client = XammFinance(main_url, main_account, main_txns)
    else:
        client = XammFinance(test_url, test_account, test_txns)
    return client.token_exists(token, issuer)

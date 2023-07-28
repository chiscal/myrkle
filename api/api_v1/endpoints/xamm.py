from typing import Any

from fastapi import APIRouter, HTTPException

# from api import deps


from schemas import xamm

from blockchain.xrp_client import XammFinance

from blockchain.xrp.x_constants import XURLS_

test_url = XURLS_["TESTNET_URL"]
test_txns = XURLS_["TESTNET_TXNS"]
test_account =  XURLS_["TESTNET_ACCOUNT"]

router = APIRouter()


@router.post("/cancel-offer/", response_model=Any)
def cancel_offer(
    *,
    transaction: xamm.CancelOffer
    ):

    client = XammFinance(test_url, test_account, test_txns)
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

    client = XammFinance(test_url, test_account, test_txns)
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

@router.post("/get-account-order-book-liquidity/", response_model=Any)   
def get_account_order_book_liquidity(
    *,
    transaction: xamm.GetAccountOrderBookLiquidity
    ):

    client = XammFinance(test_url, test_account, test_txns)
    try:
        return client.get_account_order_book_liquidity(
            transaction.wallet_addr,
            transaction.limit,
        )
    except Exception as exception:
        raise HTTPException(status_code=400, detail=str(exception))

@router.post("/order-book-swap/", response_model=Any)
def order_book_swap(
    *,
    transaction: xamm.OrderBookSwap
    ):
    client = XammFinance(test_url, test_account, test_txns)
    try:
        return client.order_book_swap(
            transaction.sender_addr,
            transaction.buy,
            transaction.sell,
            transaction.swap_all,
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
    client = XammFinance()
    try:
        return client.sort_best_offer(
            transaction.buy,
            transaction.sell,
            transaction.best_buy,
            transaction.best_sell,
            transaction.limit,
            transaction.buy_issuer,
            transaction.sell_issuer,
        )
    except Exception as exception:
        raise HTTPException(status_code=400, detail=str(exception))

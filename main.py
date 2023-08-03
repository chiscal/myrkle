import asyncio
import concurrent.futures


import time
from fastapi import FastAPI,  WebSocket, WebSocketDisconnect
from starlette.middleware.cors import CORSMiddleware
from blockchain.xrp_client import XRPWalletClient, XammFinance

# from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
# from websockets.exceptions import ConnectionClosedError, ConnectionClosedOK
# from notification.websocket_manager import manager
# from notification.messaging_bq import mq

# from api.deps import get_current_user

from api.api_v1.api import api_router
from core.config import settings

import uvicorn
from blockchain.xrp.x_constants import XURLS_
# import os
# from blockchain.xrp_client import XRPWalletClient

test_url = XURLS_["TESTNET_URL"]
test_txns = XURLS_["TESTNET_TXNS"]
test_account =  XURLS_["TESTNET_ACCOUNT"]
main_url = XURLS_["MAINNET_URL"]
main_txns = XURLS_["MAINNET_TXNS"]
main_account = XURLS_["MAINNET_ACCOUNT"]

app = FastAPI(
    title=settings.PROJECT_NAME, openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Set all CORS enabled origins
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(api_router, prefix=settings.API_V1_STR)

class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)


manager = ConnectionManager()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(f"Message text was: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast(f"Disconnected")

@app.websocket("/ws/brower_id/{browser_id}")
async def websocker_notif(websocket: WebSocket, browser_id: str):
    await websocket.accept()
    try:
        while True:
            message = {
                browser_id: {
                    "message": "A user has requested you to sign his transaction"
                }
            }
            data = await websocket.receive_text()
            if data == "send":
                await websocket.send_json(message)
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast(f"Disconnected")


@app.websocket("/ws/balance/{wallet_address}")
async def get_wallet_balance(websocket: WebSocket, wallet_address: str):
    client = XRPWalletClient()
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            if data == "send":
                loop = asyncio.get_running_loop()
                # test = client.get_balance(wallet_address)
                loop.run_in_executor(None, lambda: asyncio.run(websocket.send_json(client.get_balance(wallet_address))))
                # await websocket.send_json(test)
                time.sleep(5)
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast(f"Disconnected")


@app.websocket("/ws/get-account-order-book-liquidity/{wallet_addr}/{network}/{limit}")
async def get_account_order_book_liquidity(websocket: WebSocket, wallet_addr: str, network: str = "mainnet", limit: int = 20):
    client = XammFinance()
    if network == "testnet":
        client = XammFinance(test_url, test_account, test_txns)
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            if data == "send":
                loop = asyncio.get_running_loop()
                loop.run_in_executor(
                    None,
                    lambda: asyncio.run(
                        websocket.send_json(
                            client.get_account_order_book_liquidity(wallet_addr, limit)
                            )
                        )
                    )
                time.sleep(5)
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast(f"Disconnected")


@app.websocket("/ws/sort-best-offer/{network}")
async def sort_best_offer(websocket: WebSocket, network: str):
    response = {}
    client = XammFinance()
    if network == "testnet":
        client = XammFinance(test_url, test_account, test_txns)
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_json()
            response = data
            while len(response) > 0:
                loop = asyncio.get_running_loop()
                loop.run_in_executor(
                    None,
                    lambda: asyncio.run(
                        websocket.send_json(
                            client.sort_best_offer(
                                    buy=response["buy"],
                                    sell=response["sell"],
                                    best_buy=response["best_buy"],
                                    best_sell=response["best_sell"],
                                    limit=response["limit"],
                                    buy_issuer=response.get("buy_issuer"),
                                    sell_issuer=response.get("sell_issuer")
                                )
                            )
                        )
                    )
                time.sleep(5)
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast(f"Disconnected")


@app.websocket("/ws/token-balance/{wallet_addr}/{name}/{issuer_addr}/{network}")
async def token_balance(websocket: WebSocket, wallet_addr: str, name: str, issuer_addr: str, network: str):
    client = XammFinance()
    if network == "testnet":
        client = XammFinance(test_url, test_account, test_txns)
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            if data == "send":
                loop = asyncio.get_running_loop()
                loop.run_in_executor(
                    None,
                    lambda: asyncio.run(
                        websocket.send_json(
                            client.token_balance(
                                    wallet_addr=wallet_addr,
                                    name=name,
                                    issuer_addr=issuer_addr,
                                )
                            )
                        )
                    )
                time.sleep(5)
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast(f"Disconnected")


@app.websocket("/ws/status/{txid}/{mainnet}")
async def status(websocket: WebSocket, txid: str, mainnet: bool):
    client = XammFinance()
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            if data == "send":
                loop = asyncio.get_running_loop()
                loop.run_in_executor(
                    None,
                    lambda: asyncio.run(
                        websocket.send_json(
                            client.status(
                                    txid=txid,
                                    mainnet=mainnet,
                                )
                            )
                        )
                    )
                time.sleep(5)
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast(f"Disconnected")


@app.websocket("/ws/token-exists/{token}/{issuer}")
async def status(websocket: WebSocket, token: str, issuer: str):
    client = XammFinance()
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            if data == "send":
                loop = asyncio.get_running_loop()
                loop.run_in_executor(
                    None,
                    lambda: asyncio.run(
                        websocket.send_json(
                            client.token_exists(
                                    token=token,
                                    issuer=issuer,
                                )
                            )
                        )
                    )
                time.sleep(5)
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast(f"Disconnected")


@app.on_event("startup")
def startup_event():
    # instantiate the ThreadPool
    app.state.pool = concurrent.futures.ThreadPoolExecutor()

@app.on_event("shutdown")
def shutdown_event():  
    # terminate the ThreadPool
    app.state.pool.shutdown()

if __name__ == '__main__':
    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True)

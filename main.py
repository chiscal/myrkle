# import asyncio

import time
from fastapi import FastAPI,  WebSocket, WebSocketDisconnect
from starlette.middleware.cors import CORSMiddleware
from blockchain.xrp_client import XRPWalletClient

# from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
# from websockets.exceptions import ConnectionClosedError, ConnectionClosedOK
# from notification.websocket_manager import manager
# from notification.messaging_bq import mq

# from api.deps import get_current_user

from api.api_v1.api import api_router
from core.config import settings

import uvicorn
# import os
# from blockchain.xrp_client import XRPWalletClient

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

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        await websocket.send_text(f"Message text was: {data}")

@app.websocket("/ws/brower_id/{browser_id}")
async def websocker_notif(websocket: WebSocket, browser_id: str):
    await websocket.accept()
    while True:
        message = {
            browser_id: {
                "message": "A user has requested you to sign his transaction"
            }
        }
        data = await websocket.receive_text()
        if data == "send":
            await websocket.send_json(message)


@app.websocket("/ws/balance/{wallet_address}")
async def get_wallet_balance(websocket: WebSocket, wallet_address: str):
    client = XRPWalletClient()
    await websocket.accept()
    try:
        while True:
            await websocket.send_text("Yamete")
            time.sleep(5)
            await websocket.send_json(client.get_balance(wallet_address))
    except WebSocketDisconnect:
        print("Client disconnected")


if __name__ == '__main__':
    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True)

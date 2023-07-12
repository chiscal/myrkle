import time
import asyncio
from typing import Any, Dict, List
from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session

import models, schemas
from api import deps
from blockchain.xrp_client import XRPWalletClient

router = APIRouter()

manager = deps.ConnectionManager()

async def aync_func(manager: manager, frequency: int, message, websocket: WebSocket):
    while True:
        await manager.send_personal_message()
        time.sleep(frequency - time.time() % frequency)


@router.websocket("/check")
async def websocket_endpoint(websocket: WebSocket):
    # await for connections
    await websocket.accept()

    try:
        # await for messages and send messages
        while True:
            msg = await websocket.receive_text()
            if msg.lower() == "close":
                await websocket.close()
                break
            else:
                print(f'CLIENT says - {msg}')
                await websocket.send_text(f"Your message was: {msg}")

            await websocket.send_text("Connection established!")
    except WebSocketDisconnect:
        print("Client disconnected")

@router.websocket("/{wallet_address}")
async def get_wallet_balance(websocket: WebSocket, wallet_address: str):
    client = XRPWalletClient()

    await websocket.accept()
    
    try:
        # wallets = client.get_balance(wallet_address)    
        print("got here")
        # rets = await asyncio.gather(*client.get_balance(wallet_address))

        while True:
            msg = await websocket.receive_text()
            if msg.lower() == "close":
                await websocket.close()
                break
            else:
                print(f'CLIENT says - {msg}')
                await websocket.send_text(f"Your message was: {msg}")
            
            await websocket.send_json(client.get_balance(wallet_address))
    except WebSocketDisconnect:
        print("Client disconnected")


@router.websocket("/{wallet_address}")
async def get_wallet_transactions(websocket: WebSocket, wallet_address: str):
    await manager.connect(websocket)
    try:
        client = XRPWalletClient()
        transactions = client.get_transactions(wallet_address)
        await manager.send_personal_message(transactions, websocket)
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.send_personal_message(f"Please refresh your browser", websocket)


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

if __name__ == '__main__':
    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True)

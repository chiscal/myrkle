from fastapi import APIRouter

from api.api_v1.endpoints import login, notifications, users, xrp, xamm, wallets

api_router = APIRouter()

api_router.include_router(login.router, tags=["login"])
# api_router.include_router(notifications.router, tags=["notifs"])
api_router.include_router(xrp.router, prefix="/xrp", tags=["xrp"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(xamm.router, prefix="/xamm", tags=["xamm"])
# api_router.include_router(wallets.router, prefix="/wallets", tags=["wallets"])

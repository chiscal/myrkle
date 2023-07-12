# import asyncio
#
# from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
# from websockets.exceptions import ConnectionClosedError, ConnectionClosedOK
# # from notification.websocket_manager import manager
# # from notification.messaging_bq import mq
#
# from api.deps import get_current_user
#
#
# router = APIRouter()
#
# @router.websocket("notif/ws")
# async def notification_socket(
#     websocket: WebSocket, user: dict = Depends(get_current_user)
# ):
#     await manager.connect(websocket, user["id"])
#
#     try:
#         if manager.get_ws(user["id"]):
#             user_meesage = mq.get_user_messages(user["id"])
#
#             if user_meesage != None:
#                 for message in user_meesage:
#                     if message != None:
#                         message_status = await manager.personal_notification(message)
#                         print(message_status)
#                         # delete the message from the queue if successfully sent via WebSocket
#                         if message_status:
#                             mq.channel.basic_ack(delivery_tag=message["delivery_tag"])
#
#         hang = True
#         while hang:
#             try:
#                 await asyncio.sleep(1)
#                 await manager.ping(websocket)
#             except asyncio.exceptions.CancelledError:
#                 break
#
#     except (WebSocketDisconnect, ConnectionClosedError, ConnectionClosedOK):
#         manager.disconnect(user["id"])

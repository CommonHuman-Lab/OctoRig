# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
"""WebSocket endpoint — /ws/events — broadcasts platform events to connected browsers."""
import asyncio
import json as _json

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from jose import JWTError
from sqlalchemy.orm import Session

from app.core.security import decode_access_token
from app.database import get_db
from app.models.user import User
from app.ws.manager import manager

router = APIRouter(tags=["websocket"])


@router.websocket("/ws/events")
async def events_ws(websocket: WebSocket, db: Session = Depends(get_db)) -> None:
    await websocket.accept()

    # Auth via first message avoids placing JWT in the URL, where every proxy/LB logs it
    try:
        raw = await asyncio.wait_for(websocket.receive_text(), timeout=10.0)
        token = _json.loads(raw).get("token", "")
        user_id = decode_access_token(token)
        current_user = db.get(User, int(user_id))
        if current_user is None or not current_user.is_active:
            await websocket.close(code=4001)
            return
    except (TimeoutError, JWTError, Exception):
        await websocket.close(code=4001)
        return

    manager.register(websocket)
    try:
        while True:
            msg = await websocket.receive_text()
            if msg == "ping":
                await websocket.send_text('{"type":"pong"}')
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception:
        manager.disconnect(websocket)

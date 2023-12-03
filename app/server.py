from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from fastapi import (
    APIRouter, 
    Request, 
    WebSocket, 
    WebSocketDisconnect
)

from .manager import ws_manager

class Message(BaseModel):
    message: str


server_router = APIRouter()
templates = Jinja2Templates(directory='templates')

@server_router.get('/')
def route(request: Request, response_classe=HTMLResponse):
    return templates.TemplateResponse(
        'chat.html', {'request': request}
    )

@server_router.websocket('/ws/{user}')
async def handle_websocket(
        websocket: WebSocket,
        user: str,
):
    await ws_manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await ws_manager.broadcast(data)
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)

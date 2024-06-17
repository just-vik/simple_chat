from fastapi import Depends, FastAPI, WebSocket, WebSocketDisconnect
from sqlalchemy import select
from db.engine import get_async_session
from db.models import Messages
from web_socket_mngr import manager
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

@app.websocket('/ws/{username}')
async def websocket_endpoint(websocket: WebSocket, username: str, session: AsyncSession = Depends(get_async_session)):
    await manager.connect(websocket)
    try:
        while True:
            message = await websocket.receive_text()
            data = f'{username}-{message}'
            await manager.brodcast(data)

            obj = Messages(
                message = data
            )

            session.add(obj)
            await session.commit()

        
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.brodcast(f'-Пользователь {username} покинул чат')


@app.get('/getMessages')
async def getMessages(session: AsyncSession = Depends(get_async_session)):
    query = select(Messages)
    res = await session.execute(query)
    data = res.scalars()
    
    messages = []
    for i in data:
        messages.append(i.message)
        return messages


app.add_middleware(
    CORSMiddleware,
    allow_origins =['*'],
    allow_methods =['*'],
    allow_headers =['*']
)
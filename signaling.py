# signaling.py
import asyncio, json
from aiohttp import web, WSMsgType

ROOMS = {}  # room_id → set of WebSocketResponse

async def ws_handler(request):
    room_id = request.match_info['room']
    ws = web.WebSocketResponse()
    await ws.prepare(request)

    conns = ROOMS.setdefault(room_id, set())
    conns.add(ws)

    try:
        async for msg in ws:
            if msg.type == WSMsgType.TEXT:
                # relay to all other peers in room
                for peer in conns:
                    if peer is not ws:
                        await peer.send_str(msg.data)
            elif msg.type == WSMsgType.ERROR:
                break
    finally:
        conns.remove(ws)

    return ws

app = web.Application()
app.router.add_get('/ws/{room}', ws_handler)

if __name__ == '__main__':
    web.run_app(app, port=8765)

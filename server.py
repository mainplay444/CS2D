"""Минимальный демонстрационный WebSocket-сервер комнат.
Это НЕ полноценный игровой сервер: он передаёт сообщения участникам комнаты.
Запуск: python -m pip install websockets && python server.py
"""
import asyncio, json, secrets
import websockets
ROOMS = {}
async def handler(ws):
    room = None
    try:
        async for raw in ws:
            try: msg = json.loads(raw)
            except json.JSONDecodeError: continue
            action = msg.get('action')
            if action == 'create':
                room = secrets.token_hex(3).upper()[:6]
                ROOMS.setdefault(room, set()).add(ws)
                await ws.send(json.dumps({'type':'room_created','code':room}))
            elif action == 'join':
                code = str(msg.get('code','')).upper()
                if code not in ROOMS:
                    await ws.send(json.dumps({'type':'error','message':'Комната не найдена'})); continue
                room = code; ROOMS[room].add(ws)
                await ws.send(json.dumps({'type':'joined','code':room,'players':len(ROOMS[room])}))
                await broadcast(room, {'type':'player_joined','players':len(ROOMS[room])}, exclude=ws)
            elif room and action == 'state':
                await broadcast(room, {'type':'state','player':msg.get('player',{})}, exclude=ws)
            elif room and action == 'chat':
                await broadcast(room, {'type':'chat','text':str(msg.get('text',''))[:200]}, exclude=ws)
    finally:
        if room and room in ROOMS:
            ROOMS[room].discard(ws)
            if not ROOMS[room]: del ROOMS[room]
            else: await broadcast(room, {'type':'player_left','players':len(ROOMS[room])})
async def broadcast(room, payload, exclude=None):
    if room not in ROOMS: return
    data = json.dumps(payload)
    peers = [p for p in ROOMS[room] if p is not exclude]
    if peers: await asyncio.gather(*(p.send(data) for p in peers), return_exceptions=True)
async def main():
    async with websockets.serve(handler, '0.0.0.0', 8765):
        print('Last Round room server listening on ws://0.0.0.0:8765')
        await asyncio.Future()
if __name__ == '__main__': asyncio.run(main())

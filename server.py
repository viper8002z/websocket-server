import asyncio
import websockets
from urllib.parse import urlparse, parse_qs

clients = {
    "echo": {},
    "reverse": {}
}

async def handler(websocket, path):
    parsed = urlparse(path)
    clean_path = parsed.path.lstrip("/")
    query = parse_qs(parsed.query)
    client_id = query.get("id", [None])[0]

    if not client_id:
        await websocket.close(code=1008, reason="Missing client ID")
        return
    if clean_path not in clients:
        await websocket.close(code=1008, reason="Invalid path")
        return

    clients[clean_path][client_id] = websocket
    print(f"Client {client_id} connected on /{clean_path}")

    try:
        async for message in websocket:
            if ":" in message:
                target_id, msg = message.split(":", 1)
                target_ws = clients[clean_path].get(target_id)
                if target_ws:
                    await target_ws.send(msg)
            else:
                for cid, ws in list(clients[clean_path].items()):
                    if ws != websocket:
                        await ws.send(message)
    finally:
        del clients[clean_path][client_id]
        print(f"Client {client_id} disconnected from /{clean_path}")

async def main():
    async with websockets.serve(handler, "0.0.0.0", 10000):
        print("Server running on port 10000")
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())
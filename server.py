import asyncio
import websockets
import urllib.parse

LISTEN_ADDRESS = "0.0.0.0"
LISTEN_PORT = 65535

com1_clients = {}
com2_clients = {}

async def websocket_handler(websocket):
    parsed_url = urllib.parse.urlparse(websocket.request.path)
    parsed_query = urllib.parse.parse_qs(parsed_url.query)
    client_id = parsed_query.get("id", [None])[0]

    if client_id is None:
        await websocket.close(code=1008, reason="missing id parameter")
        return

    try:
        if parsed_url.path == "/com1":
            com1_clients[client_id] = websocket

            try:
                async for message in websocket:
                    if com2_clients.get(client_id) is not None:
                        await com2_clients[client_id].send(message)
            except websockets.exceptions.ConnectionClosed:
                del com1_clients[client_id]

        elif parsed_url.path == "/com2":
            com2_clients[client_id] = websocket

            try:
                async for message in websocket:
                    if com1_clients.get(client_id) is not None:
                        await com1_clients[client_id].send(message)
            except websockets.exceptions.ConnectionClosed:
                del com2_clients[client_id]

        else:
            await websocket.close(code=1008, reason="invalid path")
            return
    except websockets.exceptions.ConnectionClosedError:
        pass

async def main():
    async with websockets.serve(websocket_handler, LISTEN_ADDRESS, LISTEN_PORT):
        print(f"WebSocket server started on ws://{LISTEN_ADDRESS}:{LISTEN_PORT}")
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())

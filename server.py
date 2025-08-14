import asyncio
import websockets

async def echo(websocket):
    async for message in websocket:
        print(f"Received from client: {message}")
        await websocket.send(f"Server echoed: {message}")
        print(f"Sent back to client: Server echoed: {message}")

async def main():
    async with websockets.serve(echo, "0.0.0.0", 65535):
        print("WebSocket server started on ws://0.0.0.0:65535")
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())

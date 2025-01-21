import asyncio
import json

import websockets


async def handle_client(websocket):
    try:
        async for message in websocket:
            print(f"Received:{message}")

            response = {"status": "success", "message": f"Echo: {message}"}

        await websockets.send(json.dumps(response))
    except websocket.exceptions.ConnectionClosed:
        print("client disconnected")


async def main():
    async with websockets.serve(handle_client, "localhost", 8765):
        print("server started on ws://localhost:8765")
        await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(main())

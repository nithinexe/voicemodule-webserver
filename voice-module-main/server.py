# ai_server.py
import asyncio
import json

import websockets
from openai import AsyncOpenAI


class AIServer:
    def __init__(self):
        self.client = AsyncOpenAI(api_key="your-api-key-here")

    async def generate_response(self, message):
        """Generate response using GPT"""
        try:
            response = await self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful AI assistant. Keep responses concise and natural.",
                    },
                    {"role": "user", "content": message},
                ],
            )
            return {
                "status": "success",
                "type": "ai_response",
                "content": response.choices[0].message.content,
            }
        except Exception as e:
            return {"status": "error", "type": "error", "content": str(e)}

    async def handle_client(self, websocket):
        """Handle WebSocket client connection"""
        try:
            async for message in websocket:
                try:
                    # Parse incoming message
                    data = json.loads(message)

                    # Process based on message type
                    if data["type"] == "speech":
                        # Generate AI response
                        response = await self.generate_response(data["content"])
                    else:
                        response = {
                            "status": "error",
                            "type": "error",
                            "content": "Unknown message type",
                        }

                    # Send response
                    await websocket.send(json.dumps(response))

                except json.JSONDecodeError:
                    await websocket.send(
                        json.dumps(
                            {
                                "status": "error",
                                "type": "error",
                                "content": "Invalid JSON format",
                            }
                        )
                    )

        except websockets.exceptions.ConnectionClosed:
            print("Client disconnected")

    async def start_server(self):
        """Start the WebSocket server"""
        async with websockets.serve(self.handle_client, "localhost", 8765):
            print("AI Server started on ws://localhost:8765")
            await asyncio.Future()  # run forever

    def run(self):
        """Run the server"""
        try:
            asyncio.run(self.start_server())
        except KeyboardInterrupt:
            print("\nServer stopped by user")


if __name__ == "__main__":
    # Install required packages:
    # pip install websockets openai

    server = AIServer()
    server.run()

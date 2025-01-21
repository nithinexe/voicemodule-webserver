import asyncio
import json

import speech_recognition as sr
import websockets


class SpeechClient:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.uri = "ws://localhost:8765"

    def get_speech_input(self):
        """Get speech input from microphone"""
        with sr.Microphone() as source:
            print("Listening...")

            self.recognizer.adjust_for_ambient_noise(source)
            try:
                audio = self.recognizer.listen(source, timeout=5)

                text = self.recognizer.recognize_google(audio)
                print(f"You said: {text}")
                return text

            except sr.UnknownValueError:
                print("Could not understand audio")
                return None
            except sr.RequestError as e:
                print(f"Could not request results;{e}")
                return None

    async def connect_and_send(self):
        """Connect to a websocket server and send speech input"""
        async with websockets.connect(self.uri) as websocket:
            while True:
                text = self.get_speech_input()

                if text:
                    message = {"type": "speech", "content": text}

                    await websocket.send(json.dumps(message))
                    print("Waiting for response....")

                    response = await websocket.recv()
                    response_data = json.loads(response)
                    print(f"server response: {response_data}")

    def run(self):
        """Start the speech client"""
        try:
            asyncio.run(self.connect_and_send())
        except KeyboardInterrupt:
            print("\nClient stopped by user")


if __name__ == "__main__":
    client = SpeechClient()
    client.run()

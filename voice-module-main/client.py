# complete_client.py
import asyncio
import json
import threading

import pyttsx3
import speech_recognition as sr
import websockets


class CompleteClient:
    def __init__(self):
        # Initialize speech recognition
        self.recognizer = sr.Recognizer()

        # Initialize text-to-speech
        self.engine = pyttsx3.init()
        self.setup_tts()

        # WebSocket URI
        self.uri = "ws://localhost:8765"

    def setup_tts(self):
        """Configure text-to-speech settings"""
        voices = self.engine.getProperty("voices")
        self.engine.setProperty("voice", voices[0].id)  # Index 0 for male, 1 for female
        self.engine.setProperty("rate", 150)  # Speech rate

    def speak(self, text):
        """Convert text to speech"""

        def tts_thread():
            self.engine.say(text)
            self.engine.runAndWait()

        # Run TTS in a separate thread to avoid blocking
        thread = threading.Thread(target=tts_thread)
        thread.start()
        thread.join()

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
                print(f"Could not request results; {e}")
                return None

    async def connect_and_send(self):
        """Connect to WebSocket server and handle communication"""
        while True:  # Keep trying to reconnect if connection fails
            try:
                async with websockets.connect(self.uri) as websocket:
                    print("Connected to server")

                    while True:  # Main communication loop
                        # Get speech input
                        text = self.get_speech_input()

                        if text:
                            # Create message payload
                            message = {"type": "speech", "content": text}

                            # Send to server
                            await websocket.send(json.dumps(message))
                            print("Waiting for response...")

                            # Get response
                            response = await websocket.recv()
                            response_data = json.loads(response)

                            # Handle response
                            if response_data["status"] == "success":
                                print(f"AI: {response_data['content']}")
                                self.speak(response_data["content"])
                            else:
                                print(f"Error: {response_data['content']}")

            except websockets.exceptions.ConnectionClosed:
                print("Connection lost. Retrying in 5 seconds...")
                await asyncio.sleep(5)
            except Exception as e:
                print(f"Error: {e}")
                await asyncio.sleep(5)

    def run(self):
        """Start the client"""
        try:
            asyncio.run(self.connect_and_send())
        except KeyboardInterrupt:
            print("\nClient stopped by user")


if __name__ == "__main__":
    # Install required packages:
    # pip install websockets speech_recognition pyaudio pyttsx3

    client = CompleteClient()
    client.run()

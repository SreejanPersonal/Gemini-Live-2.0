import asyncio
import traceback
import pyaudio
from google import genai
from src.config import (
    FORMAT,
    CHANNELS,
    RECEIVE_SAMPLE_RATE,
    MODEL,
    API_VERSION
)

# Import taskgroup for compatibility with Python versions below 3.11
try:
    from asyncio import TaskGroup
except ImportError:
    from taskgroup import TaskGroup

class TextOnlyHandler:
    def __init__(self, logger):
        self.logger = logger
        self.audio_in_queue = asyncio.Queue()
        self.ai_speaking = False
        self.client = genai.Client(http_options={"api_version": API_VERSION})
        self.CONFIG = {"generation_config": {"response_modalities": ["AUDIO"]}}
        self.pya = pyaudio.PyAudio()

    async def send_text(self, session):
        """Continuously reads text input from the user and sends it to the AI session."""
        try:
            while True:
                text = await asyncio.to_thread(
                    input,
                    "You: ",
                )
                if text.lower() == "q":
                    break
                await session.send(text or ".", end_of_turn=True)
        except Exception as e:
            traceback.print_exc()

    async def receive_audio(self, session):
        """Receives audio responses from the AI session and queues them for playback."""
        try:
            while True:
                turn = session.receive()
                async for response in turn:
                    if data := response.data:
                        await self.audio_in_queue.put(data)
                        continue  # Continue to the next response
                    if text := response.text:
                        print(f"Assistant: {text}")
                # After the turn is complete, clear the audio queue to stop any ongoing playback
                while not self.audio_in_queue.empty():
                    self.audio_in_queue.get_nowait()
        except Exception as e:
            traceback.print_exc()

    async def play_audio(self):
        """Plays audio data received from the AI session."""
        audio_stream = self.pya.open(
            format=FORMAT,
            channels=CHANNELS,
            rate=RECEIVE_SAMPLE_RATE,
            output=True,
        )
        try:
            while True:
                data = await self.audio_in_queue.get()
                if not self.ai_speaking:
                    self.ai_speaking = True  # AI starts speaking
                    print("Assistant is speaking...")
                await asyncio.to_thread(audio_stream.write, data)
                if self.audio_in_queue.empty():
                    self.ai_speaking = False  # AI has finished speaking
                    print("You can type your message now.")
        except Exception as e:
            traceback.print_exc()
        finally:
            audio_stream.stop_stream()
            audio_stream.close()

    async def run(self):
        """Initializes the AI session and starts all asynchronous tasks."""
        try:
            async with (
                self.client.aio.live.connect(model=MODEL, config=self.CONFIG) as session,
                TaskGroup() as tg,
            ):
                self.session = session

                # Create asynchronous tasks
                send_text_task = tg.create_task(self.send_text(session))
                tg.create_task(self.receive_audio(session))
                tg.create_task(self.play_audio())

                # Keep the main coroutine alive until send_text completes
                await send_text_task

        except asyncio.CancelledError:
            pass
        except Exception as e:
            traceback.print_exc()

    def close(self):
        """Closes PyAudio instance."""
        self.pya.terminate()
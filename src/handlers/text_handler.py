# src/handlers/text_handler.py

import asyncio
import base64
import io
import sys
import traceback
import cv2
import pyaudio
import PIL.Image
import mss
from exceptiongroup import ExceptionGroup
from google import genai
from src.config import (
    FORMAT,
    CHANNELS,
    SEND_SAMPLE_RATE,
    RECEIVE_SAMPLE_RATE,
    CHUNK_SIZE,
    MODEL,
    API_VERSION
)
from src.utils.logger import setup_logger

class TextOnlyHandler:
    def __init__(self, logger):
        self.logger = logger
        self.audio_in_queue = asyncio.Queue()
        self.out_queue = asyncio.Queue(maxsize=5)
        self.ai_speaking = False
        self.client = genai.Client(http_options={"api_version": API_VERSION})
        self.CONFIG = {"generation_config": {"response_modalities": ["AUDIO"]}}
        self.pya = pyaudio.PyAudio()

        # Compatibility for Python versions below 3.11
        if sys.version_info < (3, 11, 0):
            import taskgroup
            import exceptiongroup
            asyncio.TaskGroup = taskgroup.TaskGroup
            asyncio.ExceptionGroup = exceptiongroup.ExceptionGroup

    async def send_text(self, session):
        """Continuously reads text input from the user and sends it to the AI session."""
        self.logger.info("Text send task started.")
        try:
            while True:
                text = await asyncio.to_thread(
                    input,
                    "Enter your message (type 'q' to quit): ",
                )
                if text.lower() == "q":
                    break
                await session.send(text or ".", end_of_turn=True)
        except Exception as e:
            self.logger.error(f"Error in send_text: {e}")
            traceback.print_exc()

    async def receive_audio(self, session):
        """Receives audio responses from the AI session and queues them for playback."""
        self.logger.info("Text receive task started.")
        try:
            while True:
                turn = session.receive()
                async for response in turn:
                    if data := response.data:
                        await self.audio_in_queue.put(data)
                        continue  # Continue to the next response
                    if text := response.text:
                        self.logger.info(f"AI: {text}")
                # After the turn is complete (e.g., when new input is sent)
                # Clear the audio queue to stop any ongoing playback
                while not self.audio_in_queue.empty():
                    self.audio_in_queue.get_nowait()
        except Exception as e:
            self.logger.error(f"Error in receive_audio: {e}")
            traceback.print_exc()

    async def play_audio(self):
        """Plays audio data received from the AI session."""
        self.logger.info("Text play task started.")
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
                await asyncio.to_thread(audio_stream.write, data)
                if self.audio_in_queue.empty():
                    self.ai_speaking = False  # AI has finished speaking
        except Exception as e:
            self.logger.error(f"Error in play_audio: {e}")
            traceback.print_exc()
        finally:
            audio_stream.stop_stream()
            audio_stream.close()

    async def run(self):
        """Initializes the AI session and starts all asynchronous tasks."""
        self.logger.info("Starting TextOnlyHandler.")
        try:
            async with (
                self.client.aio.live.connect(model=MODEL, config=self.CONFIG) as session,
                asyncio.TaskGroup() as tg,
            ):
                self.session = session

                # Create asynchronous tasks
                tg.create_task(self.send_text(session))
                tg.create_task(self.receive_audio(session))
                tg.create_task(self.play_audio())

                # Keep the main coroutine alive until send_text completes
                await asyncio.Event().wait()

        except asyncio.CancelledError:
            self.logger.info("TextOnlyHandler cancelled.")
        except ExceptionGroup as EG:
            self.logger.error(f"ExceptionGroup in TextOnlyHandler: {EG}")
            traceback.print_exception(type(EG), EG, EG.__traceback__)
        except Exception as e:
            self.logger.error(f"Exception in TextOnlyHandler: {e}")
            traceback.print_exc()

    def close(self):
        """Closes PyAudio instance."""
        self.pya.terminate()
        self.logger.info("PyAudio terminated.")

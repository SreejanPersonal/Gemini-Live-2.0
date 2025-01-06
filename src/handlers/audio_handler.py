import asyncio
import pyaudio
import traceback
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

# Import taskgroup for compatibility with Python versions below 3.11
try:
    from asyncio import TaskGroup
except ImportError:
    from taskgroup import TaskGroup

class AudioOnlyHandler:
    def __init__(self, logger):
        self.logger = logger
        self.audio_in_queue = asyncio.Queue()
        self.audio_out_queue = asyncio.Queue()
        self.ai_speaking = False
        self.client = genai.Client(http_options={"api_version": API_VERSION})
        self.CONFIG = {"generation_config": {"response_modalities": ["AUDIO"]}}
        self.pya = pyaudio.PyAudio()

    async def send_audio(self, session):
        """Continuously captures audio from the microphone and sends it to the AI session."""
        try:
            while True:
                audio_data = await self.audio_in_queue.get()
                if audio_data is None:
                    break  # Exit signal received
                await session.send({"data": audio_data, "mime_type": "audio/pcm"}, end_of_turn=True)
        except Exception as e:
            traceback.print_exc()

    async def receive_audio(self, session):
        """Receives audio responses from the AI session and queues them for playback."""
        try:
            while True:
                turn = session.receive()
                async for response in turn:
                    if data := response.data:
                        await self.audio_out_queue.put(data)
                    if text := response.text:
                        print(f"Assistant: {text}")
                # After the turn is complete, clear the audio queue to stop any ongoing playback
                while not self.audio_out_queue.empty():
                    self.audio_out_queue.get_nowait()
        except Exception as e:
            traceback.print_exc()

    async def listen_audio(self):
        """Listens to the microphone input and places audio data into the queue for sending."""
        mic_info = self.pya.get_default_input_device_info()
        audio_stream = self.pya.open(
            format=FORMAT,
            channels=CHANNELS,
            rate=SEND_SAMPLE_RATE,
            input=True,
            input_device_index=mic_info["index"],
            frames_per_buffer=CHUNK_SIZE,
        )
        try:
            print("Listening... You can speak now.")
            while True:
                if not self.ai_speaking:
                    data = await asyncio.to_thread(
                        audio_stream.read, CHUNK_SIZE, exception_on_overflow=False
                    )
                    await self.audio_in_queue.put(data)
                else:
                    await asyncio.sleep(0.1)
        except Exception as e:
            traceback.print_exc()
        finally:
            audio_stream.stop_stream()
            audio_stream.close()
            print("Stopped Listening.")

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
                data = await self.audio_out_queue.get()
                if not self.ai_speaking:
                    self.ai_speaking = True  # AI starts speaking
                    print("Assistant is speaking...")
                await asyncio.to_thread(audio_stream.write, data)
                if self.audio_out_queue.empty():
                    self.ai_speaking = False  # AI has finished speaking
                    print("You can speak now.")
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
                tg.create_task(self.listen_audio())
                tg.create_task(self.send_audio(session))
                tg.create_task(self.receive_audio(session))
                tg.create_task(self.play_audio())

                # Keep the main coroutine alive
                await asyncio.Event().wait()

        except asyncio.CancelledError:
            pass
        except Exception as e:
            traceback.print_exc()

    def close(self):
        """Closes PyAudio instance."""
        self.pya.terminate()
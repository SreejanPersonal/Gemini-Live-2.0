import asyncio
import base64
import io
import traceback
import cv2
import pyaudio
import PIL.Image
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

class CameraHandler:
    def __init__(self, logger):
        self.logger = logger
        self.audio_out_queue = asyncio.Queue()
        self.out_queue = asyncio.Queue(maxsize=5)
        self.ai_speaking = False
        self.client = genai.Client(http_options={"api_version": API_VERSION})
        self.CONFIG = {"generation_config": {"response_modalities": ["AUDIO"]}}
        self.pya = pyaudio.PyAudio()

    def _get_frame(self, cap):
        ret, frame = cap.read()
        if not ret:
            return None
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = PIL.Image.fromarray(frame_rgb)
        img.thumbnail([1024, 1024])
        image_io = io.BytesIO()
        img.save(image_io, format="jpeg")
        image_io.seek(0)
        mime_type = "image/jpeg"
        image_bytes = image_io.read()
        return {"mime_type": mime_type, "data": base64.b64encode(image_bytes).decode()}

    async def get_frames(self):
        cap = await asyncio.to_thread(cv2.VideoCapture, 0)
        try:
            print("Camera is on. Capturing images...")
            while True:
                frame = await asyncio.to_thread(self._get_frame, cap)
                if frame is None:
                    continue
                await self.out_queue.put(frame)
                await asyncio.sleep(1.0)  # Adjust the capture rate as needed
        except Exception as e:
            traceback.print_exc()
        finally:
            cap.release()
            print("Stopped capturing images.")

    async def send_realtime(self, session):
        try:
            while True:
                msg = await self.out_queue.get()
                await session.send(msg)
        except Exception as e:
            traceback.print_exc()

    async def listen_audio(self):
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
                    await self.out_queue.put({"data": data, "mime_type": "audio/pcm"})
                else:
                    await asyncio.sleep(0.1)
        except Exception as e:
            traceback.print_exc()
        finally:
            audio_stream.stop_stream()
            audio_stream.close()
            print("Stopped Listening.")

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
                tg.create_task(self.get_frames())
                tg.create_task(self.listen_audio())
                tg.create_task(self.send_realtime(session))
                tg.create_task(self.receive_audio(session))
                tg.create_task(self.play_audio())

                # Keep the main coroutine alive
                await asyncio.Event().wait()

        except asyncio.CancelledError:
            pass
        except Exception as e:
            traceback.print_exc()

    def close(self):
        """Closes resources."""
        self.pya.terminate()
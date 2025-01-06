import sys
import asyncio
from src.handlers.audio_handler import AudioOnlyHandler
from src.handlers.text_handler import TextOnlyHandler
from src.handlers.camera_handler import CameraHandler
from src.handlers.screen_handler import ScreenHandler
from src.config import (
    INPUT_MODE_AUDIO,
    INPUT_MODE_TEXT,
    INPUT_MODE_CAMERA,  
    INPUT_MODE_SCREEN,
)
from src.config import DEFAULT_MONITOR_INDEX 

class GeminiLiveApp:
    def __init__(
        self,
        input_mode=INPUT_MODE_TEXT,
        monitor_index=DEFAULT_MONITOR_INDEX, 
        enable_file_logging=True,
        log_level="INFO",
    ):
        self.input_mode = input_mode
        self.monitor_index = monitor_index 
        self.logger = None
        if enable_file_logging:
            from src.utils.logger import setup_logger

            self.logger = setup_logger(
                "GeminiLive",
                log_to_file=True,
                level=log_level
            )
        if self.logger:
            self.logger.info("Gemini Live Application Started.")

        if self.input_mode == INPUT_MODE_AUDIO:
            self.handler = AudioOnlyHandler(self.logger)
        elif self.input_mode == INPUT_MODE_TEXT:
            self.handler = TextOnlyHandler(self.logger)
        elif self.input_mode == INPUT_MODE_CAMERA:
            self.handler = CameraHandler(self.logger)
        elif self.input_mode == INPUT_MODE_SCREEN:
            self.handler = ScreenHandler(self.logger, self.monitor_index)  # Pass monitor_index
        else:
            if self.logger:
                self.logger.error(f"Unsupported input mode: {self.input_mode}")
            raise ValueError(f"Unsupported input mode: {self.input_mode}")

    async def run(self):
        try:
            await self.handler.run()
        except KeyboardInterrupt:
            if self.logger:
                self.logger.info("User initiated shutdown.")
            else:
                print("User initiated shutdown.")
        finally:
            self.handler.close()
            if self.logger:
                self.logger.info("Gemini Live Application Exited.")

def main(
    input_mode=INPUT_MODE_TEXT,
    monitor_index=DEFAULT_MONITOR_INDEX,
    enable_file_logging=True,
    log_level="INFO",
):
    app = GeminiLiveApp(
        input_mode=input_mode,
        monitor_index=monitor_index,
        enable_file_logging=enable_file_logging,
        log_level=log_level
    )
    asyncio.run(app.run())

if __name__ == "__main__":
    # Examples:
    # To run audio mode:
    # main(input_mode=INPUT_MODE_AUDIO)

    # To run text mode:
    # main(input_mode=INPUT_MODE_TEXT)

    # To run camera mode:
    # main(input_mode=INPUT_MODE_CAMERA)

    # To run screen mode with monitor index:
    main(input_mode=INPUT_MODE_SCREEN, monitor_index=DEFAULT_MONITOR_INDEX)
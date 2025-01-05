# main.py

import asyncio
from src.handlers.audio_handler import AudioOnlyHandler
from src.handlers.text_handler import TextOnlyHandler
from src.utils.logger import setup_logger
from src.config import INPUT_MODE_AUDIO, INPUT_MODE_TEXT

class GeminiLiveApp:
    def __init__(
        self,
        input_mode=INPUT_MODE_TEXT,
        enable_console_logging=True,
        enable_file_logging=True,
        log_level="INFO",
    ):
        self.input_mode = input_mode
        self.logger = setup_logger(
            "GeminiLive",
            log_to_console=enable_console_logging,
            log_to_file=enable_file_logging,
            level=log_level
        )
        self.logger.info("Gemini Live Application Started.")

        if self.input_mode == INPUT_MODE_AUDIO:
            self.handler = AudioOnlyHandler(self.logger)
        elif self.input_mode == INPUT_MODE_TEXT:
            self.handler = TextOnlyHandler(self.logger)
        else:
            self.logger.error(f"Unsupported input mode: {self.input_mode}")
            raise ValueError(f"Unsupported input mode: {self.input_mode}")

    async def run(self):
        try:
            await self.handler.run()
        except KeyboardInterrupt:
            self.logger.info("User initiated shutdown.")
        finally:
            self.handler.close()
            self.logger.info("Gemini Live Application Exited.")

def main(
    input_mode=INPUT_MODE_TEXT,
    enable_console_logging=True,
    enable_file_logging=True,
    log_level="INFO",
):
    app = GeminiLiveApp(
        input_mode=input_mode,
        enable_console_logging=enable_console_logging,
        enable_file_logging=enable_file_logging,
        log_level=log_level
    )
    asyncio.run(app.run())

if __name__ == "__main__":
    # Example usage:
    # To run audio mode:
    main(input_mode=INPUT_MODE_AUDIO)
    #
    # To run text mode:
    # main(input_mode=INPUT_MODE_TEXT)

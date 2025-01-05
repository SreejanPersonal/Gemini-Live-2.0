# src/config.py

import os
import pyaudio
from dotenv import load_dotenv

load_dotenv()

# API Configuration
API_VERSION = "v1alpha"
MODEL = "models/gemini-2.0-flash-exp"

# Audio Configuration
FORMAT = pyaudio.paInt16
CHANNELS = 1
SEND_SAMPLE_RATE = 16000
RECEIVE_SAMPLE_RATE = 24000
CHUNK_SIZE = 1024

# Logging Configuration
LOG_FILE_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "src/logs", "app.log")
DEFAULT_LOG_LEVEL = "INFO"

# Input Modes
INPUT_MODE_AUDIO = "audio"
INPUT_MODE_TEXT = "text"

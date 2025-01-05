# Gemini-Live-2.0

Welcome to **Gemini-Live-2.0**, a live AI assistant that enables real-time interaction through audio and text modes. This project leverages Google's Generative AI API to provide interactive sessions where users can send messages and receive responses in both audio and text formats.

This README is designed to guide beginners through the setup, installation, and usage of the project. Follow the instructions below to get started quickly.

---

## Table of Contents

- [Gemini-Live-2.0](#gemini-live-20)
  - [Table of Contents](#table-of-contents)
  - [Features](#features)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
    - [1. Clone the Repository](#1-clone-the-repository)
    - [2. Navigate to the Project Directory](#2-navigate-to-the-project-directory)
    - [3. Set Up a Virtual Environment (Optional but Recommended)](#3-set-up-a-virtual-environment-optional-but-recommended)
    - [4. Install Dependencies](#4-install-dependencies)
    - [5. Configure Environment Variables](#5-configure-environment-variables)
  - [Usage](#usage)
    - [Running in Audio Mode](#running-in-audio-mode)
    - [Running in Text Mode](#running-in-text-mode)
  - [Project Structure](#project-structure)
    - [Files and Directories](#files-and-directories)
  - [Configuration](#configuration)
  - [Logging](#logging)
  - [Troubleshooting](#troubleshooting)
  - [License](#license)

---

## Features

- **Audio Interaction**: Communicate with the AI assistant using your microphone and receive audio responses.
- **Text Interaction**: Type messages to the AI assistant and receive both text and audio responses.
- **Real-Time Processing**: Asynchronous handling for smooth and responsive interactions.
- **Customizable Settings**: Modifiable configurations for audio settings, logging, and input modes.
- **Logging**: Detailed logs to monitor the application's behavior and troubleshoot issues.

---

## Prerequisites

Before you begin, ensure you have met the following requirements:

- **Operating System**: Windows, macOS, or Linux
- **Python Version**: Python 3.8 or higher
- **Internet Connection**: Required for connecting to the AI API
- **Microphone**: For audio mode interactions
- **Environment Variables**: Google API key and any other necessary credentials

---

## Installation

Follow these steps to set up the project on your local machine.

### 1. Clone the Repository

```bash
git clone https://github.com/SreejanPersonal/Gemini-Live-2.0.git
```

### 2. Navigate to the Project Directory

```bash
cd Gemini-Live-2.0
```

### 3. Set Up a Virtual Environment (Optional but Recommended)

Create a virtual environment to manage project dependencies.

```bash
# On Windows
python -m venv venv
venv\Scripts\activate

# On macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 4. Install Dependencies

Install the required Python packages using `pip`.

```bash
pip install -r requirements.txt
```

### 5. Configure Environment Variables

Create a `.env` file in the root directory to store your environment variables.

```bash
copy .env.example .env  # On Windows
cp .env.example .env    # On macOS/Linux
```

Open the `.env` file and add your Google API key:

```
GOOGLE_API_KEY=your_google_api_key_here
```

> **Important**: Keep your API keys secure and do not share them publicly.

---

## Usage

You can run the application in either **Audio Mode** or **Text Mode**.

### Running in Audio Mode

In Audio Mode, you can speak to the AI assistant using your microphone and hear its responses.

```bash
python main.py
```

By default, the application runs in Audio Mode. If you want to be explicit:

```bash
python main.py --input_mode audio
```

### Running in Text Mode

In Text Mode, you can type messages to the AI assistant and receive both text and audio responses.

```bash
python main.py --input_mode text
```

---

## Project Structure

The project has the following structure:

```
Gemini-Live-2.0/
├── .env.example
├── .gitignore
├── main.py
├── requirements.txt
├── src/
│   ├── config.py
│   ├── handlers/
│   │   ├── audio_handler.py
│   │   └── text_handler.py
│   ├── logs/
│   │   └── app.log
│   └── utils/
│       └── logger.py
```

### Files and Directories

- **.env.example**: Example of the environment variables file. Copy this to `.env` and replace placeholders with actual values.
- **.gitignore**: Specifies intentionally untracked files to ignore.
- **main.py**: The main entry point of the application.
- **requirements.txt**: Lists all Python dependencies required by the project.
- **src/**: Contains all the source code modules.
  - **config.py**: Configuration settings for the application.
  - **handlers/**: Module containing the interaction handlers.
    - **audio_handler.py**: Handles audio input/output interactions.
    - **text_handler.py**: Handles text input/output interactions.
  - **logs/**: Directory where log files are stored.
    - **app.log**: Log file capturing application runtime logs.
  - **utils/**: Utility modules.
    - **logger.py**: Sets up and configures logging for the application.

---

## Configuration

You can adjust application settings by modifying the `src/config.py` file or setting environment variables.

Key configurations include:

- **API Configuration**:
  - `API_VERSION`: The version of the API to use (default is `"v1alpha"`).
  - `MODEL`: The AI model to use (e.g., `"models/gemini-2.0-flash-exp"`).
- **Audio Configuration**:
  - `FORMAT`: Audio format used by PyAudio.
  - `CHANNELS`: Number of audio channels.
  - `SEND_SAMPLE_RATE`: Sample rate for sending audio data.
  - `RECEIVE_SAMPLE_RATE`: Sample rate for receiving audio data.
  - `CHUNK_SIZE`: Buffer size for audio streams.
- **Logging Configuration**:
  - `LOG_FILE_PATH`: File path for the application log.
  - `DEFAULT_LOG_LEVEL`: Default logging level (e.g., `"INFO"`).
- **Input Modes**:
  - `INPUT_MODE_AUDIO`: Constant for audio mode.
  - `INPUT_MODE_TEXT`: Constant for text mode.

---

## Logging

The application logs important events and errors to help you understand its behavior.

- **Console Logging**: Logs are output to the console with colored formatting for readability.
- **File Logging**: Logs are also saved to `src/logs/app.log`.

You can configure logging preferences in the `setup_logger` function in `src/utils/logger.py`.

---

## Troubleshooting

- **Microphone or Audio Issues**:
  - Ensure your microphone and speakers are properly connected and configured.
  - Check that your system's audio settings allow applications to access the microphone.
- **Dependencies Not Found**:
  - Verify that all dependencies are installed using `pip install -r requirements.txt`.
  - If you encounter errors with `pyaudio`, you may need to install additional system packages.
    - On Windows, install the appropriate PyAudio wheel file from [here](https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio).
    - On macOS, you may need to install PortAudio using Homebrew: `brew install portaudio`.
- **API Key Issues**:
  - Ensure that your `GOOGLE_API_KEY` is valid and has the necessary permissions.
  - Double-check that your `.env` file is correctly set up.

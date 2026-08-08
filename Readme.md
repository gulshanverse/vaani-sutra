# Vaani Sutra — वाणी सूत्र

**Where Intelligence Finds Its Voice.**

Vaani Sutra is a real-time AI voice support agent designed to connect customer conversations to Google Gemini Realtime through VideoSDK agents. It is built for multilingual customer support, voice-based interaction, and a production-ready environment with secure configuration handling.

## What is Vaani Sutra?

Vaani Sutra combines:
- Voice-first customer support via VideoSDK
- Google Gemini Realtime for AI responses
- Secure environment configuration via `python-dotenv`
- Structured voice agent startup and graceful shutdown

"Vaani" means voice, speech, or expression. "Sutra" means connection, thread, or guiding principle. Together, Vaani Sutra is the voice connection layer for real-time AI support.

## Architecture

- `main.py` — application entrypoint and VideoSDK job startup
- `config/settings.py` — environment loading and credential validation
- `utils/logging_setup.py` — structured logging and optional file logging
- `run_and_watch.py` — helper watcher to restart the agent when credentials become available

## Features

- Real-time voice agent implementation using VideoSDK
- Gemini Realtime audio model integration
- Secure credentials validation and startup failure handling
- Graceful shutdown on keyboard interrupt or startup error
- Unit tests for config and startup behavior

## Technology Stack

- Python 3.12
- VideoSDK Agents
- Google Gemini Realtime
- python-dotenv
- pytest for unit testing

## Installation

1. Create a fresh Python 3.12 virtual environment:

```powershell
py -3.12 -m venv .venv
```

2. Activate the environment:

```powershell
.\.venv\Scripts\Activate.ps1
```

3. Upgrade pip and install dependencies:

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## Environment Variables

Copy `.env.example` to `.env` and replace placeholder values:

```env
GOOGLE_API_KEY=your_google_api_key_here
VIDEOSDK_AUTH_TOKEN=your_videosdk_auth_token_here
VIDEOSDK_API_KEY=your_videosdk_api_key_here
VIDEOSDK_SECRET_KEY=your_videosdk_secret_key_here
```

The application checks required credentials at startup and exits cleanly if missing.

## Running Locally

Once credentials are available:

```powershell
python main.py
```

Use the watcher when credentials may become available later:

```powershell
python run_and_watch.py
```

## Testing

Run unit tests with pytest:

```powershell
python -m pytest
```

## Project Structure

```text
AI-Voice-Support-Agent/
├── config/
│   └── settings.py
├── tests/
│   ├── test_config.py
│   └── test_main.py
├── utils/
│   └── logging_setup.py
├── main.py
├── run_and_watch.py
├── requirements.txt
├── requirements-lock.txt
├── .env.example
├── .gitignore
└── README.md
```

## Security

- `.env` is excluded from Git via `.gitignore`
- Secrets are validated at startup, not logged
- `.env.example` contains placeholders only
- The repository has no committed `.env` file or API keys

## Troubleshooting

- `ERROR: GOOGLE_API_KEY is not configured.` — ensure `.env` or the environment provides the key
- `No VideoSDK auth available.` — set `VIDEOSDK_AUTH_TOKEN`, or `VIDEOSDK_API_KEY` and `VIDEOSDK_SECRET_KEY`
- If startup fails due to dependency errors, confirm the virtual environment is Python 3.12 and dependencies are installed from `requirements.txt`

## Future Roadmap

- Add structured conversation state and intent handling
- Support additional Gemini voice models and languages
- Add integration test suite for VideoSDK + Gemini runtime
- Improve logging to include request IDs and observability

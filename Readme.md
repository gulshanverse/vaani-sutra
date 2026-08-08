# GODIMS AI Voice Support Agent (demo)

This repository contains a demo AI voice support agent. To make the project runnable
without external binary dependencies during development, the `videosdk` interfaces
are provided as local stubs. The agent can run in an offline/demo mode or be
extended to integrate with real VideoSDK and Gemini Realtime APIs.

---

## Features

- Real-time AI voice conversation
- English & Hindi language support
- Professional, human-like customer support
- Service and pricing information on demand
- Automated lead collection (Name, Email, Phone, Budget, Service)
- Automatic call greeting and closing

---

## Tech Stack

| Component | Technology |
|---|---|
| Language | Python 3.11+ |
| Voice Agent Framework | VideoSDK Agents |
| AI Model | Google Gemini Realtime API |
| Concurrency | AsyncIO |
| Config Management | python-dotenv |

---

## Project Structure

```text
godims-voice-agent/
├── main.py
├── .env
├── requirements.txt
└── README.md
```

---

## Environment Variables

Create a `.env` file in the project root:

```env
GOOGLE_API_KEY=YOUR_GEMINI_API_KEY
```

---

## Dependencies

`requirements.txt` (pinned):

```txt
python-dotenv==1.0.0
```

---

## Setup Guide

### 1. Create a Virtual Environment

**Windows**
```bash
python -m venv .venv
```

**macOS / Linux**
```bash
python3 -m venv .venv
```

### 2. Activate the Virtual Environment

**Windows**
```bash
.venv\Scripts\activate
```

**macOS / Linux**
```bash
source .venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the Agent

Provide credentials in `.env` (or environment):

```
VIDEOSDK_AUTH_TOKEN=YOUR_VIDEOSDK_AUTH_TOKEN
GOOGLE_API_KEY=YOUR_GOOGLE_GEMINI_API_KEY
```

Start the agent watcher which will wait for credentials and launch automatically:

```bash
python run_and_watch.py
```

Or run directly once credentials are present:

```bash
python main.py
```

**macOS / Linux**
```bash
python3 main.py
```

---

## Workflow

```text
Customer Call
      │
      ▼
VideoSDK Agent
      │
      ▼
Gemini Realtime API
      │
      ▼
Voice Response
      │
      ▼
Customer Support
      │
      ▼
Lead Collection
```

---

## Agent Responsibilities

1. Greet customers professionally
2. Ask for preferred language (English / Hindi)
3. Explain GODIMS services
4. Share pricing and project timelines
5. Collect customer requirements and contact details
6. End the call politely

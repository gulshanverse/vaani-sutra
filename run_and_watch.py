"""Watch for credentials in the environment or .env and run `main.py` when available.

Usage: python run_and_watch.py

This helper polls for required credentials and launches the agent automatically
once both VideoSDK and GOOGLE_API_KEY are provided. It prints logs to the console
and restarts the process if it exits with an error.
"""
import time
import subprocess
import os
import sys
from config.settings import get_videosdk_auth, validate_google_api_key


def creds_present():
    try:
        validate_google_api_key(required=True)
    except Exception:
        return False
    if not get_videosdk_auth():
        return False
    return True


def main():
    poll_interval = int(os.getenv("CREDENTIALS_POLL_INTERVAL", "5"))
    print("Waiting for credentials (.env or environment)...")
    while not creds_present():
        print("Credentials not found. Ensure GOOGLE_API_KEY and VideoSDK auth are set.")
        time.sleep(poll_interval)

    print("Credentials found — launching agent")
    while True:
        proc = subprocess.Popen([sys.executable, "main.py"], cwd=os.path.dirname(__file__))
        proc.wait()
        rc = proc.returncode
        print(f"Agent exited with code {rc}")
        if rc == 0:
            print("Agent exited cleanly. Stopping watcher.")
            break
        print("Restarting agent in 3 seconds...")
        time.sleep(3)


if __name__ == "__main__":
    main()

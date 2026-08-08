import os
import logging

logger = logging.getLogger(__name__)

try:
    from videosdk.agents.utils import resolve_videosdk_auth_token
except Exception:
    resolve_videosdk_auth_token = None

# Make .env optional: try to load if python-dotenv is available
try:
    from dotenv import load_dotenv

    load_dotenv()
    logger.debug("Loaded .env using python-dotenv")
except Exception:
    logger.debug("python-dotenv not available; skipping .env load")


def get_env(key: str, required: bool = False, default=None):
    val = os.getenv(key, default)
    if required and not val:
        logger.error("Missing required environment variable: %s", key)
        raise RuntimeError(f"Missing required environment variable: {key}")
    return val


def validate_google_api_key(required: bool = True):
    """Validate presence and basic format of the Google Gemini API key.

    If `required` is True, raises RuntimeError when key is missing or invalid.
    Returns the key when present.
    """
    key = get_env("GOOGLE_API_KEY", required=False)
    if not key:
        msg = "GOOGLE_API_KEY not set. Please set GOOGLE_API_KEY in your environment or .env file."
        if required:
            logger.error(msg)
            raise RuntimeError(msg)
        logger.warning(msg)
        return None

    # Basic sanity check
    if len(key) < 10:
        msg = "GOOGLE_API_KEY looks invalid (too short)"
        logger.error(msg)
        raise RuntimeError(msg)
    return key


def get_videosdk_auth():
    """Return VideoSDK auth token resolved from environment or None.

    Checks `VIDEOSDK_AUTH_TOKEN` first, then `VIDEOSDK_API_KEY` + `VIDEOSDK_SECRET_KEY`
    using the installed VideoSDK token resolver when available.
    """
    token = os.getenv("VIDEOSDK_AUTH_TOKEN")
    if token and token.strip():
        return token.strip()

    if resolve_videosdk_auth_token is not None:
        return resolve_videosdk_auth_token()

    api_key = os.getenv("VIDEOSDK_API_KEY")
    secret = os.getenv("VIDEOSDK_SECRET_KEY")
    if api_key and secret:
        return f"{api_key}:{secret}"
    return None


def ensure_credentials_or_raise():
    """Ensure both VideoSDK and Google API credentials are present, else raise.

    This is intended to be called at startup to fail fast when required credentials
    are missing so the operator can provide them.
    """
    google_key = validate_google_api_key(required=True)
    vsdk = get_videosdk_auth()
    if not vsdk:
        msg = (
            "No VideoSDK auth available. Provide VIDEOSDK_AUTH_TOKEN, or VIDEOSDK_API_KEY and VIDEOSDK_SECRET_KEY."
        )
        logger.error(msg)
        raise RuntimeError(msg)
    return google_key, vsdk

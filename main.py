import traceback
import logging
import asyncio

from videosdk.agents import (
    Agent,
    AgentSession,
    Pipeline,
    JobContext,
    RoomOptions,
    WorkerJob,
    Options,
)

from videosdk.agents._plugins import (
    GeminiRealtime,
    GeminiLiveConfig,
)

from config.settings import validate_google_api_key, get_videosdk_auth, ensure_credentials_or_raise
from utils.logging_setup import configure_logging

configure_logging()
logger = logging.getLogger(__name__)


class MyVoiceAgent(Agent):
    def __init__(self):
        super().__init__(
            instructions=(
                "You are Varsha, a professional customer support executive from GODIMS."
            )
        )

    async def on_enter(self):
        # For demo/offline mode we just log the greeting
        logger.info("Agent greeting: Hello Sir! I am Varsha from GODIMS. How can I help you today?")

    async def on_exit(self):
        logger.info("Agent farewell: Thank you for contacting GODIMS. Have a wonderful day!")


async def start_session(context: JobContext):
    # Validate API key and fail-fast if missing
    api_key = validate_google_api_key(required=True)

    # Resolve VideoSDK auth (JobContext will also validate when connecting)
    vsdk_auth = get_videosdk_auth()
    if not vsdk_auth:
        logger.error("VideoSDK auth not found. Set VIDEOSDK_AUTH_TOKEN or VIDEOSDK_API_KEY+VIDEOSDK_SECRET_KEY.")
        raise RuntimeError("Missing VideoSDK credentials")

    model = GeminiRealtime(
        model="gemini-3.1-flash-live-preview",
        api_key=api_key,
        config=GeminiLiveConfig(
            voice="Leda",
            response_modalities=["AUDIO"],
        ),
    )

    pipeline = Pipeline(llm=model)

    session = AgentSession(agent=MyVoiceAgent(), pipeline=pipeline)

    await session.start(wait_for_participant=True, run_until_shutdown=True)


def make_context():
    return JobContext(room_options=RoomOptions())


def main():
    options = Options(agent_id="GodimsSupportAgent", register=True, max_processes=10, host="localhost", port=8081)
    job = WorkerJob(entrypoint=start_session, jobctx=make_context, options=options)

    logger.info("Starting GODIMS Voice Agent...")
    try:
        # Ensure there is a running event loop available for libraries that
        # call asyncio.get_event_loop() during synchronous setup (Python 3.14+).
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

            job.start()
    except KeyboardInterrupt:
        logger.info("Shutting down due to keyboard interrupt")
    except Exception:
        logger.error("Unhandled exception during startup:")
        traceback.print_exc()


if __name__ == "__main__":
    main()
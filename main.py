import asyncio
import logging
from dataclasses import dataclass
from typing import Optional

from videosdk.agents import (
    Agent,
    AgentSession,
    Pipeline,
    JobContext,
    RoomOptions,
    WorkerJob,
    Options,
)
from videosdk.agents._plugins import GeminiRealtime, GeminiLiveConfig

from config.settings import ensure_credentials_or_raise
from utils.logging_setup import configure_logging

configure_logging()
logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class RuntimeConfig:
    google_api_key: str


runtime_config: Optional[RuntimeConfig] = None


class VaaniSutraAgent(Agent):
    def __init__(self) -> None:
        super().__init__(
            instructions=(
                "You are Varsha, a professional customer support executive for Vaani Sutra."
            )
        )

    async def on_enter(self) -> None:
        logger.info(
            "Agent greeting: Hello! I am Varsha from Vaani Sutra. How can I support you today?"
        )

    async def on_exit(self) -> None:
        logger.info(
            "Agent farewell: Thank you for contacting Vaani Sutra. Have a wonderful day!"
        )


async def start_session(context: JobContext) -> None:
    if runtime_config is None:
        raise RuntimeError("Runtime configuration is not initialized")

    model = GeminiRealtime(
        model="gemini-3.1-flash-live-preview",
        api_key=runtime_config.google_api_key,
        config=GeminiLiveConfig(
            voice="Leda",
            response_modalities=["AUDIO"],
        ),
    )

    pipeline = Pipeline(llm=model)
    session = AgentSession(agent=VaaniSutraAgent(), pipeline=pipeline)

    await session.start(wait_for_participant=True, run_until_shutdown=True)


def make_context() -> JobContext:
    return JobContext(room_options=RoomOptions())


def build_worker_job() -> WorkerJob:
    return WorkerJob(
        entrypoint=start_session,
        jobctx=make_context,
        options=Options(
            agent_id="VaaniSutraSupportAgent",
            register=True,
            max_processes=10,
            host="localhost",
            port=8081,
        ),
    )


def main() -> int:
    global runtime_config

    try:
        google_api_key, _ = ensure_credentials_or_raise()
        runtime_config = RuntimeConfig(google_api_key=google_api_key)

        logger.info("Starting Vaani Sutra Voice Agent...")
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        job = build_worker_job()
        job.start()
        return 0
    except KeyboardInterrupt:
        logger.info("Shutting down due to keyboard interrupt")
        return 0
    except Exception as error:
        logger.error("Startup failed: %s", error)
        return 1
    finally:
        try:
            if loop is not None and not loop.is_closed():
                loop.close()
        except Exception:
            pass


if __name__ == "__main__":
    raise SystemExit(main())

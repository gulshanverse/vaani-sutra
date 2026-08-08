import os
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
    videosdk_auth: str
    playground: bool = False


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
    if runtime_config is None:
        raise RuntimeError("Runtime configuration is not initialized")

    ro = RoomOptions(
        auth_token=runtime_config.videosdk_auth,
        playground=runtime_config.playground,
        join_meeting=True,
    )
    return JobContext(room_options=ro)


def build_worker_job() -> WorkerJob:
    if runtime_config is None:
        raise RuntimeError("Runtime configuration is not initialized")

    return WorkerJob(
        entrypoint=start_session,
        jobctx=make_context,
        options=Options(
            agent_id="VaaniSutraSupportAgent",
            register=not runtime_config.playground,
            max_processes=10,
            host="localhost",
            port=8081,
            auth_token=runtime_config.videosdk_auth,
        ),
    )


def _parse_truthy(env_val: Optional[str]) -> bool:
    if not env_val:
        return False
    return env_val.strip().lower() in ("1", "true", "yes", "on")


def main() -> int:
    global runtime_config

    try:
        google_api_key, vsdk_auth = ensure_credentials_or_raise()
        playground_flag = _parse_truthy(os.getenv("VAANI_SUTRA_PLAYGROUND", "false"))

        runtime_config = RuntimeConfig(
            google_api_key=google_api_key,
            videosdk_auth=vsdk_auth,
            playground=playground_flag,
        )

        if playground_flag:
            logger.info("========================================")
            logger.info("VAANI SUTRA LOCAL VOICE TEST")
            logger.info("========================================")
            logger.info("Playground mode enabled. Starting local browser test flow.")

        logger.info("Starting Vaani Sutra Voice Agent... (playground=%s)", playground_flag)
        logger.info(
            "Worker execution mode: %s",
            "direct playground" if playground_flag else "backend registration",
        )

        job = build_worker_job()
        job.start()
        return 0
    except KeyboardInterrupt:
        logger.info("Shutting down due to keyboard interrupt")
        return 0
    except Exception as error:
        logger.error("Startup failed: %s", error)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

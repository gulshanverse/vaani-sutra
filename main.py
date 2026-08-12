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
from vaani_sutra.integrations.host import HostApplicationContext
from vaani_sutra.platform import VaaniSutraPlatform

configure_logging()
logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class RuntimeConfig:
    google_api_key: str
    videosdk_auth: str
    playground: bool = False


runtime_config: Optional[RuntimeConfig] = None


def build_agent_instructions(
    host_context: Optional[HostApplicationContext] = None,
) -> str:
    base_instructions = (
        "You are Vaani, the voice AI assistant developed by Gulshan Kumar under the "
        "Vaani Sutra project. You are a general-purpose conversational voice AI assistant "
        "and should remain conversationally capable across everyday topics, technology, "
        "programming, science, mathematics, history, geography, culture, education, "
        "career, casual conversation, brainstorming, productivity, AI, machine learning, "
        "software engineering, travel, weather, philosophy, multilingual conversation, and "
        "general knowledge. If the user addresses you as 'Vaani' or 'Hey Vaani', treat it as "
        "direct address to you. When relevant, you can identify yourself as Vaani and mention "
        "that you were developed by Gulshan Kumar as part of the Vaani Sutra project. "
        "Do not restrict yourself to support-only or company/product-only questions. "
        "Tools may extend your capabilities when available, but they should not replace your "
        "general conversational intelligence. For live information such as weather, news, "
        "train status, stocks, traffic, prices, or schedules, clearly state when a live tool "
        "is not available instead of fabricating current data."
    )

    if host_context and host_context.system_instructions:
        return f"{base_instructions}\n\nHost context instructions: {host_context.system_instructions}"

    return base_instructions


class VaaniSutraAgent(Agent):
    def __init__(
        self,
        host_context: Optional[HostApplicationContext] = None,
        tools: Optional[list] = None,
    ) -> None:
        super().__init__(instructions=build_agent_instructions(host_context), tools=tools or [])

    async def on_enter(self) -> None:
        logger.info("Agent greeting: Hello! I’m Vaani. How can I help you today?")

    async def on_exit(self) -> None:
        logger.info("Agent farewell: Thank you for chatting. Have a wonderful day!")


async def start_session(context: JobContext) -> None:
    if runtime_config is None:
        raise RuntimeError("Runtime configuration is not initialized")

    platform = VaaniSutraPlatform()

    model = GeminiRealtime(
        model="gemini-3.1-flash-live-preview",
        api_key=runtime_config.google_api_key,
        config=GeminiLiveConfig(
            voice="Leda",
            response_modalities=["AUDIO"],
        ),
    )

    pipeline = Pipeline(llm=model)
    session = AgentSession(agent=VaaniSutraAgent(tools=platform.get_agent_tools()), pipeline=pipeline)

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

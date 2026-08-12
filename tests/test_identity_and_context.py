from main import VaaniSutraAgent, build_agent_instructions
from vaani_sutra.integrations.host import HostApplicationContext


def test_vaani_identity_prompt_mentions_vaani_and_developer():
    prompt = build_agent_instructions()

    assert "Vaani" in prompt
    assert "Gulshan Kumar" in prompt
    assert "Vaani Sutra" in prompt
    assert "general-purpose conversational voice ai assistant" in prompt.lower()


def test_agent_uses_general_purpose_instructions_by_default():
    agent = VaaniSutraAgent()

    assert "general-purpose" in agent.instructions.lower()
    assert "customer support" not in agent.instructions.lower()
    assert "only talk about" not in agent.instructions.lower()


def test_host_context_does_not_enable_company_restrictions_by_default():
    host_context = HostApplicationContext(
        application_id="rail-yatra",
        application_name="RailYatra",
        user_id="user_001",
        locale="en-IN",
    )

    prompt = build_agent_instructions(host_context=host_context)

    assert "general-purpose" in prompt.lower()
    assert "customer support" not in prompt.lower()
    assert "only discuss" not in prompt.lower()
    assert "rail-yatra" not in prompt.lower()

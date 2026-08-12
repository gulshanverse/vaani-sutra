import pytest

from vaani_sutra.memory.manager import MemoryManager
from vaani_sutra.memory.models import MemoryCategory, MemoryScope
from vaani_sutra.memory.policy import MemoryPolicy
from vaani_sutra.memory.store import SQLiteMemoryStore
from vaani_sutra.tools.builtin.memory_tools import ForgetTool, ListMemoriesTool, RecallTool, RememberTool


@pytest.fixture
def memory_manager(tmp_path):
    db_path = tmp_path / "memory.sqlite3"
    return MemoryManager(store=SQLiteMemoryStore(db_path=str(db_path)))


def test_memory_create_retrieve_update_delete_list(memory_manager):
    created = memory_manager.remember(
        application_id="rail-yatra",
        user_id="user_123",
        key="preferred_language",
        value="Hindi",
        category=MemoryCategory.PREFERENCE,
    )

    assert created is not None

    recalled = memory_manager.recall(
        application_id="rail-yatra",
        user_id="user_123",
        key="preferred_language",
    )
    assert recalled is not None
    assert recalled.value == "Hindi"

    updated = memory_manager.remember(
        application_id="rail-yatra",
        user_id="user_123",
        key="preferred_language",
        value="English",
        category=MemoryCategory.PREFERENCE,
    )
    assert updated is not None

    recalled_after_update = memory_manager.recall(
        application_id="rail-yatra",
        user_id="user_123",
        key="preferred_language",
    )
    assert recalled_after_update is not None
    assert recalled_after_update.value == "English"

    memories = memory_manager.list_memories(application_id="rail-yatra", user_id="user_123")
    assert len(memories) == 1

    removed = memory_manager.forget(application_id="rail-yatra", user_id="user_123", key="preferred_language")
    assert removed is True
    assert memory_manager.recall(application_id="rail-yatra", user_id="user_123", key="preferred_language") is None


def test_memory_isolation_by_application_user_and_session(memory_manager):
    memory_manager.remember(
        application_id="rail-yatra",
        user_id="user_123",
        key="name",
        value="Gulshan",
        category=MemoryCategory.PROFILE,
    )
    memory_manager.remember(
        application_id="rail-yatra",
        user_id="user_456",
        key="name",
        value="Rahul",
        category=MemoryCategory.PROFILE,
    )
    memory_manager.remember(
        application_id="hospital-assist",
        user_id="user_123",
        key="name",
        value="Asha",
        category=MemoryCategory.PROFILE,
    )
    memory_manager.remember(
        application_id="rail-yatra",
        user_id="user_123",
        key="session_note",
        value="temporary",
        category=MemoryCategory.CONTEXT,
        scope=MemoryScope.SESSION,
        session_id="session-1",
    )

    assert memory_manager.recall(application_id="rail-yatra", user_id="user_123", key="name").value == "Gulshan"
    assert memory_manager.recall(application_id="rail-yatra", user_id="user_456", key="name").value == "Rahul"
    assert memory_manager.recall(application_id="hospital-assist", user_id="user_123", key="name").value == "Asha"
    assert memory_manager.recall(
        application_id="rail-yatra",
        user_id="user_123",
        key="session_note",
        session_id="session-1",
    ).value == "temporary"
    assert memory_manager.recall(
        application_id="rail-yatra",
        user_id="user_123",
        key="session_note",
        session_id="session-2",
    ) is None


def test_memory_policy_rejects_sensitive_data():
    policy = MemoryPolicy()
    assert policy.allow_memory(key="favorite_color", value="blue", category=MemoryCategory.PREFERENCE) is True
    assert policy.allow_memory(key="password", value="secret", category=MemoryCategory.PROFILE) is False
    assert policy.allow_memory(key="api_key", value="abc123", category=MemoryCategory.PROFILE) is False
    assert policy.allow_memory(key="note", value="contains refresh_token here", category=MemoryCategory.OTHER) is False


def test_memory_tools_execute_and_list(memory_manager):
    remember_tool = RememberTool(manager=memory_manager)
    recall_tool = RecallTool(manager=memory_manager)
    forget_tool = ForgetTool(manager=memory_manager)
    list_tool = ListMemoriesTool(manager=memory_manager)

    remember_result = remember_tool.execute(
        {
            "application_id": "rail-yatra",
            "user_id": "user_123",
            "key": "preferred_language",
            "value": "Hindi",
            "category": "PREFERENCE",
        }
    )
    assert remember_result["success"] is True

    recall_result = recall_tool.execute(
        {
            "application_id": "rail-yatra",
            "user_id": "user_123",
            "key": "preferred_language",
        }
    )
    assert recall_result["found"] is True
    assert recall_result["value"] == "Hindi"

    list_result = list_tool.execute(
        {
            "application_id": "rail-yatra",
            "user_id": "user_123",
            "limit": 10,
        }
    )
    assert list_result["items"]

    forget_result = forget_tool.execute(
        {
            "application_id": "rail-yatra",
            "user_id": "user_123",
            "key": "preferred_language",
        }
    )
    assert forget_result["removed"] is True


def test_empty_memory_handling(memory_manager):
    assert memory_manager.list_memories(application_id="rail-yatra", user_id="missing") == []
    assert memory_manager.recall(application_id="rail-yatra", user_id="missing", key="name") is None

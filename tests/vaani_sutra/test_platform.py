from vaani_sutra.platform import VaaniSutraPlatform


def test_platform_registers_builtin_capabilities(monkeypatch, tmp_path):
    class TempSQLiteMemoryStore:
        def __init__(self):
            from vaani_sutra.memory.store import SQLiteMemoryStore

            self._delegate = SQLiteMemoryStore(db_path=str(tmp_path / "memory.sqlite3"))

        def __getattr__(self, item):
            return getattr(self._delegate, item)

    import vaani_sutra.platform as platform_module

    monkeypatch.setattr(platform_module, "SQLiteMemoryStore", TempSQLiteMemoryStore)

    platform = VaaniSutraPlatform()
    tool_names = set(platform.get_registry().list_tool_names())

    assert {"calculator", "datetime", "domain_lookup", "weather", "web_search", "remember", "recall", "forget", "list_memories"}.issubset(tool_names)

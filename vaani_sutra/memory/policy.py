from __future__ import annotations

from .models import MemoryCategory


class MemoryPolicy:
    SENSITIVE_KEYS = {
        "password",
        "passwd",
        "api_key",
        "apikey",
        "token",
        "access_token",
        "refresh_token",
        "secret",
        "private_key",
        "cookie",
        "authorization",
        "system_prompt",
        "system-instruction",
    }

    def allow_memory(self, *, key: str, value: str | None, category: MemoryCategory) -> bool:
        if not key or not isinstance(key, str):
            return False
        normalized_key = key.lower()
        if any(secret_key in normalized_key for secret_key in self.SENSITIVE_KEYS):
            return False
        if value is None:
            return False
        normalized_value = str(value).strip().lower()
        if any(secret_key in normalized_value for secret_key in self.SENSITIVE_KEYS):
            return False
        if category == MemoryCategory.OTHER and not str(value).strip():
            return False
        return True

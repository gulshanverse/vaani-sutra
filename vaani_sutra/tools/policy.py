from __future__ import annotations

from enum import Enum


class ToolRiskLevel(str, Enum):
    READ_ONLY = "READ_ONLY"
    CONFIRMATION_REQUIRED = "CONFIRMATION_REQUIRED"
    BLOCKED = "BLOCKED"


class ToolPolicy:
    @staticmethod
    def is_execution_allowed(risk_level: ToolRiskLevel, confirmed: bool = False) -> bool:
        if risk_level == ToolRiskLevel.BLOCKED:
            return False
        if risk_level == ToolRiskLevel.CONFIRMATION_REQUIRED:
            return confirmed
        return True

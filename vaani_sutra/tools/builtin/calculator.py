from __future__ import annotations

import ast
import operator
from typing import Any

from ..base import Tool, ToolInputSchema, ToolMetadata

_ALLOWED_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
    ast.Mod: operator.mod,
}


class CalculatorTool(Tool):
    def __init__(self):
        metadata = ToolMetadata(
            name="calculator",
            description="Performs safe arithmetic calculations without arbitrary code execution.",
            timeout_seconds=2.0,
            risk_level="READ_ONLY",
            requires_confirmation=False,
        )
        input_schema = {
            "expression": ToolInputSchema(
                type="string",
                description="Arithmetic expression to evaluate.",
                required=True,
            )
        }
        super().__init__(metadata=metadata, input_schema=input_schema)

    def execute(self, arguments: dict[str, Any]) -> Any:
        expression = arguments.get("expression")
        if not isinstance(expression, str):
            raise ValueError("expression must be a string")
        node = ast.parse(expression, mode="eval")
        return self._evaluate(node.body)

    def _evaluate(self, node: ast.AST) -> float:
        if isinstance(node, ast.BinOp):
            left = self._evaluate(node.left)
            right = self._evaluate(node.right)
            op_type = type(node.op)
            if op_type not in _ALLOWED_OPERATORS:
                raise ValueError(f"Operator not supported: {op_type.__name__}")
            return _ALLOWED_OPERATORS[op_type](left, right)
        if isinstance(node, ast.UnaryOp):
            operand = self._evaluate(node.operand)
            op_type = type(node.op)
            if op_type not in _ALLOWED_OPERATORS:
                raise ValueError(f"Operator not supported: {op_type.__name__}")
            return _ALLOWED_OPERATORS[op_type](operand)
        if isinstance(node, ast.Constant):
            if isinstance(node.value, (int, float)):
                return float(node.value)
            raise ValueError("Only numeric constants are allowed")
        raise ValueError(f"Unsupported expression element: {type(node).__name__}")

"""Calculator tool for mathematical operations."""
import math
import re
from typing import Any


async def calculate_tool(expression: str) -> dict[str, Any]:
    """
    Perform mathematical calculations.

    Args:
        expression: Mathematical expression to evaluate

    Returns:
        Dictionary with result and metadata
    """
    try:
        # Sanitize expression - only allow safe mathematical operations
        # Remove any potentially dangerous characters
        safe_expr = re.sub(r'[^0-9+\-*/().%\s]', '', expression)

        # Create safe namespace with math functions
        safe_dict = {
            "abs": abs,
            "round": round,
            "min": min,
            "max": max,
            "sum": sum,
            "pow": pow,
            "sqrt": math.sqrt,
            "sin": math.sin,
            "cos": math.cos,
            "tan": math.tan,
            "log": math.log,
            "pi": math.pi,
            "e": math.e,
        }

        # Evaluate expression
        result = eval(safe_expr, {"__builtins__": {}}, safe_dict)

        return {
            "expression": expression,
            "result": result,
            "success": True,
            "error": None,
        }

    except Exception as e:
        return {
            "expression": expression,
            "result": None,
            "success": False,
            "error": str(e),
        }

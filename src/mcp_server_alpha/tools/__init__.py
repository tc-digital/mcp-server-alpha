"""MCP tools for the server."""
from .eligibility import check_eligibility_tool
from .enrollment import initiate_enrollment_tool
from .products import get_cross_sell_products_tool, search_products_tool
from .quotes import generate_quote_tool

__all__ = [
    "check_eligibility_tool",
    "initiate_enrollment_tool",
    "get_cross_sell_products_tool",
    "search_products_tool",
    "generate_quote_tool",
]

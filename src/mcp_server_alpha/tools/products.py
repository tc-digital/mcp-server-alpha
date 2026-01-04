"""Product search and discovery tools."""
from typing import Any

from ..config import ProductRegistry


async def search_products_tool(
    registry: ProductRegistry,
    category: str | None = None,
    provider_id: str | None = None,
    active_only: bool = True,
) -> list[dict[str, Any]]:
    """
    Search for insurance products.

    Args:
        registry: Product registry
        category: Filter by category (health, dental, vision, life, etc.)
        provider_id: Filter by provider/carrier ID
        active_only: Only return active products

    Returns:
        List of product summaries
    """
    products = registry.list_products(
        category=category, provider_id=provider_id, active_only=active_only
    )

    return [
        {
            "id": p.id,
            "name": p.name,
            "category": p.category,
            "provider_id": p.provider_id,
            "description": p.description,
            "active": p.active,
        }
        for p in products
    ]


async def get_cross_sell_products_tool(
    registry: ProductRegistry, product_id: str
) -> list[dict[str, Any]]:
    """
    Get cross-sell product recommendations.

    Args:
        registry: Product registry
        product_id: Current product ID

    Returns:
        List of compatible cross-sell products
    """
    products = registry.get_cross_sell_products(product_id)

    return [
        {
            "id": p.id,
            "name": p.name,
            "category": p.category,
            "provider_id": p.provider_id,
            "description": p.description,
            "why_recommended": f"Commonly paired with {product_id}",
        }
        for p in products
    ]

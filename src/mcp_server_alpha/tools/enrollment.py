"""Enrollment tools."""
from typing import Any

from ..config import ProductRegistry
from ..models import Consumer, Quote
from ..providers import ProviderRegistry


async def initiate_enrollment_tool(
    product_registry: ProductRegistry,
    provider_registry: ProviderRegistry,
    quote: Quote,
    consumer: Consumer,
    enrollment_data: dict[str, Any],
) -> dict[str, Any]:
    """
    Initiate enrollment for a product.

    Args:
        product_registry: Product registry
        provider_registry: Provider registry
        quote: Approved quote
        consumer: Consumer information
        enrollment_data: Additional enrollment data from user

    Returns:
        Enrollment result
    """
    product = product_registry.get(quote.product_id)
    if not product:
        return {"success": False, "error": f"Product {quote.product_id} not found"}

    provider = provider_registry.get(product.provider_id)
    if not provider:
        return {"success": False, "error": f"Provider {product.provider_id} not available"}

    try:
        result = await provider.initiate_enrollment(quote, consumer, enrollment_data)
        return result
    except Exception as e:
        return {"success": False, "error": str(e)}

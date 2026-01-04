"""Quote generation tools."""
from typing import Any

from ..config import ProductRegistry
from ..models import Consumer, QuoteRequest
from ..providers import ProviderRegistry


async def generate_quote_tool(
    product_registry: ProductRegistry,
    provider_registry: ProviderRegistry,
    quote_request: QuoteRequest,
    consumer: Consumer,
) -> dict[str, Any]:
    """
    Generate a quote for a product.

    Args:
        product_registry: Product registry
        provider_registry: Provider registry
        quote_request: Quote request details
        consumer: Consumer information

    Returns:
        Quote response
    """
    product = product_registry.get(quote_request.product_id)
    if not product:
        return {
            "success": False,
            "error": f"Product {quote_request.product_id} not found",
            "quote": None,
        }

    provider = provider_registry.get(product.provider_id)
    if not provider:
        return {
            "success": False,
            "error": f"Provider {product.provider_id} not available",
            "quote": None,
        }

    try:
        quote = await provider.get_quote(quote_request, consumer)

        return {
            "success": True,
            "quote": {
                "quote_id": quote.quote_id,
                "product_id": quote.product_id,
                "monthly_premium": str(quote.monthly_premium),
                "deductible": str(quote.deductible) if quote.deductible else None,
                "coverage_amount": str(quote.coverage_amount) if quote.coverage_amount else None,
                "effective_date": quote.effective_date.isoformat(),
                "expiration_date": quote.expiration_date.isoformat(),
                "details": quote.details,
            },
            "error": None,
        }
    except Exception as e:
        return {"success": False, "error": str(e), "quote": None}

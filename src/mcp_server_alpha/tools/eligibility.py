"""Eligibility checking tools."""
from typing import Any

from ..config import ProductRegistry
from ..models import Consumer
from ..providers import ProviderRegistry


async def check_eligibility_tool(
    product_registry: ProductRegistry,
    provider_registry: ProviderRegistry,
    product_id: str,
    consumer: Consumer,
) -> dict[str, Any]:
    """
    Check if a consumer is eligible for a product.

    Args:
        product_registry: Product registry
        provider_registry: Provider registry
        product_id: Product ID to check
        consumer: Consumer information

    Returns:
        Eligibility result with reasons
    """
    product = product_registry.get(product_id)
    if not product:
        return {"eligible": False, "reasons": [f"Product {product_id} not found"]}

    # Check product-level eligibility
    product_eligible, product_reasons = product.check_eligibility(consumer.profile.to_dict())

    if not product_eligible:
        return {"eligible": False, "reasons": product_reasons, "disclaimers": []}

    # Check provider-level eligibility
    provider = provider_registry.get(product.provider_id)
    if not provider:
        return {
            "eligible": False,
            "reasons": [f"Provider {product.provider_id} not available"],
            "disclaimers": [],
        }

    provider_eligible, provider_reasons = await provider.check_eligibility(product, consumer)

    if not provider_eligible:
        return {"eligible": False, "reasons": provider_reasons, "disclaimers": []}

    # Return disclaimers if eligible
    disclaimers = [
        {
            "type": d.type,
            "title": d.title,
            "content": d.content,
            "required_acknowledgment": d.required_acknowledgment,
        }
        for d in sorted(product.disclaimers, key=lambda x: x.display_order)
    ]

    return {
        "eligible": True,
        "reasons": ["All eligibility requirements met"],
        "disclaimers": disclaimers,
        "enrollment_steps": [
            {"step_id": step.step_id, "name": step.name, "description": step.description}
            for step in product.enrollment_flow
        ],
    }

"""Example script demonstrating MCP server usage."""
import asyncio
from datetime import date
from decimal import Decimal
from pathlib import Path

from mcp_server_alpha.config import ConfigLoader, ProductRegistry
from mcp_server_alpha.models import Consumer, ConsumerProfile, QuoteRequest
from mcp_server_alpha.providers import MockInsuranceProvider, ProviderRegistry
from mcp_server_alpha.tools import (
    check_eligibility_tool,
    generate_quote_tool,
    get_cross_sell_products_tool,
    search_products_tool,
)


async def main():
    """Run example workflow."""
    print("=== MCP Server Alpha - Example Workflow ===\n")

    # 1. Set up registries
    print("1. Initializing registries...")
    product_registry = ProductRegistry()
    provider_registry = ProviderRegistry()

    # Load products
    config_dir = Path(__file__).parent / "products"
    ConfigLoader.load_from_directory(config_dir, product_registry)
    print(f"   Loaded {len(product_registry.list_products())} products\n")

    # Register provider
    provider = MockInsuranceProvider("mock_insurance_co")
    provider_registry.register(provider)
    print("   Registered mock insurance provider\n")

    # 2. Create sample consumer
    print("2. Creating sample consumer...")
    consumer = Consumer(
        id="demo-consumer-001",
        first_name="Alice",
        last_name="Johnson",
        email="alice.johnson@example.com",
        date_of_birth=date(1985, 3, 15),
        profile=ConsumerProfile(
            age=38,
            state="CA",
            zip_code="94102",
            income=85000,
            household_size=3,
            tobacco_user=False,
        ),
    )
    print(f"   Consumer: {consumer.first_name} {consumer.last_name}, Age: {consumer.profile.age}\n")

    # 3. Search for products
    print("3. Searching for health insurance products...")
    products = await search_products_tool(product_registry, category="health")
    for p in products:
        print(f"   - {p['name']} ({p['id']})")
    print()

    # 4. Check eligibility
    if products:
        product_id = products[0]["id"]
        print(f"4. Checking eligibility for {product_id}...")
        eligibility = await check_eligibility_tool(
            product_registry, provider_registry, product_id, consumer
        )
        print(f"   Eligible: {eligibility['eligible']}")
        if eligibility["eligible"]:
            print(f"   Reasons: {', '.join(eligibility['reasons'])}")
            if eligibility.get("disclaimers"):
                print(f"   Disclaimers: {len(eligibility['disclaimers'])} required")
        else:
            print(f"   Reasons: {', '.join(eligibility['reasons'])}")
        print()

        # 5. Generate quote (if eligible)
        if eligibility["eligible"]:
            print("5. Generating quote...")
            quote_request = QuoteRequest(
                product_id=product_id,
                consumer_id=consumer.id,
                coverage_amount=Decimal("100000"),
                dependents=2,
            )
            quote_result = await generate_quote_tool(
                product_registry, provider_registry, quote_request, consumer
            )
            if quote_result["success"]:
                quote = quote_result["quote"]
                print(f"   Quote ID: {quote['quote_id']}")
                print(f"   Monthly Premium: ${quote['monthly_premium']}")
                print(f"   Coverage: ${quote['coverage_amount']}")
                print(f"   Deductible: ${quote['deductible']}")
            print()

            # 6. Get cross-sell recommendations
            print("6. Getting cross-sell recommendations...")
            cross_sell = await get_cross_sell_products_tool(product_registry, product_id)
            if cross_sell:
                for p in cross_sell:
                    print(f"   - {p['name']} ({p['category']})")
            else:
                print("   No cross-sell products available")
            print()

    print("=== Example Complete ===")


if __name__ == "__main__":
    asyncio.run(main())

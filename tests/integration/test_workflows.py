"""Integration tests for MCP server tools."""
import pytest
from datetime import date
from decimal import Decimal

from mcp_server_alpha.config import ProductRegistry
from mcp_server_alpha.models import (
    Consumer,
    ConsumerProfile,
    Product,
    ProductCategory,
    QuoteRequest,
)
from mcp_server_alpha.providers import MockInsuranceProvider, ProviderRegistry
from mcp_server_alpha.tools import (
    check_eligibility_tool,
    generate_quote_tool,
    get_cross_sell_products_tool,
    search_products_tool,
)


@pytest.fixture
def product_registry():
    """Create product registry with sample products."""
    registry = ProductRegistry()

    product1 = Product(
        id="health-001",
        name="Basic Health Plan",
        category=ProductCategory.HEALTH,
        provider_id="mock_insurance_co",
        description="Basic health coverage",
        cross_sell_products=["dental-001", "vision-001"],
        active=True,
    )

    product2 = Product(
        id="dental-001",
        name="Dental Plan",
        category=ProductCategory.DENTAL,
        provider_id="mock_insurance_co",
        description="Dental coverage",
        active=True,
    )

    product3 = Product(
        id="vision-001",
        name="Vision Plan",
        category=ProductCategory.VISION,
        provider_id="mock_insurance_co",
        description="Vision coverage",
        active=True,
    )

    registry.register(product1)
    registry.register(product2)
    registry.register(product3)

    yield registry
    registry.clear()


@pytest.fixture
def provider_registry():
    """Create provider registry with mock provider."""
    registry = ProviderRegistry()
    provider = MockInsuranceProvider("mock_insurance_co")
    registry.register(provider)
    yield registry
    registry.clear()


@pytest.fixture
def sample_consumer():
    """Create sample consumer."""
    return Consumer(
        id="consumer-001",
        first_name="John",
        last_name="Doe",
        email="john@example.com",
        date_of_birth=date(1985, 5, 15),
        profile=ConsumerProfile(
            age=38,
            state="CA",
            zip_code="90210",
            income=75000,
            household_size=2,
            tobacco_user=False,
        ),
    )


@pytest.mark.asyncio
async def test_search_products_tool(product_registry):
    """Test product search tool."""
    results = await search_products_tool(product_registry)
    assert len(results) == 3

    # Search by category
    health_results = await search_products_tool(product_registry, category="health")
    assert len(health_results) == 1
    assert health_results[0]["category"] == "health"


@pytest.mark.asyncio
async def test_check_eligibility_tool(product_registry, provider_registry, sample_consumer):
    """Test eligibility check tool."""
    result = await check_eligibility_tool(
        product_registry, provider_registry, "health-001", sample_consumer
    )

    assert result["eligible"] is True
    assert "reasons" in result


@pytest.mark.asyncio
async def test_generate_quote_tool(product_registry, provider_registry, sample_consumer):
    """Test quote generation tool."""
    quote_request = QuoteRequest(
        product_id="health-001",
        consumer_id=sample_consumer.id,
        coverage_amount=Decimal("50000"),
        dependents=0,
    )

    result = await generate_quote_tool(
        product_registry, provider_registry, quote_request, sample_consumer
    )

    assert result["success"] is True
    assert result["quote"] is not None
    assert "monthly_premium" in result["quote"]


@pytest.mark.asyncio
async def test_cross_sell_tool(product_registry):
    """Test cross-sell recommendations tool."""
    results = await get_cross_sell_products_tool(product_registry, "health-001")

    assert len(results) == 2
    assert any(p["id"] == "dental-001" for p in results)
    assert any(p["id"] == "vision-001" for p in results)


@pytest.mark.asyncio
async def test_end_to_end_workflow(product_registry, provider_registry, sample_consumer):
    """Test complete workflow from search to quote."""
    # 1. Search for products
    products = await search_products_tool(product_registry, category="health")
    assert len(products) > 0
    product_id = products[0]["id"]

    # 2. Check eligibility
    eligibility = await check_eligibility_tool(
        product_registry, provider_registry, product_id, sample_consumer
    )
    assert eligibility["eligible"] is True

    # 3. Generate quote
    quote_request = QuoteRequest(
        product_id=product_id,
        consumer_id=sample_consumer.id,
        coverage_amount=Decimal("50000"),
        dependents=0,
    )
    quote_result = await generate_quote_tool(
        product_registry, provider_registry, quote_request, sample_consumer
    )
    assert quote_result["success"] is True

    # 4. Get cross-sell recommendations
    cross_sell = await get_cross_sell_products_tool(product_registry, product_id)
    assert len(cross_sell) > 0

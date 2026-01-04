"""Unit tests for provider implementations."""
import pytest
from datetime import date
from decimal import Decimal

from mcp_server_alpha.models import Consumer, ConsumerProfile, Product, ProductCategory, QuoteRequest
from mcp_server_alpha.providers import MockInsuranceProvider


@pytest.fixture
def mock_provider():
    """Create a mock provider instance."""
    return MockInsuranceProvider("test_provider")


@pytest.fixture
def sample_consumer():
    """Create a sample consumer."""
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


@pytest.fixture
def sample_product():
    """Create a sample product."""
    return Product(
        id="health-001",
        name="Basic Health Plan",
        category=ProductCategory.HEALTH,
        provider_id="test_provider",
        description="Basic health insurance",
    )


@pytest.mark.asyncio
async def test_mock_provider_eligibility(mock_provider, sample_product, sample_consumer):
    """Test mock provider eligibility check."""
    is_eligible, reasons = await mock_provider.check_eligibility(sample_product, sample_consumer)
    assert is_eligible is True
    assert "All eligibility requirements met" in reasons


@pytest.mark.asyncio
async def test_mock_provider_eligibility_underage(mock_provider, sample_product):
    """Test eligibility fails for underage consumer."""
    underage_consumer = Consumer(
        id="consumer-002",
        first_name="Jane",
        last_name="Doe",
        email="jane@example.com",
        date_of_birth=date(2010, 1, 1),
        profile=ConsumerProfile(age=14, state="CA", zip_code="90210"),
    )

    is_eligible, reasons = await mock_provider.check_eligibility(sample_product, underage_consumer)
    assert is_eligible is False
    assert any("18 or older" in reason for reason in reasons)


@pytest.mark.asyncio
async def test_mock_provider_quote(mock_provider, sample_consumer):
    """Test mock provider quote generation."""
    quote_request = QuoteRequest(
        product_id="health-001",
        consumer_id=sample_consumer.id,
        coverage_amount=Decimal("50000"),
        dependents=0,
    )

    quote = await mock_provider.get_quote(quote_request, sample_consumer)

    assert quote.quote_id is not None
    assert quote.product_id == "health-001"
    assert quote.consumer_id == sample_consumer.id
    assert quote.monthly_premium > 0
    assert quote.coverage_amount == Decimal("50000")


@pytest.mark.asyncio
async def test_mock_provider_quote_with_dependents(mock_provider, sample_consumer):
    """Test quote calculation with dependents."""
    quote_request = QuoteRequest(
        product_id="health-001",
        consumer_id=sample_consumer.id,
        coverage_amount=Decimal("50000"),
        dependents=2,
    )

    quote = await mock_provider.get_quote(quote_request, sample_consumer)

    # Should have higher premium with dependents
    assert quote.monthly_premium > Decimal("100")


@pytest.mark.asyncio
async def test_mock_provider_quote_tobacco_user(mock_provider):
    """Test quote calculation for tobacco user."""
    tobacco_consumer = Consumer(
        id="consumer-003",
        first_name="Bob",
        last_name="Smith",
        email="bob@example.com",
        date_of_birth=date(1985, 5, 15),
        profile=ConsumerProfile(
            age=38,
            state="CA",
            zip_code="90210",
            tobacco_user=True,
        ),
    )

    quote_request = QuoteRequest(
        product_id="health-001",
        consumer_id=tobacco_consumer.id,
        coverage_amount=Decimal("50000"),
        dependents=0,
    )

    tobacco_quote = await mock_provider.get_quote(quote_request, tobacco_consumer)

    # Create non-tobacco quote for comparison
    non_tobacco_consumer = Consumer(
        id="consumer-004",
        first_name="Alice",
        last_name="Jones",
        email="alice@example.com",
        date_of_birth=date(1985, 5, 15),
        profile=ConsumerProfile(
            age=38,
            state="CA",
            zip_code="90210",
            tobacco_user=False,
        ),
    )

    non_tobacco_quote = await mock_provider.get_quote(quote_request, non_tobacco_consumer)

    # Tobacco user should pay more
    assert tobacco_quote.monthly_premium > non_tobacco_quote.monthly_premium


@pytest.mark.asyncio
async def test_mock_provider_enrollment(mock_provider, sample_consumer):
    """Test mock enrollment initiation."""
    from mcp_server_alpha.models import Quote
    from datetime import datetime

    quote = Quote(
        quote_id="quote-001",
        product_id="health-001",
        consumer_id=sample_consumer.id,
        monthly_premium=Decimal("150.00"),
        deductible=Decimal("1000.00"),
        coverage_amount=Decimal("50000.00"),
        effective_date=datetime.now(),
        expiration_date=datetime.now(),
    )

    result = await mock_provider.initiate_enrollment(quote, sample_consumer, {})

    assert result["success"] is True
    assert "enrollment_id" in result
    assert result["status"] == "pending"
    assert "next_steps" in result


@pytest.mark.asyncio
async def test_mock_provider_enrollment_status(mock_provider):
    """Test enrollment status check."""
    result = await mock_provider.get_enrollment_status("enrollment-123")

    assert "enrollment_id" in result
    assert "status" in result
    assert "progress" in result

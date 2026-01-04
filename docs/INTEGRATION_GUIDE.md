# Integration Guide

## Adding a New Insurance Provider

This guide walks through integrating a new insurance carrier into the MCP server.

### Step 1: Implement the Provider Interface

Create a new file in `src/mcp_server_alpha/providers/`:

```python
# src/mcp_server_alpha/providers/acme_insurance.py
import httpx
from typing import Any
from ..models import Consumer, Product, Quote, QuoteRequest
from .base import BaseProvider

class AcmeInsuranceProvider(BaseProvider):
    """Integration with Acme Insurance carrier API."""
    
    def __init__(self, provider_id: str, config: dict[str, Any] | None = None):
        super().__init__(provider_id, config)
        self.api_key = config.get("api_key")
        self.base_url = config.get("base_url", "https://api.acme-insurance.com")
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            headers={"Authorization": f"Bearer {self.api_key}"}
        )
    
    async def check_eligibility(
        self, product: Product, consumer: Consumer
    ) -> tuple[bool, list[str]]:
        """Check eligibility with Acme's API."""
        # First, check product-level rules
        is_eligible, reasons = product.check_eligibility(consumer.profile.to_dict())
        if not is_eligible:
            return False, reasons
        
        # Then check with carrier API
        response = await self.client.post("/eligibility/check", json={
            "product_code": product.metadata.get("acme_product_code"),
            "member": {
                "age": consumer.profile.age,
                "state": consumer.profile.state,
                "zip": consumer.profile.zip_code,
            }
        })
        
        data = response.json()
        return data["eligible"], data.get("reasons", [])
    
    async def get_quote(self, quote_request: QuoteRequest, consumer: Consumer) -> Quote:
        """Get quote from Acme's API."""
        response = await self.client.post("/quotes", json={
            "product_id": quote_request.product_id,
            "member_age": consumer.profile.age,
            "coverage_amount": str(quote_request.coverage_amount),
            "dependents": quote_request.dependents,
        })
        
        data = response.json()
        
        # Map Acme's response to our Quote model
        return Quote(
            quote_id=data["quote_reference"],
            product_id=quote_request.product_id,
            consumer_id=quote_request.consumer_id,
            monthly_premium=Decimal(data["monthly_premium"]),
            deductible=Decimal(data["deductible"]),
            coverage_amount=quote_request.coverage_amount,
            effective_date=...,
            expiration_date=...,
        )
    
    async def initiate_enrollment(
        self, quote: Quote, consumer: Consumer, enrollment_data: dict[str, Any]
    ) -> dict[str, Any]:
        """Start enrollment with Acme."""
        response = await self.client.post("/enrollments", json={
            "quote_id": quote.quote_id,
            "member": {
                "first_name": consumer.first_name,
                "last_name": consumer.last_name,
                "email": consumer.email,
                ...
            },
            **enrollment_data
        })
        
        data = response.json()
        return {
            "success": data["status"] == "initiated",
            "enrollment_id": data["enrollment_id"],
            "status": data["status"],
            "next_steps": data["required_actions"],
        }
    
    async def get_enrollment_status(self, enrollment_id: str) -> dict[str, Any]:
        """Check enrollment status with Acme."""
        response = await self.client.get(f"/enrollments/{enrollment_id}")
        data = response.json()
        return {
            "enrollment_id": enrollment_id,
            "status": data["status"],
            "progress": data.get("completion_percentage", 0) / 100,
            "current_step": data.get("current_step"),
        }
```

### Step 2: Register the Provider

Update your server initialization:

```python
# src/mcp_server_alpha/server.py
from .providers import AcmeInsuranceProvider

# In __init__:
acme_provider = AcmeInsuranceProvider("acme_insurance", config={
    "api_key": os.getenv("ACME_API_KEY"),
    "base_url": "https://api.acme-insurance.com"
})
self.provider_registry.register(acme_provider)
```

### Step 3: Create Products for the Provider

Create product config files in `examples/products/`:

```json
{
  "id": "acme-health-gold",
  "name": "Acme Gold Health Plan",
  "category": "health",
  "provider_id": "acme_insurance",
  "description": "Premium health coverage from Acme",
  "eligibility_rules": [...],
  "metadata": {
    "acme_product_code": "GOLD-H-2024"
  }
}
```

### Step 4: Test the Integration

```python
# tests/integration/test_acme_provider.py
import pytest
from mcp_server_alpha.providers import AcmeInsuranceProvider

@pytest.mark.asyncio
async def test_acme_eligibility():
    provider = AcmeInsuranceProvider("acme_insurance", {
        "api_key": "test_key"
    })
    
    # Test eligibility check
    is_eligible, reasons = await provider.check_eligibility(...)
    assert is_eligible is True
```

## Error Handling Best Practices

1. **Handle API Timeouts**: Use httpx timeout configuration
2. **Retry Logic**: Implement exponential backoff for transient errors
3. **Logging**: Log all API calls and responses
4. **Validation**: Validate API responses before mapping to models
5. **Graceful Degradation**: Return meaningful errors to users

## Configuration Management

Store provider configs securely:

```python
# .env
ACME_API_KEY=your_api_key_here
ACME_BASE_URL=https://api.acme-insurance.com

# Load in server
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    acme_api_key: str
    acme_base_url: str
    
    class Config:
        env_file = ".env"
```

## Performance Considerations

1. **Connection Pooling**: Reuse httpx client instances
2. **Async/Await**: All provider methods are async
3. **Caching**: Cache eligibility results when appropriate
4. **Rate Limiting**: Respect provider API rate limits
5. **Monitoring**: Track API response times and errors

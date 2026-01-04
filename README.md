# MCP Server Alpha

A production-ready Model Context Protocol (MCP) server for insurance products, built with modern Python frameworks for extensibility, maintainability, and rapid development.

## 🎯 Project Vision

This MCP server enables seamless integration of insurance products and APIs through a flexible, config-driven architecture that:

- **Allows product managers** to add/configure products, eligibility rules, and compliance workflows without code changes
- **Abstracts provider APIs** (carriers, enrollment systems) for easy addition of new partners
- **Supports multi-step enrollment flows** that vary by carrier or product
- **Enables cross-sell/upsell logic** based on consumer profiles and product compatibility
- **Works across channels** (chat, voice, SMS) using adapters that share business logic
- **Facilitates rapid QA** of new product configurations before launch

## 🏗️ Architecture

```
src/mcp_server_alpha/
├── models/          # Type-safe data models (Product, Consumer, Quote, etc.)
├── providers/       # Provider abstraction layer for carrier APIs
├── config/          # Config-driven product registry and loader
├── tools/           # MCP tool implementations (search, eligibility, quotes)
├── orchestration/   # Workflow engine for multi-step processes
├── adapters/        # Multi-channel adapters (chat, voice, SMS)
└── server.py        # Main MCP server implementation
```

### Key Components

#### 1. **Config-Driven Product System**
Products are defined in JSON/YAML files with:
- Eligibility rules and qualifiers
- Compliance disclaimers
- Multi-step enrollment flows
- Cross-sell product mappings
- Provider-specific metadata

#### 2. **Provider Abstraction Layer**
Clean interface for integrating carrier APIs:
```python
class BaseProvider(ABC):
    async def check_eligibility(...)
    async def get_quote(...)
    async def initiate_enrollment(...)
    async def get_enrollment_status(...)
```

#### 3. **MCP Tools**
Five core tools exposed via MCP:
- `search_products` - Find products by category/provider
- `check_eligibility` - Verify consumer eligibility
- `generate_quote` - Get pricing quotes
- `get_cross_sell_products` - Recommend compatible products
- `initiate_enrollment` - Start enrollment process

#### 4. **Multi-Channel Adapters**
Format responses for different channels without duplicating logic:
- Chat adapter (formatted markdown)
- Voice adapter (coming soon)
- SMS adapter (coming soon)

#### 5. **Workflow Orchestration**
State machine for managing multi-step processes:
- Eligibility → Quote → Cross-sell → Enrollment
- Configurable branching logic
- Error handling and rollback support

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- pip or uv

### Installation

```bash
# Clone the repository
git clone https://github.com/tc-digital/mcp-server-alpha.git
cd mcp-server-alpha

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -e ".[dev]"
```

### Running the Server

```bash
# Run the MCP server
python -m mcp_server_alpha.server

# Or use as a module
python src/mcp_server_alpha/server.py
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=mcp_server_alpha --cov-report=html

# Run specific test suite
pytest tests/unit/
pytest tests/integration/
```

### Linting and Type Checking

```bash
# Run ruff linter
ruff check src/

# Run type checker
mypy src/
```

## 📝 Usage Examples

### Defining a Product

Create a JSON file in `examples/products/`:

```json
{
  "id": "health-premium-001",
  "name": "Premium Health Plan",
  "category": "health",
  "provider_id": "carrier_abc",
  "description": "Comprehensive health coverage",
  "eligibility_rules": [
    {
      "name": "age_requirement",
      "description": "Age 18-64",
      "qualifiers": [
        {
          "name": "min_age",
          "description": "At least 18",
          "field": "age",
          "operator": "gte",
          "value": 18
        }
      ],
      "logic": "all"
    }
  ],
  "disclaimers": [
    {
      "type": "compliance",
      "title": "Coverage Notice",
      "content": "Coverage subject to state regulations...",
      "required_acknowledgment": true,
      "display_order": 1
    }
  ],
  "enrollment_flow": [
    {
      "step_id": "personal_info",
      "name": "Personal Information",
      "description": "Basic demographic info",
      "required_fields": ["first_name", "last_name", "email"],
      "next_step": "payment_info"
    },
    {
      "step_id": "payment_info",
      "name": "Payment",
      "description": "Payment details",
      "required_fields": ["payment_method"],
      "next_step": null
    }
  ],
  "cross_sell_products": ["dental-001", "vision-001"],
  "active": true
}
```

### Adding a New Provider

Implement the `BaseProvider` interface:

```python
from mcp_server_alpha.providers import BaseProvider

class MyCarrierProvider(BaseProvider):
    async def check_eligibility(self, product, consumer):
        # Call carrier API
        response = await self.api_client.check_eligibility(...)
        return response.eligible, response.reasons
    
    async def get_quote(self, quote_request, consumer):
        # Generate quote via carrier API
        ...
```

Register the provider:

```python
provider = MyCarrierProvider("my_carrier", config={
    "api_key": "...",
    "endpoint": "https://api.carrier.com"
})
provider_registry.register(provider)
```

### Using MCP Tools

The server exposes tools through the MCP protocol:

```python
# Search for health insurance products
result = await call_tool("search_products", {
    "category": "health",
    "active_only": True
})

# Check eligibility
result = await call_tool("check_eligibility", {
    "product_id": "health-001",
    "consumer_data": {
        "profile": {"age": 35, "state": "CA", ...}
    }
})

# Generate quote
result = await call_tool("generate_quote", {
    "product_id": "health-001",
    "consumer_data": {...},
    "coverage_amount": 50000,
    "dependents": 2
})
```

## 🧪 Testing

The project includes comprehensive test coverage:

### Unit Tests
- `tests/unit/test_models.py` - Product models, eligibility rules, qualifiers
- `tests/unit/test_providers.py` - Provider implementations
- `tests/unit/test_config.py` - Configuration loading and registry

### Integration Tests
- `tests/integration/test_workflows.py` - End-to-end workflows

### Example Test

```python
@pytest.mark.asyncio
async def test_eligibility_check():
    consumer = Consumer(
        id="test-001",
        profile=ConsumerProfile(age=30, state="CA", ...)
    )
    
    result = await check_eligibility_tool(
        product_registry,
        provider_registry,
        "health-001",
        consumer
    )
    
    assert result["eligible"] is True
```

## 🔧 Configuration

### Product Configuration
Products are loaded from `examples/products/*.json` on server startup. No code changes needed to add products.

### Provider Configuration
Providers can be configured with:
- API credentials
- Endpoint URLs
- Timeout settings
- Retry policies

### Environment Variables
```bash
# Optional: Set config directory
export PRODUCT_CONFIG_DIR=/path/to/products

# Optional: Set log level
export LOG_LEVEL=DEBUG
```

## 📚 Tech Stack

- **MCP SDK** - Model Context Protocol implementation
- **Pydantic** - Type-safe data validation
- **FastAPI** - API framework (for future REST endpoints)
- **SQLModel** - Database models (for future persistence)
- **LangGraph** - Workflow orchestration
- **pytest** - Testing framework
- **ruff** - Fast Python linter
- **mypy** - Static type checking

## 🛣️ Roadmap

- [x] Core MCP server implementation
- [x] Config-driven product system
- [x] Provider abstraction layer
- [x] Mock provider for testing
- [x] MCP tools (search, eligibility, quote, cross-sell)
- [x] Multi-channel adapters (chat)
- [x] Workflow orchestration
- [x] Comprehensive tests
- [ ] Database persistence layer
- [ ] Real carrier API integrations
- [ ] Voice adapter
- [ ] SMS adapter
- [ ] Admin UI for product configuration
- [ ] Analytics and reporting
- [ ] Advanced workflow branching
- [ ] A/B testing framework

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests (`pytest`)
5. Run linting (`ruff check src/`)
6. Commit your changes (`git commit -m 'Add amazing feature'`)
7. Push to the branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

## 📄 License

This project is proprietary software owned by TC Digital.

## 💡 Design Principles

1. **Separation of Concerns** - Business logic, provider logic, and presentation are cleanly separated
2. **Config Over Code** - Products and rules defined in config files, not hardcoded
3. **Type Safety** - Pydantic models ensure data integrity throughout
4. **Testability** - Every component has clear interfaces and comprehensive tests
5. **Extensibility** - New providers, products, and channels added without core changes
6. **Production Ready** - Error handling, logging, validation from day one

## 📞 Support

For questions or issues:
- Open an issue on GitHub
- Contact the development team
- Check the documentation in `/docs` (coming soon)

---

Built with ❤️ by TC Digital

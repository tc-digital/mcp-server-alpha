# Architecture Overview

## System Architecture

The MCP Server Alpha is designed as a modular, production-ready system for managing insurance products and workflows through the Model Context Protocol.

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      MCP Client                              │
│                 (Claude, Custom Apps)                        │
└──────────────────────┬──────────────────────────────────────┘
                       │ MCP Protocol
┌──────────────────────▼──────────────────────────────────────┐
│                   MCP Server Alpha                           │
│  ┌────────────────────────────────────────────────────────┐ │
│  │              MCP Tools Layer                           │ │
│  │  • search_products  • check_eligibility                │ │
│  │  • generate_quote   • get_cross_sell_products          │ │
│  │  • initiate_enrollment                                 │ │
│  └────────────┬──────────────────────────────┬────────────┘ │
│               │                              │               │
│  ┌────────────▼────────────┐  ┌─────────────▼────────────┐ │
│  │   Product Registry      │  │   Provider Registry      │ │
│  │  • Config-driven        │  │  • Abstract API layer    │ │
│  │  • Eligibility rules    │  │  • Multiple carriers     │ │
│  │  • Disclaimers          │  │  • Pluggable impl.       │ │
│  └─────────────────────────┘  └──────────────────────────┘ │
│               │                              │               │
│  ┌────────────▼──────────────────────────────▼────────────┐ │
│  │           Workflow Orchestration Engine                │ │
│  │  • State management   • Multi-step flows               │ │
│  │  • Error handling     • Branching logic                │ │
│  └────────────────────────────┬──────────────────────────┘ │
│                               │                             │
│  ┌────────────────────────────▼──────────────────────────┐ │
│  │         Multi-Channel Adapters                        │ │
│  │  • Chat Adapter  • Voice Adapter  • SMS Adapter       │ │
│  └───────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│              External Systems                                │
│  • Carrier APIs  • Payment Gateways  • CRM Systems          │
└─────────────────────────────────────────────────────────────┘
```

## Core Components

### 1. Models Layer (`models/`)
**Purpose**: Type-safe data structures using Pydantic

**Key Models**:
- `Product`: Insurance product definition with eligibility rules, disclaimers, enrollment flows
- `Consumer`: Consumer profile with demographic and health information
- `Quote`: Quote details including pricing and coverage
- `EligibilityRule`: Configurable rule engine for product eligibility
- `Qualifier`: Individual eligibility criteria with operators

**Design Principles**:
- Immutable data structures
- Strict type checking
- Comprehensive validation
- Serialization support for config files

### 2. Providers Layer (`providers/`)
**Purpose**: Abstract carrier/vendor API integrations

**Interface**:
```python
class BaseProvider(ABC):
    async def check_eligibility(product, consumer) -> (bool, reasons)
    async def get_quote(quote_request, consumer) -> Quote
    async def initiate_enrollment(quote, consumer, data) -> dict
    async def get_enrollment_status(enrollment_id) -> dict
```

**Benefits**:
- New carriers added without core code changes
- Consistent interface across all providers
- Easy testing with mock implementations
- Parallel API calls supported

**Registry Pattern**:
- Providers registered at startup
- Lookup by provider_id
- Configuration injection for credentials

### 3. Config System (`config/`)
**Purpose**: Load and manage product configurations

**Features**:
- JSON/YAML product definitions
- Hot-reload capability (future)
- Validation on load
- Hierarchical organization

**Product Registry**:
- In-memory product catalog
- Fast lookups by ID
- Filtered queries (category, provider, active status)
- Cross-sell relationship tracking

### 4. Tools Layer (`tools/`)
**Purpose**: MCP tool implementations

**Available Tools**:
1. `search_products`: Find products by filters
2. `check_eligibility`: Verify consumer eligibility
3. `generate_quote`: Get pricing quotes
4. `get_cross_sell_products`: Recommend related products
5. `initiate_enrollment`: Start enrollment process

**Tool Design**:
- Async/await for performance
- Comprehensive error handling
- Structured return values
- Channel-agnostic logic

### 5. Orchestration Layer (`orchestration/`)
**Purpose**: Manage multi-step workflows

**Workflow States**:
```
INITIATED → ELIGIBILITY_CHECK → QUOTE_GENERATION → 
CROSS_SELL → ENROLLMENT → COMPLETED/FAILED
```

**Features**:
- State machine implementation
- Context preservation across steps
- Error tracking and recovery
- Audit trail support

### 6. Adapters Layer (`adapters/`)
**Purpose**: Format responses for different channels

**Channel Support**:
- **Chat Adapter**: Markdown formatting for chat interfaces
- **Voice Adapter**: TTS-friendly responses (future)
- **SMS Adapter**: Concise text messages (future)

**Benefits**:
- No business logic duplication
- Consistent formatting per channel
- Easy addition of new channels

## Data Flow

### Example: Complete Enrollment Flow

```
1. User: "Show me health insurance plans"
   ↓
2. MCP Tool: search_products(category="health")
   ↓
3. Product Registry: filter and return matching products
   ↓
4. Chat Adapter: format product list for display
   ↓
5. User: "Check if I'm eligible for health-basic-001"
   ↓
6. MCP Tool: check_eligibility(product_id, consumer_data)
   ↓
7. Product Registry: get product and check rules
   ↓
8. Provider: call carrier API for additional checks
   ↓
9. Workflow Engine: update state to ELIGIBILITY_CHECK
   ↓
10. Chat Adapter: format eligibility result with disclaimers
   ↓
11. User: "Generate a quote"
   ↓
12. MCP Tool: generate_quote(product_id, consumer_data)
   ↓
13. Provider: call carrier quote API
   ↓
14. Workflow Engine: update state to QUOTE_GENERATION
   ↓
15. MCP Tool: get_cross_sell_products(product_id)
   ↓
16. Product Registry: return related products
   ↓
17. Workflow Engine: update state to CROSS_SELL
   ↓
18. Chat Adapter: format quote and recommendations
```

## Design Patterns

### 1. Registry Pattern
Used for both Products and Providers to enable:
- Dependency injection
- Runtime configuration
- Easy testing with mocks
- Pluggable architecture

### 2. Strategy Pattern
Used in Provider abstraction to:
- Swap implementations without code changes
- Support multiple carriers
- Test with mock providers

### 3. Adapter Pattern
Used for multi-channel support to:
- Separate presentation from logic
- Support multiple interfaces
- Reuse business logic

### 4. State Machine Pattern
Used in workflow orchestration to:
- Track process state
- Handle transitions
- Manage error states
- Enable rollback

## Configuration Strategy

### Product Configuration
Products are defined in JSON/YAML files with:

```json
{
  "id": "product-id",
  "name": "Product Name",
  "category": "health",
  "provider_id": "carrier_name",
  "eligibility_rules": [...],
  "disclaimers": [...],
  "enrollment_flow": [...],
  "cross_sell_products": [...]
}
```

**Benefits**:
- Product managers can add products without code
- Version control for product definitions
- A/B testing support
- Rapid QA of new products

### Provider Configuration
Providers configured with:
- API credentials (from environment)
- Endpoint URLs
- Timeout settings
- Retry policies

## Extensibility Points

### Adding a New Provider
1. Implement `BaseProvider` interface
2. Register provider in server initialization
3. Configure API credentials
4. Add products with `provider_id`

### Adding a New Product Category
1. Add enum value to `ProductCategory`
2. Create product JSON config
3. No code changes required

### Adding a New Channel
1. Implement `BaseAdapter` interface
2. Register adapter in server
3. Format methods for channel-specific output

### Adding a New Tool
1. Create async function in `tools/`
2. Register tool in MCP server
3. Define input schema
4. Implement business logic

## Security Considerations

### Current Implementation
- Type validation on all inputs
- Pydantic model validation
- No credentials in code (env vars)
- Abstract provider layer prevents direct API exposure

### Production Enhancements
- API key rotation
- Rate limiting per consumer
- Request logging and audit trail
- PII encryption
- HIPAA compliance measures
- OAuth2 authentication
- Role-based access control

## Performance Considerations

### Current Optimizations
- Async/await throughout
- In-memory registries
- Connection pooling (httpx)
- Efficient serialization (Pydantic)

### Future Optimizations
- Redis caching for quotes
- Database persistence
- CDN for static content
- Load balancing
- Horizontal scaling support

## Testing Strategy

### Unit Tests
- Model validation
- Eligibility logic
- Provider implementations
- Registry operations

### Integration Tests
- End-to-end workflows
- Multi-step processes
- Cross-sell recommendations
- Tool interactions

### Future Testing
- Load testing
- Security testing
- API compatibility testing
- User acceptance testing

## Deployment Architecture

### Development
```
Local Development
├── Python 3.10+
├── Virtual environment
├── pytest for testing
└── Mock providers
```

### Production (Future)
```
Load Balancer
├── MCP Server Instance 1
├── MCP Server Instance 2
└── MCP Server Instance N
    ├── Redis Cache
    ├── PostgreSQL Database
    └── External APIs
```

## Technology Stack Rationale

### Python 3.10+
- Modern async/await support
- Type hints and mypy
- Rich ecosystem
- Fast development

### Pydantic
- Type-safe models
- Automatic validation
- JSON serialization
- OpenAPI schema generation

### FastAPI (Ready for REST)
- High performance
- Automatic docs
- Async native
- Modern Python patterns

### MCP SDK
- Standard protocol
- Claude integration
- Tool abstraction
- Future-proof

### LangGraph
- Workflow orchestration
- State management
- Graph-based flows
- LangChain integration

### pytest
- Async support
- Fixtures
- Parametrization
- Coverage reporting

### ruff
- Fast linting
- Auto-fixing
- Modern rules
- Drop-in replacement

## Future Enhancements

### Phase 2
- [ ] Database persistence (PostgreSQL)
- [ ] Caching layer (Redis)
- [ ] Real carrier integrations
- [ ] Voice and SMS adapters
- [ ] Payment processing

### Phase 3
- [ ] Admin UI for product management
- [ ] Analytics dashboard
- [ ] A/B testing framework
- [ ] Advanced workflow branching
- [ ] Machine learning recommendations

### Phase 4
- [ ] Multi-tenant support
- [ ] White-label capabilities
- [ ] API marketplace
- [ ] Plugin system
- [ ] GraphQL API

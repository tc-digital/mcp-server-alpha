"""Main MCP server implementation."""
import asyncio
import uuid
from datetime import date
from decimal import Decimal
from pathlib import Path
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

from .adapters import ChatAdapter
from .config import ConfigLoader, ProductRegistry
from .models import Consumer, ConsumerProfile, QuoteRequest
from .orchestration import WorkflowEngine
from .providers import MockInsuranceProvider, ProviderRegistry
from .tools import (
    check_eligibility_tool,
    generate_quote_tool,
    get_cross_sell_products_tool,
    search_products_tool,
)

# Configuration constants
DEFAULT_DOB = "1980-01-01"


class MCPServerAlpha:
    """Main MCP server class."""

    def __init__(self, config_dir: Path | None = None):
        """Initialize the MCP server."""
        self.server = Server("mcp-server-alpha")
        self.product_registry = ProductRegistry()
        self.provider_registry = ProviderRegistry()
        self.workflow_engine = WorkflowEngine()
        self.chat_adapter = ChatAdapter()

        # Register mock provider
        mock_provider = MockInsuranceProvider("mock_insurance_co")
        self.provider_registry.register(mock_provider)

        # Load products from config directory
        if config_dir:
            ConfigLoader.load_from_directory(config_dir, self.product_registry)

        # Register MCP tools
        self._register_tools()

    def _register_tools(self) -> None:
        """Register MCP tools."""

        @self.server.list_tools()
        async def list_tools() -> list[Tool]:
            """List available tools."""
            return [
                Tool(
                    name="search_products",
                    description="Search for insurance products by category and provider",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "category": {
                                "type": "string",
                                "description": (
                                    "Product category (health, dental, vision, life, "
                                    "disability, medicare, ancillary)"
                                ),
                            },
                            "provider_id": {
                                "type": "string",
                                "description": "Provider/carrier ID",
                            },
                            "active_only": {
                                "type": "boolean",
                                "description": "Only return active products",
                                "default": True,
                            },
                        },
                    },
                ),
                Tool(
                    name="check_eligibility",
                    description="Check if a consumer is eligible for a specific product",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "product_id": {
                                "type": "string",
                                "description": "Product ID to check eligibility for",
                            },
                            "consumer_data": {
                                "type": "object",
                                "description": "Consumer information including profile data",
                                "properties": {
                                    "id": {"type": "string"},
                                    "first_name": {"type": "string"},
                                    "last_name": {"type": "string"},
                                    "email": {"type": "string"},
                                    "date_of_birth": {"type": "string"},
                                    "profile": {
                                        "type": "object",
                                        "properties": {
                                            "age": {"type": "integer"},
                                            "state": {"type": "string"},
                                            "zip_code": {"type": "string"},
                                            "income": {"type": "integer"},
                                            "household_size": {"type": "integer"},
                                            "tobacco_user": {"type": "boolean"},
                                        },
                                    },
                                },
                            },
                        },
                        "required": ["product_id", "consumer_data"],
                    },
                ),
                Tool(
                    name="generate_quote",
                    description="Generate a quote for a specific product and consumer",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "product_id": {"type": "string"},
                            "consumer_data": {"type": "object"},
                            "coverage_amount": {"type": "number"},
                            "dependents": {"type": "integer", "default": 0},
                        },
                        "required": ["product_id", "consumer_data"],
                    },
                ),
                Tool(
                    name="get_cross_sell_products",
                    description="Get cross-sell product recommendations for a given product",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "product_id": {
                                "type": "string",
                                "description": "Product ID to get recommendations for",
                            }
                        },
                        "required": ["product_id"],
                    },
                ),
                Tool(
                    name="initiate_enrollment",
                    description="Initiate enrollment process for a quote",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "quote_id": {"type": "string"},
                            "consumer_data": {"type": "object"},
                            "enrollment_data": {
                                "type": "object",
                                "description": "Additional enrollment information",
                            },
                        },
                        "required": ["quote_id", "consumer_data"],
                    },
                ),
            ]

        @self.server.call_tool()
        async def call_tool(name: str, arguments: Any) -> list[TextContent]:
            """Handle tool calls."""
            try:
                if name == "search_products":
                    result = await search_products_tool(
                        self.product_registry,
                        category=arguments.get("category"),
                        provider_id=arguments.get("provider_id"),
                        active_only=arguments.get("active_only", True),
                    )
                    formatted = await self.chat_adapter.format_product_list(result)
                    return [TextContent(type="text", text=formatted)]

                elif name == "check_eligibility":
                    consumer = self._parse_consumer(arguments["consumer_data"])
                    result = await check_eligibility_tool(
                        self.product_registry,
                        self.provider_registry,
                        arguments["product_id"],
                        consumer,
                    )
                    formatted = await self.chat_adapter.format_eligibility_result(result)
                    return [TextContent(type="text", text=formatted)]

                elif name == "generate_quote":
                    consumer = self._parse_consumer(arguments["consumer_data"])
                    quote_request = QuoteRequest(
                        product_id=arguments["product_id"],
                        consumer_id=consumer.id,
                        coverage_amount=Decimal(str(arguments.get("coverage_amount", 50000))),
                        dependents=arguments.get("dependents", 0),
                    )
                    result = await generate_quote_tool(
                        self.product_registry,
                        self.provider_registry,
                        quote_request,
                        consumer,
                    )
                    formatted = await self.chat_adapter.format_quote(result)
                    return [TextContent(type="text", text=formatted)]

                elif name == "get_cross_sell_products":
                    result = await get_cross_sell_products_tool(
                        self.product_registry, arguments["product_id"]
                    )
                    formatted = await self.chat_adapter.format_product_list(result)
                    return [
                        TextContent(
                            type="text",
                            text=f"Cross-sell recommendations:\n\n{formatted}",
                        )
                    ]

                elif name == "initiate_enrollment":
                    # This would need quote storage in production
                    return [
                        TextContent(
                            type="text",
                            text=(
                                "Enrollment feature requires quote storage - "
                                "implement in production"
                            ),
                        )
                    ]

                else:
                    return [TextContent(type="text", text=f"Unknown tool: {name}")]

            except Exception as e:
                return [TextContent(type="text", text=f"Error: {str(e)}")]

    def _parse_consumer(self, consumer_data: dict[str, Any]) -> Consumer:
        """Parse consumer data from tool arguments."""
        profile_data = consumer_data.get("profile", {})
        profile = ConsumerProfile(**profile_data)

        # Parse date of birth with error handling
        dob_str = consumer_data.get("date_of_birth", DEFAULT_DOB)
        try:
            if isinstance(dob_str, str):
                dob = date.fromisoformat(dob_str)
            elif isinstance(dob_str, date):
                dob = dob_str
            else:
                dob = date.fromisoformat(DEFAULT_DOB)
        except (ValueError, AttributeError):
            dob = date.fromisoformat(DEFAULT_DOB)

        return Consumer(
            id=consumer_data.get("id", str(uuid.uuid4())),
            first_name=consumer_data.get("first_name", ""),
            last_name=consumer_data.get("last_name", ""),
            email=consumer_data.get("email", ""),
            phone=consumer_data.get("phone"),
            date_of_birth=dob,
            profile=profile,
        )

    async def run(self) -> None:
        """Run the MCP server."""
        async with stdio_server() as (read_stream, write_stream):
            init_options = self.server.create_initialization_options()
            await self.server.run(read_stream, write_stream, init_options)


def main() -> None:
    """Entry point for the MCP server."""
    # Load products from examples directory
    config_dir = Path(__file__).parent.parent.parent / "examples" / "products"

    server = MCPServerAlpha(config_dir=config_dir if config_dir.exists() else None)
    asyncio.run(server.run())


if __name__ == "__main__":
    main()

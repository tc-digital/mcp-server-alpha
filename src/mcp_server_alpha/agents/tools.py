"""Tool wrappers for LangChain agent integration."""
from decimal import Decimal

from langchain_core.tools import tool

from ..config import ProductRegistry
from ..models import Consumer, QuoteRequest
from ..providers import ProviderRegistry
from ..tools import (
    check_eligibility_tool as _check_eligibility,
)
from ..tools import (
    generate_quote_tool as _generate_quote,
)
from ..tools import (
    get_cross_sell_products_tool as _get_cross_sell,
)
from ..tools import (
    search_products_tool as _search_products,
)


class AgentTools:
    """
    Wrapper for MCP tools to make them compatible with LangChain agents.

    This class converts our async MCP tools into LangChain tool format.
    """

    def __init__(
        self, product_registry: ProductRegistry, provider_registry: ProviderRegistry
    ):
        """Initialize with registries."""
        self.product_registry = product_registry
        self.provider_registry = provider_registry

    def get_tools(self) -> list:
        """Get list of LangChain-compatible tools."""

        @tool
        async def search_products(
            category: str | None = None, provider_id: str | None = None
        ) -> str:
            """
            Search for insurance products by category and provider.

            Args:
                category: Product category (health, dental, vision, life,
                    disability, medicare, ancillary)
                provider_id: Provider/carrier identifier

            Returns:
                Formatted list of matching products
            """
            results = await _search_products(
                self.product_registry,
                category=category,
                provider_id=provider_id,
                active_only=True,
            )

            if not results:
                return "No products found matching criteria."

            output = "Found products:\n"
            for p in results:
                output += f"\n• {p['name']} ({p['category']})"
                output += f"\n  ID: {p['id']}"
                output += f"\n  Provider: {p['provider_id']}"
                output += f"\n  Description: {p['description']}\n"

            return output

        @tool
        async def check_eligibility(
            product_id: str, age: int, state: str, zip_code: str
        ) -> str:
            """
            Check if a consumer is eligible for a specific insurance product.

            Args:
                product_id: Product identifier
                age: Consumer age
                state: State of residence (e.g., 'CA', 'NY')
                zip_code: ZIP code

            Returns:
                Eligibility result with explanation
            """
            # Create consumer from parameters
            from datetime import date, datetime
            from uuid import uuid4

            from ..models import ConsumerProfile

            birth_year = datetime.now().year - age

            consumer = Consumer(
                id=str(uuid4()),
                first_name="User",
                last_name="",
                email="user@example.com",
                date_of_birth=date(birth_year, 1, 1),
                profile=ConsumerProfile(
                    age=age, state=state, zip_code=zip_code
                ),
            )

            result = await _check_eligibility(
                self.product_registry,
                self.provider_registry,
                product_id,
                consumer,
            )

            if result["eligible"]:
                output = "✓ Eligible for this product!\n"
                output += f"Reasons: {', '.join(result['reasons'])}\n"

                if result.get("disclaimers"):
                    disclaimers_count = len(result['disclaimers'])
                    output += f"\nImportant notices: {disclaimers_count} disclaimer(s) apply"

                return output
            else:
                output = "✗ Not eligible for this product.\n"
                output += f"Reasons: {', '.join(result['reasons'])}"
                return output

        @tool
        async def generate_quote(
            product_id: str,
            age: int,
            state: str,
            zip_code: str,
            coverage_amount: int = 50000,
            dependents: int = 0,
        ) -> str:
            """
            Generate a price quote for an insurance product.

            Args:
                product_id: Product identifier
                age: Consumer age
                state: State of residence
                zip_code: ZIP code
                coverage_amount: Desired coverage amount in dollars
                dependents: Number of dependents to cover

            Returns:
                Quote details with pricing
            """
            # Create consumer
            from datetime import date, datetime
            from uuid import uuid4

            from ..models import ConsumerProfile

            birth_year = datetime.now().year - age

            consumer = Consumer(
                id=str(uuid4()),
                first_name="User",
                last_name="",
                email="user@example.com",
                date_of_birth=date(birth_year, 1, 1),
                profile=ConsumerProfile(
                    age=age, state=state, zip_code=zip_code
                ),
            )

            quote_request = QuoteRequest(
                product_id=product_id,
                consumer_id=consumer.id,
                coverage_amount=Decimal(str(coverage_amount)),
                dependents=dependents,
            )

            result = await _generate_quote(
                self.product_registry,
                self.provider_registry,
                quote_request,
                consumer,
            )

            if result["success"]:
                q = result["quote"]
                output = "Quote Generated:\n"
                output += f"• Monthly Premium: ${q['monthly_premium']}\n"
                output += f"• Coverage Amount: ${q['coverage_amount']}\n"
                output += f"• Deductible: ${q['deductible']}\n"
                output += f"• Quote ID: {q['quote_id']}\n"
                return output
            else:
                return f"Failed to generate quote: {result.get('error')}"

        @tool
        async def get_cross_sell_products(product_id: str) -> str:
            """
            Get cross-sell product recommendations for a given product.

            Args:
                product_id: Current product identifier

            Returns:
                List of recommended related products
            """
            results = await _get_cross_sell(self.product_registry, product_id)

            if not results:
                return "No cross-sell recommendations available."

            output = "Recommended products:\n"
            for p in results:
                output += f"\n• {p['name']} ({p['category']})"
                output += f"\n  ID: {p['id']}"
                output += f"\n  {p['description']}\n"

            return output

        return [
            search_products,
            check_eligibility,
            generate_quote,
            get_cross_sell_products,
        ]

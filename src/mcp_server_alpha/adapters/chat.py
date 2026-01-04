"""Chat channel adapter."""
from typing import Any

from .base import BaseAdapter


class ChatAdapter(BaseAdapter):
    """Adapter for chat-based channels."""

    async def format_product_list(self, products: list[dict[str, Any]]) -> str:
        """Format product list for chat."""
        if not products:
            return "No products found matching your criteria."

        lines = ["Here are the available products:"]
        for i, product in enumerate(products, 1):
            lines.append(
                f"\n{i}. **{product['name']}** ({product['category']})"
                f"\n   Provider: {product['provider_id']}"
                f"\n   {product['description']}"
            )

        return "\n".join(lines)

    async def format_eligibility_result(self, result: dict[str, Any]) -> str:
        """Format eligibility check result for chat."""
        if result["eligible"]:
            msg = "✓ You are eligible for this product!\n"

            if result.get("disclaimers"):
                msg += "\n" + await self.format_disclaimers(result["disclaimers"])

            if result.get("enrollment_steps"):
                msg += "\n\n**Enrollment Process:**"
                for step in result["enrollment_steps"]:
                    msg += f"\n• {step['name']}: {step['description']}"

            return msg
        else:
            msg = "✗ You are not eligible for this product.\n\n**Reasons:**"
            for reason in result.get("reasons", []):
                msg += f"\n• {reason}"
            return msg

    async def format_quote(self, quote: dict[str, Any]) -> str:
        """Format quote for chat."""
        if not quote.get("success"):
            return f"Unable to generate quote: {quote.get('error', 'Unknown error')}"

        q = quote["quote"]
        msg = f"""**Quote Generated** (ID: {q['quote_id']})

**Monthly Premium:** ${q['monthly_premium']}"""

        if q.get("deductible"):
            msg += f"\n**Deductible:** ${q['deductible']}"

        if q.get("coverage_amount"):
            msg += f"\n**Coverage Amount:** ${q['coverage_amount']}"

        msg += f"\n**Effective Date:** {q['effective_date']}"
        msg += f"\n**Quote Valid Until:** {q['expiration_date']}"

        if q.get("details"):
            msg += "\n\n**Details:**"
            for key, value in q["details"].items():
                msg += f"\n• {key.replace('_', ' ').title()}: {value}"

        return msg

    async def format_enrollment_response(self, response: dict[str, Any]) -> str:
        """Format enrollment response for chat."""
        if not response.get("success"):
            return f"Enrollment failed: {response.get('error', 'Unknown error')}"

        msg = f"""✓ **Enrollment Initiated**

**Enrollment ID:** {response['enrollment_id']}
**Status:** {response['status']}"""

        if response.get("next_steps"):
            msg += "\n\n**Next Steps:**"
            for step in response["next_steps"]:
                msg += f"\n• {step}"

        if response.get("estimated_completion"):
            msg += f"\n\n**Estimated Completion:** {response['estimated_completion']}"

        return msg

    async def format_disclaimers(self, disclaimers: list[dict[str, Any]]) -> str:
        """Format disclaimers for chat."""
        if not disclaimers:
            return ""

        msg = "**Important Information:**"
        for disclaimer in disclaimers:
            required = " (Acknowledgment Required)" if disclaimer["required_acknowledgment"] else ""
            msg += f"\n\n**{disclaimer['title']}**{required}\n{disclaimer['content']}"

        return msg

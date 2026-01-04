"""Base adapter interface."""
from abc import ABC, abstractmethod
from typing import Any


class BaseAdapter(ABC):
    """Base interface for channel adapters (chat, voice, SMS, etc.)."""

    @abstractmethod
    async def format_product_list(self, products: list[dict[str, Any]]) -> str:
        """Format product list for the channel."""
        pass

    @abstractmethod
    async def format_eligibility_result(self, result: dict[str, Any]) -> str:
        """Format eligibility check result for the channel."""
        pass

    @abstractmethod
    async def format_quote(self, quote: dict[str, Any]) -> str:
        """Format quote for the channel."""
        pass

    @abstractmethod
    async def format_enrollment_response(self, response: dict[str, Any]) -> str:
        """Format enrollment response for the channel."""
        pass

    @abstractmethod
    async def format_disclaimers(self, disclaimers: list[dict[str, Any]]) -> str:
        """Format disclaimers for the channel."""
        pass

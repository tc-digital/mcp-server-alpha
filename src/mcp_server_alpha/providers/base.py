"""Base provider interface and registry."""
from abc import ABC, abstractmethod
from typing import Any

from ..models import Consumer, Product, Quote, QuoteRequest


class BaseProvider(ABC):
    """Base interface for insurance providers/carriers."""

    def __init__(self, provider_id: str, config: dict[str, Any] | None = None):
        """Initialize provider."""
        self.provider_id = provider_id
        self.config = config or {}

    @abstractmethod
    async def check_eligibility(
        self, product: Product, consumer: Consumer
    ) -> tuple[bool, list[str]]:
        """
        Check if consumer is eligible for product with this provider.

        Returns:
            Tuple of (is_eligible, reasons)
        """
        pass

    @abstractmethod
    async def get_quote(self, quote_request: QuoteRequest, consumer: Consumer) -> Quote:
        """
        Get a quote from the provider.

        Args:
            quote_request: Quote request details
            consumer: Consumer information

        Returns:
            Quote object
        """
        pass

    @abstractmethod
    async def initiate_enrollment(
        self, quote: Quote, consumer: Consumer, enrollment_data: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Initiate enrollment process with provider.

        Args:
            quote: Approved quote
            consumer: Consumer information
            enrollment_data: Additional enrollment data

        Returns:
            Enrollment response with status and next steps
        """
        pass

    @abstractmethod
    async def get_enrollment_status(self, enrollment_id: str) -> dict[str, Any]:
        """
        Get status of enrollment.

        Args:
            enrollment_id: Enrollment identifier

        Returns:
            Status information
        """
        pass


class ProviderRegistry:
    """Registry for managing provider instances."""

    def __init__(self) -> None:
        """Initialize registry."""
        self._providers: dict[str, BaseProvider] = {}

    def register(self, provider: BaseProvider) -> None:
        """Register a provider."""
        self._providers[provider.provider_id] = provider

    def get(self, provider_id: str) -> BaseProvider | None:
        """Get a provider by ID."""
        return self._providers.get(provider_id)

    def list_providers(self) -> list[str]:
        """List all registered provider IDs."""
        return list(self._providers.keys())

    def clear(self) -> None:
        """Clear all providers (useful for testing)."""
        self._providers.clear()

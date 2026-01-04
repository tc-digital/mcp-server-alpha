"""Configuration loader and product registry."""
import json
from pathlib import Path

import yaml

from ..models import Product


class ProductRegistry:
    """Registry for managing product definitions."""

    def __init__(self) -> None:
        """Initialize registry."""
        self._products: dict[str, Product] = {}

    def register(self, product: Product) -> None:
        """Register a product."""
        self._products[product.id] = product

    def get(self, product_id: str) -> Product | None:
        """Get a product by ID."""
        return self._products.get(product_id)

    def list_products(
        self,
        category: str | None = None,
        provider_id: str | None = None,
        active_only: bool = True,
    ) -> list[Product]:
        """
        List products with optional filters.

        Args:
            category: Filter by category
            provider_id: Filter by provider
            active_only: Only return active products

        Returns:
            List of matching products
        """
        products = list(self._products.values())

        if active_only:
            products = [p for p in products if p.active]

        if category:
            products = [p for p in products if p.category == category]

        if provider_id:
            products = [p for p in products if p.provider_id == provider_id]

        return products

    def get_cross_sell_products(self, product_id: str) -> list[Product]:
        """Get cross-sell products for a given product."""
        product = self.get(product_id)
        if not product:
            return []

        cross_sell_ids = product.cross_sell_products
        return [p for p in self._products.values() if p.id in cross_sell_ids and p.active]

    def clear(self) -> None:
        """Clear all products (useful for testing)."""
        self._products.clear()


class ConfigLoader:
    """Load product configurations from files."""

    @staticmethod
    def load_from_file(file_path: Path) -> Product:
        """
        Load a product from a JSON or YAML file.

        Args:
            file_path: Path to config file

        Returns:
            Product instance
        """
        with open(file_path) as f:
            if file_path.suffix in [".yaml", ".yml"]:
                data = yaml.safe_load(f)
            else:
                data = json.load(f)

        return Product(**data)

    @staticmethod
    def load_from_directory(dir_path: Path, registry: ProductRegistry) -> None:
        """
        Load all products from a directory.

        Args:
            dir_path: Directory containing product config files
            registry: ProductRegistry to register products in
        """
        if not dir_path.exists():
            return

        for file_path in dir_path.glob("*.json"):
            try:
                product = ConfigLoader.load_from_file(file_path)
                registry.register(product)
            except Exception as e:
                print(f"Error loading product from {file_path}: {e}")

        for file_path in dir_path.glob("*.yaml"):
            try:
                product = ConfigLoader.load_from_file(file_path)
                registry.register(product)
            except Exception as e:
                print(f"Error loading product from {file_path}: {e}")

        for file_path in dir_path.glob("*.yml"):
            try:
                product = ConfigLoader.load_from_file(file_path)
                registry.register(product)
            except Exception as e:
                print(f"Error loading product from {file_path}: {e}")

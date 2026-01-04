"""Unit tests for configuration management."""
import json
import tempfile
from pathlib import Path

import pytest

from mcp_server_alpha.config import ConfigLoader, ProductRegistry
from mcp_server_alpha.models import Product, ProductCategory


@pytest.fixture
def product_registry():
    """Create a fresh product registry."""
    registry = ProductRegistry()
    yield registry
    registry.clear()


@pytest.fixture
def sample_product():
    """Create a sample product."""
    return Product(
        id="test-001",
        name="Test Product",
        category=ProductCategory.HEALTH,
        provider_id="test_provider",
        description="Test product",
        active=True,
    )


def test_product_registry_register_get(product_registry, sample_product):
    """Test registering and getting products."""
    product_registry.register(sample_product)

    retrieved = product_registry.get("test-001")
    assert retrieved is not None
    assert retrieved.id == "test-001"
    assert retrieved.name == "Test Product"


def test_product_registry_list_all(product_registry):
    """Test listing all products."""
    product1 = Product(
        id="health-001",
        name="Health Plan",
        category=ProductCategory.HEALTH,
        provider_id="provider1",
        description="Health insurance",
        active=True,
    )
    product2 = Product(
        id="dental-001",
        name="Dental Plan",
        category=ProductCategory.DENTAL,
        provider_id="provider1",
        description="Dental insurance",
        active=True,
    )

    product_registry.register(product1)
    product_registry.register(product2)

    all_products = product_registry.list_products()
    assert len(all_products) == 2


def test_product_registry_filter_by_category(product_registry):
    """Test filtering products by category."""
    product1 = Product(
        id="health-001",
        name="Health Plan",
        category=ProductCategory.HEALTH,
        provider_id="provider1",
        description="Health insurance",
        active=True,
    )
    product2 = Product(
        id="dental-001",
        name="Dental Plan",
        category=ProductCategory.DENTAL,
        provider_id="provider1",
        description="Dental insurance",
        active=True,
    )

    product_registry.register(product1)
    product_registry.register(product2)

    health_products = product_registry.list_products(category="health")
    assert len(health_products) == 1
    assert health_products[0].category == ProductCategory.HEALTH


def test_product_registry_filter_by_provider(product_registry):
    """Test filtering products by provider."""
    product1 = Product(
        id="health-001",
        name="Health Plan 1",
        category=ProductCategory.HEALTH,
        provider_id="provider1",
        description="Health insurance",
        active=True,
    )
    product2 = Product(
        id="health-002",
        name="Health Plan 2",
        category=ProductCategory.HEALTH,
        provider_id="provider2",
        description="Health insurance",
        active=True,
    )

    product_registry.register(product1)
    product_registry.register(product2)

    provider1_products = product_registry.list_products(provider_id="provider1")
    assert len(provider1_products) == 1
    assert provider1_products[0].provider_id == "provider1"


def test_product_registry_active_only(product_registry):
    """Test filtering active products only."""
    product1 = Product(
        id="health-001",
        name="Health Plan",
        category=ProductCategory.HEALTH,
        provider_id="provider1",
        description="Health insurance",
        active=True,
    )
    product2 = Product(
        id="health-002",
        name="Old Health Plan",
        category=ProductCategory.HEALTH,
        provider_id="provider1",
        description="Discontinued",
        active=False,
    )

    product_registry.register(product1)
    product_registry.register(product2)

    active_products = product_registry.list_products(active_only=True)
    assert len(active_products) == 1
    assert active_products[0].active is True

    all_products = product_registry.list_products(active_only=False)
    assert len(all_products) == 2


def test_product_registry_cross_sell(product_registry):
    """Test getting cross-sell products."""
    product1 = Product(
        id="health-001",
        name="Health Plan",
        category=ProductCategory.HEALTH,
        provider_id="provider1",
        description="Health insurance",
        cross_sell_products=["dental-001", "vision-001"],
        active=True,
    )
    product2 = Product(
        id="dental-001",
        name="Dental Plan",
        category=ProductCategory.DENTAL,
        provider_id="provider1",
        description="Dental insurance",
        active=True,
    )
    product3 = Product(
        id="vision-001",
        name="Vision Plan",
        category=ProductCategory.VISION,
        provider_id="provider1",
        description="Vision insurance",
        active=True,
    )

    product_registry.register(product1)
    product_registry.register(product2)
    product_registry.register(product3)

    cross_sell = product_registry.get_cross_sell_products("health-001")
    assert len(cross_sell) == 2


def test_config_loader_from_file(product_registry):
    """Test loading product from JSON file."""
    product_data = {
        "id": "test-001",
        "name": "Test Product",
        "category": "health",
        "provider_id": "test_provider",
        "description": "Test product",
        "active": True,
        "eligibility_rules": [],
        "disclaimers": [],
        "enrollment_flow": [],
        "cross_sell_products": [],
        "metadata": {},
    }

    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(product_data, f)
        temp_path = Path(f.name)

    try:
        product = ConfigLoader.load_from_file(temp_path)
        assert product.id == "test-001"
        assert product.name == "Test Product"
        assert product.category == ProductCategory.HEALTH
    finally:
        temp_path.unlink()


def test_config_loader_from_directory(product_registry):
    """Test loading products from directory."""
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        # Create two product files
        product1_data = {
            "id": "health-001",
            "name": "Health Plan",
            "category": "health",
            "provider_id": "provider1",
            "description": "Health insurance",
            "active": True,
            "eligibility_rules": [],
            "disclaimers": [],
            "enrollment_flow": [],
            "cross_sell_products": [],
            "metadata": {},
        }

        product2_data = {
            "id": "dental-001",
            "name": "Dental Plan",
            "category": "dental",
            "provider_id": "provider1",
            "description": "Dental insurance",
            "active": True,
            "eligibility_rules": [],
            "disclaimers": [],
            "enrollment_flow": [],
            "cross_sell_products": [],
            "metadata": {},
        }

        with open(temp_path / "health-001.json", "w") as f:
            json.dump(product1_data, f)

        with open(temp_path / "dental-001.json", "w") as f:
            json.dump(product2_data, f)

        ConfigLoader.load_from_directory(temp_path, product_registry)

        assert product_registry.get("health-001") is not None
        assert product_registry.get("dental-001") is not None
        assert len(product_registry.list_products()) == 2

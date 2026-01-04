"""Unit tests for product models."""
import pytest

from mcp_server_alpha.models import (
    Disclaimer,
    EligibilityRule,
    Product,
    ProductCategory,
    Qualifier,
)


def test_qualifier_evaluation():
    """Test qualifier evaluation logic."""
    qualifier = Qualifier(
        name="age_check",
        description="Must be 18 or older",
        field="age",
        operator="gte",
        value=18,
    )

    assert qualifier.evaluate({"age": 25}) is True
    assert qualifier.evaluate({"age": 18}) is True
    assert qualifier.evaluate({"age": 17}) is False
    assert qualifier.evaluate({"age": None}) is False
    assert qualifier.evaluate({}) is False


def test_qualifier_operators():
    """Test different qualifier operators."""
    test_cases = [
        ({"field": "age", "operator": "eq", "value": 30}, {"age": 30}, True),
        ({"field": "age", "operator": "ne", "value": 30}, {"age": 25}, True),
        ({"field": "age", "operator": "gt", "value": 30}, {"age": 35}, True),
        ({"field": "age", "operator": "lt", "value": 30}, {"age": 25}, True),
        ({"field": "state", "operator": "in", "value": ["CA", "NY"]}, {"state": "CA"}, True),
        ({"field": "state", "operator": "in", "value": ["CA", "NY"]}, {"state": "TX"}, False),
    ]

    for qualifier_data, consumer_data, expected in test_cases:
        qualifier = Qualifier(
            name="test", description="test", **qualifier_data
        )
        assert qualifier.evaluate(consumer_data) == expected


def test_eligibility_rule_all_logic():
    """Test eligibility rule with 'all' logic."""
    rule = EligibilityRule(
        name="age_range",
        description="Age between 18 and 64",
        qualifiers=[
            Qualifier(
                name="min_age",
                description="At least 18",
                field="age",
                operator="gte",
                value=18,
            ),
            Qualifier(
                name="max_age",
                description="Under 65",
                field="age",
                operator="lt",
                value=65,
            ),
        ],
        logic="all",
    )

    is_eligible, reasons = rule.evaluate({"age": 30})
    assert is_eligible is True
    assert len(reasons) == 0

    is_eligible, reasons = rule.evaluate({"age": 17})
    assert is_eligible is False
    assert len(reasons) > 0

    is_eligible, reasons = rule.evaluate({"age": 65})
    assert is_eligible is False
    assert len(reasons) > 0


def test_eligibility_rule_any_logic():
    """Test eligibility rule with 'any' logic."""
    rule = EligibilityRule(
        name="state_check",
        description="In eligible states",
        qualifiers=[
            Qualifier(
                name="california",
                description="California resident",
                field="state",
                operator="eq",
                value="CA",
            ),
            Qualifier(
                name="new_york",
                description="New York resident",
                field="state",
                operator="eq",
                value="NY",
            ),
        ],
        logic="any",
    )

    is_eligible, reasons = rule.evaluate({"state": "CA"})
    assert is_eligible is True

    is_eligible, reasons = rule.evaluate({"state": "NY"})
    assert is_eligible is True

    is_eligible, reasons = rule.evaluate({"state": "TX"})
    assert is_eligible is False


def test_product_eligibility():
    """Test product eligibility checking."""
    product = Product(
        id="test-001",
        name="Test Product",
        category=ProductCategory.HEALTH,
        provider_id="test_provider",
        description="Test product",
        eligibility_rules=[
            EligibilityRule(
                name="age_requirement",
                description="Age 18+",
                qualifiers=[
                    Qualifier(
                        name="min_age",
                        description="At least 18",
                        field="age",
                        operator="gte",
                        value=18,
                    )
                ],
                logic="all",
            )
        ],
    )

    is_eligible, reasons = product.check_eligibility({"age": 25})
    assert is_eligible is True
    assert len(reasons) == 0

    is_eligible, reasons = product.check_eligibility({"age": 17})
    assert is_eligible is False
    assert len(reasons) > 0


def test_product_cross_sell():
    """Test product cross-sell configuration."""
    product = Product(
        id="health-001",
        name="Health Plan",
        category=ProductCategory.HEALTH,
        provider_id="test_provider",
        description="Health insurance",
        cross_sell_products=["dental-001", "vision-001"],
    )

    assert len(product.cross_sell_products) == 2
    assert "dental-001" in product.cross_sell_products

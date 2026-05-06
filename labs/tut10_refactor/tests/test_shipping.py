# tests/test_shipping.py
import pytest
from src.shipping import calculate_shipping


# --- happy paths ---

@pytest.mark.parametrize("zone,service,weight,expected", [
    (1, "standard", 2.0, 7.00),
    (1, "express", 2.0, 13.00),
    (1, "overnight", 2.0, 24.00),
    (2, "standard", 3.0, 11.60),
    (2, "express", 3.0, 19.40),
    (3, "overnight", 1.5, 34.50),
    ("international", "standard", 5.0, 40.00),
    ("international", "express", 5.0, 60.00),
])
def test_base_costs(zone, service, weight, expected):
    assert calculate_shipping(weight, zone, service) == expected


# --- modifiers ---

def test_member_discount_applied():
    assert calculate_shipping(2.0, 1, "standard", is_member=True) == 6.30


def test_insurance_surcharge_applied():
    assert calculate_shipping(2.0, 1, "standard", has_insurance=True) == 7.35


def test_holiday_surcharge_applied():
    assert calculate_shipping(2.0, 1, "standard", is_holiday=True) == 8.40


def test_all_modifiers_combine():
    # base 7.00 -> member 6.30 -> insurance 6.615 -> holiday 7.938 -> 7.94
    assert calculate_shipping(
        2.0, 1, "standard",
        is_member=True, has_insurance=True, is_holiday=True,
    ) == 7.94


# --- error paths ---

@pytest.mark.parametrize("weight", [0, -1.0, None])
def test_invalid_weight_raises(weight):
    with pytest.raises(ValueError, match="weight must be positive"):
        calculate_shipping(weight, 1, "standard")


def test_invalid_zone_raises():
    with pytest.raises(ValueError, match="invalid zone"):
        calculate_shipping(2.0, 99, "standard")


def test_invalid_service_raises():
    with pytest.raises(ValueError, match="invalid service"):
        calculate_shipping(2.0, 1, "teleport")


def test_overnight_international_rejected():
    with pytest.raises(ValueError, match="overnight is not available"):
        calculate_shipping(2.0, "international", "overnight")


# --- estimate_delivery_days (Step 5 activity) ---
from src.shipping import estimate_delivery_days


@pytest.mark.parametrize("zone,service,expected_days", [
    (1, "standard", 3),
    (1, "overnight", 1),
    (2, "express", 3),
    (3, "standard", 7),
    ("international", "express", 7),
])
def test_delivery_days(zone, service, expected_days):
    assert estimate_delivery_days(zone, service) == expected_days


def test_delivery_days_holiday_adds_two():
    assert estimate_delivery_days(1, "standard", is_holiday=True) == 5


def test_delivery_days_remote_adds_three():
    assert estimate_delivery_days(1, "standard", is_remote=True) == 6


def test_delivery_days_invalid_zone():
    with pytest.raises(ValueError, match="invalid zone"):
        estimate_delivery_days(99, "standard")


def test_delivery_days_overnight_international_rejected():
    with pytest.raises(ValueError):
        estimate_delivery_days("international", "overnight")

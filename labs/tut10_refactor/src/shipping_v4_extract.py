# src/shipping.py
"""Calculates parcel shipping cost."""

VALID_ZONES = (1, 2, 3, "international")
VALID_SERVICES = ("standard", "express", "overnight")

RATES = {
    (1, "standard"): (5.00, 1.00),
    (1, "express"): (10.00, 1.50),
    (1, "overnight"): (20.00, 2.00),
    (2, "standard"): (8.00, 1.20),
    (2, "express"): (14.00, 1.80),
    (2, "overnight"): (25.00, 2.50),
    (3, "standard"): (12.00, 1.50),
    (3, "express"): (18.00, 2.20),
    (3, "overnight"): (30.00, 3.00),
    ("international", "standard"): (25.00, 3.00),
    ("international", "express"): (40.00, 4.00),
}


def _validate(weight, zone, service):
    if weight is None or weight <= 0:
        raise ValueError("weight must be positive")
    if zone not in VALID_ZONES:
        raise ValueError(f"invalid zone: {zone}")
    if service not in VALID_SERVICES:
        raise ValueError(f"invalid service: {service}")
    if zone == "international" and service == "overnight":
        raise ValueError("overnight is not available internationally")


def _apply_modifiers(cost, is_member, has_insurance, is_holiday):
    if is_member:
        cost *= 0.90
    if has_insurance:
        cost *= 1.05
    if is_holiday:
        cost *= 1.20
    return cost


def calculate_shipping(
    weight, zone, service,
    is_member=False, has_insurance=False, is_holiday=False,
):
    _validate(weight, zone, service)
    base, per_kg = RATES[(zone, service)]
    cost = base + weight * per_kg
    cost = _apply_modifiers(cost, is_member, has_insurance, is_holiday)
    return round(cost, 2)

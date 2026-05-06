# src/shipping.py
"""Calculates parcel shipping cost. Refactor target."""


def calculate_shipping(
    weight, zone, service,
    is_member=False, has_insurance=False, is_holiday=False,
):
    if weight is None or weight <= 0:
        raise ValueError("weight must be positive")
    if zone not in (1, 2, 3, "international"):
        raise ValueError(f"invalid zone: {zone}")

    cost = 0.0
    if zone == 1:
        if service == "standard":
            cost = 5.00 + weight * 1.00
        elif service == "express":
            cost = 10.00 + weight * 1.50
        elif service == "overnight":
            cost = 20.00 + weight * 2.00
        else:
            raise ValueError(f"invalid service: {service}")
    elif zone == 2:
        if service == "standard":
            cost = 8.00 + weight * 1.20
        elif service == "express":
            cost = 14.00 + weight * 1.80
        elif service == "overnight":
            cost = 25.00 + weight * 2.50
        else:
            raise ValueError(f"invalid service: {service}")
    elif zone == 3:
        if service == "standard":
            cost = 12.00 + weight * 1.50
        elif service == "express":
            cost = 18.00 + weight * 2.20
        elif service == "overnight":
            cost = 30.00 + weight * 3.00
        else:
            raise ValueError(f"invalid service: {service}")
    elif zone == "international":
        if service == "standard":
            cost = 25.00 + weight * 3.00
        elif service == "express":
            cost = 40.00 + weight * 4.00
        elif service == "overnight":
            raise ValueError("overnight is not available internationally")
        else:
            raise ValueError(f"invalid service: {service}")

    if is_member:
        cost = cost * 0.90
    if has_insurance:
        cost = cost * 1.05
    if is_holiday:
        cost = cost * 1.20

    return round(cost, 2)

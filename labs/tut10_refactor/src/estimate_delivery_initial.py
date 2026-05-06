# src/shipping.py — append (Step 5 activity)

def estimate_delivery_days(zone, service, is_holiday=False, is_remote=False):
    if zone is None or service is None:
        raise ValueError("zone and service required")
    if zone == 1:
        if service == "standard":
            days = 3
        elif service == "express":
            days = 2
        elif service == "overnight":
            days = 1
        else:
            raise ValueError(f"invalid service: {service}")
    elif zone == 2:
        if service == "standard":
            days = 5
        elif service == "express":
            days = 3
        elif service == "overnight":
            days = 1
        else:
            raise ValueError(f"invalid service: {service}")
    elif zone == 3:
        if service == "standard":
            days = 7
        elif service == "express":
            days = 4
        elif service == "overnight":
            days = 2
        else:
            raise ValueError(f"invalid service: {service}")
    elif zone == "international":
        if service == "standard":
            days = 14
        elif service == "express":
            days = 7
        elif service == "overnight":
            raise ValueError("overnight is not available internationally")
        else:
            raise ValueError(f"invalid service: {service}")
    else:
        raise ValueError(f"invalid zone: {zone}")

    if is_holiday:
        days += 2
    if is_remote:
        days += 3
    return days

# src/tax.py

LOW_INCOME_THRESHOLD = 18_200
MID_INCOME_THRESHOLD = 37_000
SENIOR_AGE = 67


def calculate_deduction(
    income: float,
    age: int,
    has_spouse: bool,
    disabled: bool,
) -> float:
    """Calculate the ATO tax deduction for a taxpayer.

    Args:
        income: Annual taxable income in AUD.
        age: Taxpayer's age in years.
        has_spouse: True if the taxpayer claims the spouse offset.
        disabled: True if the taxpayer claims the disability supplement.

    Returns:
        Total deduction amount in AUD.

    Raises:
        ValueError: If income is negative.
    """
    if income < 0:
        raise ValueError("Income cannot be negative")

    deduction = 0.0

    if income <= LOW_INCOME_THRESHOLD:
        deduction += 700.0
    elif income <= MID_INCOME_THRESHOLD:
        deduction += 300.0

    if age >= SENIOR_AGE:
        deduction += 400.0

    if has_spouse:
        deduction += 200.0

    if disabled:
        deduction += 600.0

    return deduction

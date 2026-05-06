# test_pii_guard.py
from pii_guard import safe_prompt

# Should block — contains an email address
try:
    safe_prompt("Fix the bug reported by john.doe@example.com in the checkout flow")
    print("FAIL: should have raised ValueError")
except ValueError as e:
    print(f"Blocked (expected): {e}")

# Should pass — no PII
result = safe_prompt("Fix the null pointer exception in the checkout flow")
print(f"Passed (expected): returned {len(result)} chars")

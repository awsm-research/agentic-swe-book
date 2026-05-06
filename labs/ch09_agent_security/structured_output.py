from pydantic import BaseModel

class CodeReviewResult(BaseModel):
    summary: str
    issues: list[dict]  # {"severity": "blocker|warning|suggestion", "location": str, "description": str}
    verdict: str  # "approve" | "request_changes" | "needs_discussion"
    security_flags: list[str]

# Require the agent to produce this exact structure
# Injection attempts that generate free-form text will fail schema validation

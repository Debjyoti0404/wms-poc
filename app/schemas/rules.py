from decimal import Decimal

from pydantic import BaseModel, Field


class RuleValidateAssignmentRequest(BaseModel):
    mission_id: int
    executor_id: int


class RuleValidateMovementRequest(BaseModel):
    mission_id: int
    mission_line_id: int
    executor_id: int
    qty: Decimal = Field(gt=0)


class RuleValidationResponse(BaseModel):
    allowed: bool
    reason: str | None = None

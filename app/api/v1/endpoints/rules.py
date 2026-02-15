from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.repositories.executor import ExecutorRepository
from app.repositories.handling_unit import HandlingUnitRepository
from app.repositories.location import LocationRepository
from app.repositories.mission import MissionRepository
from app.rules.mission_rules import validate_assign
from app.rules.movement_rules import validate_movement
from app.schemas.rules import (
    RuleValidateAssignmentRequest,
    RuleValidateMovementRequest,
    RuleValidationResponse,
)

router = APIRouter(prefix="/rules")


@router.post("/validate-assignment", response_model=RuleValidationResponse)
def validate_assignment(
    payload: RuleValidateAssignmentRequest,
    db: Session = Depends(get_db),
) -> RuleValidationResponse:
    missions = MissionRepository(db)
    executors = ExecutorRepository(db)

    mission = missions.get_with_lines(payload.mission_id)
    executor = executors.get(payload.executor_id)
    if mission is None or executor is None:
        return RuleValidationResponse(allowed=False, reason="Mission or executor not found")

    try:
        validate_assign(mission, executor)
        return RuleValidationResponse(allowed=True)
    except Exception as exc:
        return RuleValidationResponse(allowed=False, reason=str(exc))


@router.post("/validate-movement", response_model=RuleValidationResponse)
def validate_movement_rule(
    payload: RuleValidateMovementRequest,
    db: Session = Depends(get_db),
) -> RuleValidationResponse:
    missions = MissionRepository(db)
    executors = ExecutorRepository(db)
    locations = LocationRepository(db)
    handling_units = HandlingUnitRepository(db)

    mission = missions.get_with_lines(payload.mission_id)
    mission_line = missions.get_line(payload.mission_line_id)
    executor = executors.get(payload.executor_id)
    if mission is None or mission_line is None or executor is None:
        return RuleValidationResponse(allowed=False, reason="Mission, line, or executor not found")

    source = locations.get(mission_line.from_location_id)
    destination = locations.get(mission_line.to_location_id)
    if source is None or destination is None:
        return RuleValidationResponse(allowed=False, reason="Mission line locations not found")

    handling_unit = handling_units.get(mission_line.hu_id) if mission_line.hu_id is not None else None

    try:
        validate_movement(
            mission=mission,
            mission_line=mission_line,
            executor=executor,
            source_location=source,
            destination_location=destination,
            qty=payload.qty,
            handling_unit=handling_unit,
        )
        return RuleValidationResponse(allowed=True)
    except Exception as exc:
        return RuleValidationResponse(allowed=False, reason=str(exc))

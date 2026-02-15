from decimal import Decimal

from app.db.models.executor import Executor, ExecutorType
from app.db.models.handling_unit import HandlingUnit, HandlingUnitStatus
from app.db.models.location import Location
from app.db.models.mission import Mission, MissionLine, MissionState
from app.rules.exceptions import RuleViolation


def validate_movement(
    *,
    mission: Mission,
    mission_line: MissionLine,
    executor: Executor,
    source_location: Location,
    destination_location: Location,
    qty: Decimal,
    handling_unit: HandlingUnit | None,
) -> None:
    if mission.state != MissionState.IN_PROGRESS:
        raise RuleViolation("Mission must be in progress to record movement")

    if mission_line.mission_id != mission.id:
        raise RuleViolation("Mission line does not belong to mission")

    if qty <= 0:
        raise RuleViolation("Movement qty must be positive")

    remaining_qty = Decimal(str(mission_line.qty)) - Decimal(str(mission_line.qty_done))
    if qty > remaining_qty:
        raise RuleViolation("Movement qty exceeds remaining mission line qty")

    if not executor.active:
        raise RuleViolation("Executor is inactive")

    if executor.executor_type == ExecutorType.HUMAN and qty > Decimal("500"):
        raise RuleViolation("Human executor cannot carry payload above 500kg")

    if qty > Decimal(str(executor.max_payload_kg)):
        raise RuleViolation("Payload exceeds executor max payload")

    if not source_location.active or not destination_location.active:
        raise RuleViolation("Source and destination locations must be active")

    if source_location.id == destination_location.id:
        raise RuleViolation("Source and destination must be different")

    if handling_unit is not None:
        if handling_unit.location_id != source_location.id:
            raise RuleViolation("Handling unit is not at source location")
        if handling_unit.status in {HandlingUnitStatus.BLOCKED, HandlingUnitStatus.SEALED}:
            raise RuleViolation("Blocked or sealed handling unit cannot be moved")

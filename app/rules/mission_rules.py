from app.db.models.executor import Executor
from app.db.models.mission import Mission, MissionState
from app.rules.exceptions import RuleViolation

_ALLOWED_TRANSITIONS = {
    MissionState.DRAFT: {MissionState.ASSIGNED, MissionState.CANCELLED},
    MissionState.ASSIGNED: {MissionState.IN_PROGRESS, MissionState.CANCELLED},
    MissionState.IN_PROGRESS: {MissionState.COMPLETED, MissionState.CANCELLED},
    MissionState.COMPLETED: set(),
    MissionState.CANCELLED: set(),
}


def ensure_transition(current: MissionState, target: MissionState) -> None:
    if target not in _ALLOWED_TRANSITIONS[current]:
        raise RuleViolation(f"Invalid mission transition: {current.value} -> {target.value}")


def validate_assign(mission: Mission, executor: Executor) -> None:
    ensure_transition(mission.state, MissionState.ASSIGNED)
    if not executor.active:
        raise RuleViolation("Executor is inactive")
    if not mission.lines:
        raise RuleViolation("Mission must have at least one line before assignment")


def validate_start(mission: Mission, executor: Executor) -> None:
    ensure_transition(mission.state, MissionState.IN_PROGRESS)
    if mission.assigned_executor_id != executor.id:
        raise RuleViolation("Only the assigned executor can start this mission")
    if not executor.active:
        raise RuleViolation("Executor is inactive")


def validate_complete(mission: Mission) -> None:
    ensure_transition(mission.state, MissionState.COMPLETED)
    incomplete = [line.id for line in mission.lines if line.qty_done != line.qty]
    if incomplete:
        raise RuleViolation(f"All mission lines must be complete before finishing: {incomplete}")


def validate_cancel(mission: Mission, reason: str) -> None:
    if not reason.strip():
        raise RuleViolation("Cancel reason is required")
    if mission.state in {MissionState.COMPLETED, MissionState.CANCELLED}:
        raise RuleViolation("Completed or cancelled mission cannot be cancelled")

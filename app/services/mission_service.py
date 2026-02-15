from decimal import Decimal

from sqlalchemy.orm import Session

from app.db.models.inventory import InventoryMovement, InventoryMovementType
from app.db.models.mission import Mission
from app.repositories.executor import ExecutorRepository
from app.repositories.handling_unit import HandlingUnitRepository
from app.repositories.inventory import InventoryMovementRepository, InventoryPositionRepository
from app.repositories.location import LocationRepository
from app.repositories.mission import MissionRepository
from app.rules.exceptions import RuleViolation
from app.rules.mission_rules import validate_assign, validate_cancel, validate_complete, validate_start
from app.rules.movement_rules import validate_movement
from app.schemas.mission import MissionCreate, MissionRecordMovementCommand


class MissionService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.missions = MissionRepository(db)
        self.executors = ExecutorRepository(db)
        self.locations = LocationRepository(db)
        self.handling_units = HandlingUnitRepository(db)
        self.positions = InventoryPositionRepository(db)
        self.movements = InventoryMovementRepository(db)

    def create_mission(self, payload: MissionCreate) -> Mission:
        return self.missions.create(
            mission_no=payload.mission_no,
            type=payload.type,
            priority=payload.priority,
            created_by_operator_id=payload.created_by_operator_id,
            lines=[line.model_dump() for line in payload.lines],
        )

    def assign(self, mission_id: int, executor_id: int) -> Mission:
        mission = self.missions.get_with_lines(mission_id)
        if mission is None:
            raise RuleViolation("Mission not found", status_code=404)

        executor = self.executors.get(executor_id)
        if executor is None:
            raise RuleViolation("Executor not found", status_code=404)

        validate_assign(mission, executor)
        return self.missions.assign(mission, executor_id)

    def start(self, mission_id: int, executor_id: int) -> Mission:
        mission = self.missions.get_with_lines(mission_id)
        if mission is None:
            raise RuleViolation("Mission not found", status_code=404)

        executor = self.executors.get(executor_id)
        if executor is None:
            raise RuleViolation("Executor not found", status_code=404)

        validate_start(mission, executor)
        return self.missions.start(mission)

    def record_movement(self, mission_id: int, payload: MissionRecordMovementCommand) -> InventoryMovement:
        mission = self.missions.get_with_lines(mission_id)
        if mission is None:
            raise RuleViolation("Mission not found", status_code=404)

        mission_line = self.missions.get_line(payload.mission_line_id)
        if mission_line is None:
            raise RuleViolation("Mission line not found", status_code=404)

        executor = self.executors.get(payload.executor_id)
        if executor is None:
            raise RuleViolation("Executor not found", status_code=404)

        source_location = self.locations.get(mission_line.from_location_id)
        destination_location = self.locations.get(mission_line.to_location_id)
        if source_location is None or destination_location is None:
            raise RuleViolation("Mission line locations are invalid", status_code=400)

        idempotency_key = payload.idempotency_key
        if idempotency_key:
            existing = self.movements.get_by_idempotency_key(idempotency_key)
            if existing is not None:
                return existing

        handling_unit = None
        if mission_line.hu_id is not None:
            handling_unit = self.handling_units.get(mission_line.hu_id)
            if handling_unit is None:
                raise RuleViolation("Mission handling unit not found", status_code=404)

        validate_movement(
            mission=mission,
            mission_line=mission_line,
            executor=executor,
            source_location=source_location,
            destination_location=destination_location,
            qty=payload.qty,
            handling_unit=handling_unit,
        )

        if mission_line.item_id is None:
            if handling_unit is None:
                raise RuleViolation("HU movement requires handling unit")
            self.handling_units.update(handling_unit, location_id=destination_location.id)
            movement = self.movements.create(
                movement_type=InventoryMovementType.MOVE,
                item_id=None,
                qty=payload.qty,
                mission_line_id=mission_line.id,
                from_location_id=source_location.id,
                to_location_id=destination_location.id,
                from_hu_id=handling_unit.id,
                to_hu_id=handling_unit.id,
                executed_by_executor_id=executor.id,
                idempotency_key=idempotency_key,
            )
        else:
            from_hu_id = payload.from_hu_id or mission_line.hu_id
            to_hu_id = payload.to_hu_id or mission_line.hu_id
            if from_hu_id is None or to_hu_id is None:
                raise RuleViolation("Item movement requires from_hu_id and to_hu_id")

            from_hu = self.handling_units.get(from_hu_id)
            to_hu = self.handling_units.get(to_hu_id)
            if from_hu is None or to_hu is None:
                raise RuleViolation("from_hu_id and to_hu_id must reference existing handling units")
            if from_hu.location_id != source_location.id:
                raise RuleViolation("from_hu_id is not located at source location")
            if to_hu.location_id != destination_location.id:
                raise RuleViolation("to_hu_id is not located at destination location")

            source_position = self.positions.get_by_hu_item(from_hu_id, mission_line.item_id)
            if source_position is None:
                raise RuleViolation("Source inventory position not found")

            deducted = self.positions.update_qty_on_hand_if_version(
                position_id=source_position.id,
                expected_version=source_position.version,
                qty_delta=-payload.qty,
            )
            if not deducted:
                raise RuleViolation("Insufficient stock or concurrent source update")

            destination_position = self.positions.get_by_hu_item(to_hu_id, mission_line.item_id)
            if destination_position is None:
                destination_position = self.positions.create(
                    hu_id=to_hu_id,
                    item_id=mission_line.item_id,
                    qty_on_hand=Decimal("0"),
                )

            added = self.positions.update_qty_on_hand_if_version(
                position_id=destination_position.id,
                expected_version=destination_position.version,
                qty_delta=payload.qty,
            )
            if not added:
                raise RuleViolation("Concurrent destination update conflict")

            movement = self.movements.create(
                movement_type=InventoryMovementType.MOVE,
                item_id=mission_line.item_id,
                qty=payload.qty,
                mission_line_id=mission_line.id,
                from_location_id=source_location.id,
                to_location_id=destination_location.id,
                from_hu_id=from_hu_id,
                to_hu_id=to_hu_id,
                executed_by_executor_id=executor.id,
                idempotency_key=idempotency_key,
            )

        self.missions.increment_line_done(mission_line, payload.qty)
        return movement

    def complete(self, mission_id: int) -> Mission:
        mission = self.missions.get_with_lines(mission_id)
        if mission is None:
            raise RuleViolation("Mission not found", status_code=404)
        validate_complete(mission)
        return self.missions.complete(mission)

    def cancel(self, mission_id: int, reason: str) -> Mission:
        mission = self.missions.get_with_lines(mission_id)
        if mission is None:
            raise RuleViolation("Mission not found", status_code=404)
        validate_cancel(mission, reason)
        return self.missions.cancel(mission, reason)

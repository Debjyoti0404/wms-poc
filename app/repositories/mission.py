from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.db.models.inventory import InventoryMovement
from app.db.models.mission import Mission, MissionLine, MissionState, MissionType
from app.repositories.base import BaseRepository


class MissionRepository(BaseRepository):
    def create(
        self,
        *,
        mission_no: str,
        type: MissionType,
        priority: int,
        created_by_operator_id: int,
        lines: list[dict],
    ) -> Mission:
        mission = Mission(
            mission_no=mission_no,
            type=type,
            priority=priority,
            created_by_operator_id=created_by_operator_id,
            state=MissionState.DRAFT,
        )
        self.db.add(mission)
        self.db.flush()

        for line in lines:
            mission_line = MissionLine(
                mission_id=mission.id,
                from_location_id=line["from_location_id"],
                to_location_id=line["to_location_id"],
                item_id=line.get("item_id"),
                hu_id=line.get("hu_id"),
                qty=Decimal(str(line["qty"])),
                qty_done=Decimal("0"),
            )
            self.db.add(mission_line)

        self.db.flush()
        self.db.refresh(mission)
        return self.get_with_lines(mission.id) or mission

    def get(self, mission_id: int) -> Mission | None:
        return self.db.get(Mission, mission_id)

    def get_with_lines(self, mission_id: int) -> Mission | None:
        statement = (
            select(Mission)
            .options(selectinload(Mission.lines))
            .where(Mission.id == mission_id)
        )
        return self.db.scalar(statement)

    def list(self) -> list[Mission]:
        statement = select(Mission).options(selectinload(Mission.lines)).order_by(Mission.id)
        return list(self.db.scalars(statement).all())

    def update_priority(self, mission: Mission, priority: int) -> Mission:
        mission.priority = priority
        self.db.flush()
        self.db.refresh(mission)
        return mission

    def assign(self, mission: Mission, executor_id: int) -> Mission:
        mission.assigned_executor_id = executor_id
        mission.state = MissionState.ASSIGNED
        self.db.flush()
        self.db.refresh(mission)
        return mission

    def start(self, mission: Mission) -> Mission:
        mission.state = MissionState.IN_PROGRESS
        mission.started_at = datetime.now(tz=timezone.utc)
        self.db.flush()
        self.db.refresh(mission)
        return mission

    def complete(self, mission: Mission) -> Mission:
        mission.state = MissionState.COMPLETED
        mission.completed_at = datetime.now(tz=timezone.utc)
        self.db.flush()
        self.db.refresh(mission)
        return mission

    def cancel(self, mission: Mission, reason: str) -> Mission:
        mission.state = MissionState.CANCELLED
        mission.cancel_reason = reason
        self.db.flush()
        self.db.refresh(mission)
        return mission

    def get_line(self, mission_line_id: int) -> MissionLine | None:
        return self.db.get(MissionLine, mission_line_id)

    def increment_line_done(self, mission_line: MissionLine, qty_delta: Decimal) -> MissionLine:
        mission_line.qty_done = Decimal(str(mission_line.qty_done)) + Decimal(str(qty_delta))
        self.db.flush()
        self.db.refresh(mission_line)
        return mission_line

    def list_movements_for_mission(self, mission_id: int) -> list[InventoryMovement]:
        statement = (
            select(InventoryMovement)
            .join(MissionLine, InventoryMovement.mission_line_id == MissionLine.id)
            .where(MissionLine.mission_id == mission_id)
            .order_by(InventoryMovement.id)
        )
        return list(self.db.scalars(statement).all())
